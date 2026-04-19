# Hooks

This directory contains hook scripts and documentation for Claude Code session automation.

**Official Claude Code documentation**: Hooks are configured in `settings.json` under
the `hooks` key. This is an official, documented Claude Code feature.

---

## What hooks do

Hooks are shell commands (or HTTP endpoints, or prompts) that Claude Code executes
automatically in response to specific events during a session. They run outside of
Claude's context — they are standard shell scripts executed by the Claude Code process.

**Key properties:**
- Hooks run synchronously for blocking events (`PreToolUse`) — they can delay or block
  the tool call
- The hook's exit code controls behavior:
  - `exit 0` — allow the action to proceed
  - `exit 2` — block the action (only for `PreToolUse` blocking hooks)
  - Any other exit code — hook failure, logged but action proceeds
- Hooks can output JSON to communicate structured decisions back to Claude Code
- Hooks run with the same environment as the Claude Code process

---

## Available hooks in this catalog

### `scripts/pre-tool-safety.sh`

**Event**: `PreToolUse` on `Bash`
**Purpose**: Warns before destructive shell commands (rm -rf, DROP TABLE, etc.)
**Behavior**: Exits 2 (blocks) if a high-risk pattern is detected, with an explanation.

### `scripts/post-session-log.sh`

**Event**: `Stop`
**Purpose**: Appends a session end timestamp to a local audit log
**Behavior**: Always exits 0 (non-blocking). Writes to `.claude/session-log.txt`.

---

## How to activate hooks

Add the relevant entries to your project's `.claude/settings.json`. See
`../settings/shared-settings-example.json` for the exact format.

Hooks are **not** activated by placing scripts in this directory. Scripts here are
examples and templates. You must configure them in `settings.json` explicitly.

---

## Hook development guidelines

1. **Keep hooks fast.** Hooks that take more than a few seconds degrade the developer
   experience significantly. Pre-tool hooks especially should complete in <500ms.
2. **Keep hooks non-blocking by default.** Only block (`exit 2`) when there is a clear
   safety concern. Blocking hooks that are too aggressive become noise and get disabled.
3. **Never put credentials in hook scripts.** Use environment variables.
4. **Test hooks independently.** Run the script manually with representative inputs
   before configuring it in settings.json.
5. **Log to stderr, not stdout.** Claude Code may process stdout for structured decisions.
   Diagnostic messages go to stderr.
6. **Handle the case where input is missing.** Hook scripts receive JSON on stdin;
   always handle the case where stdin is empty or malformed.

---

## Hook input format

Claude Code passes a JSON object on stdin to hook scripts. The structure varies by event.

For `PreToolUse` on `Bash`:
```json
{
  "tool_name": "Bash",
  "tool_input": {
    "command": "rm -rf /tmp/output"
  }
}
```

For `Stop`:
```json
{
  "stop_reason": "end_turn"
}
```

Full input schemas are documented in the official Claude Code documentation.
