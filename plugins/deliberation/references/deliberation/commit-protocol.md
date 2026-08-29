# Deliberation — commit-protocol abstraction

The decision committer is the final stage of Step 6. It records the
decision artefact in a manner appropriate to the calling environment.
The engine ships with a safe local default and a clean adapter
interface; `raft` and `pbft` adapters are extension points and **must
not be faked**.

## Interface

```
DecisionCommitter
├── name(): "local_transactional" | "raft" | "pbft"
├── available(env): bool                # whether this protocol is usable here
└── commit(decisionArtefactPath): CommitResult
```

`CommitResult`:

```json
{
  "committedAt": "...",
  "committerVersion": "...",
  "protocol": "local_transactional | raft | pbft",
  "transactionId": "...",          // local: file-rename txn id; raft: log index; pbft: sequence number
  "quorumWitnessed": null,         // raft / pbft: list of witnesses that ack'd
  "notes": "..."
}
```

## Implementations

### `local_transactional` (default, always available)

Purpose: the safe baseline for a single-team / single-repo deliberation.
The decision artefact is committed atomically to disk under
`.deliberation-kb/<trace-id>/05-final-decision.json`. The committer:

1. Writes `05-final-decision.json.tmp` with the rendered artefact.
2. Computes a SHA-256 of `tmp` and stores it in
   `_meta/manifest.json` under the matching artefact entry.
3. Renames `tmp` → `05-final-decision.json` (single atomic syscall on
   POSIX).
4. Updates `_meta/manifest.json.tmp` and atomically renames it.
5. Emits `CommitResult` with `protocol: local_transactional` and
   `transactionId` = the rename's inode-change timestamp.

This protocol is the default for any environment, including in
`refactoring-supervisor` Phase 4 use, because the `.deliberation-kb/`
tree is part of the working repository and is committed by the
caller's normal git workflow.

### `raft` (extension point, not implemented)

Purpose: trusted distributed environments where multiple replicas of
the engine write to a shared replicated log (e.g., a multi-region
deliberation service).

**Not implemented in the registry.** The interface exists; the
adapter is not provided. To enable:

1. Provide a `RaftDecisionCommitter` adapter that implements the
   `DecisionCommitter` interface.
2. Register it via the calling environment's adapter registry (e.g.
   environment variable `DELIBERATION_COMMITTER=raft`, or a config
   file the engine reads at start-up). Mechanism is environment-
   specific; the engine reads `policy.commitProtocol` and asks the
   environment whether the named adapter is `available()`.
3. The adapter MUST:
   - replicate the artefact to a Raft cluster (≥3 nodes for fault
     tolerance, ≥5 for two-fault tolerance);
   - return only after a quorum of replicas has applied the entry to
     its state machine;
   - record the leader's term + log index in `transactionId`;
   - list the witnessing replicas in `quorumWitnessed`.

If the calling environment does not register a Raft adapter, the
engine MUST fall back to `local_transactional` and record the gap in
`_meta/manifest.json.failureEvents`. Faking Raft is forbidden.

### `pbft` (extension point, not implemented)

Purpose: consortium / partially adversarial environments where the
deliberation outcome must be witnessed by a quorum of mutually
distrustful parties (e.g., multi-party agreement on a regulated
decision). PBFT tolerates `f` Byzantine failures with `3f+1` replicas.

**Not implemented in the registry.** Interface contract:

- The adapter MUST run a Byzantine-tolerant consensus round with
  `3f+1 >= 4` replicas before returning.
- The adapter MUST verify replica signatures.
- The adapter MUST record the sequence number, view, and signatures
  in `transactionId` and `quorumWitnessed`.

Same fallback rule: no registered adapter ⇒ `local_transactional`
fallback + `failureEvents` entry. Faking PBFT is forbidden.

## Selection

The engine picks the committer per the rules in
`strategy-selection.md` § "Commit-protocol selection". When the
selected protocol is unavailable, fall back and record the gap.

## Audit trail

The final user-facing report and `05-final-decision.json` MUST record
the actual `commitProtocol` used (after fallback), not the requested
protocol. If a fallback occurred, the user-facing report includes a
"Commit-protocol fallback" note pointing at the manifest entry.
