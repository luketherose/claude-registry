---
description: Terse, actionable code review in one-line format. No hedging, no code repetition: just problem and fix per critical line.
---

Review in caveman format. One line per issue.

## Format
`L<line>: <problem>. <fix>.`
Multi-file: `<file>:L<line>: <problem>. <fix>.`

## Severity
- 🔴 **bug** — broken behaviour, incident risk
- 🟡 **risk** — works but fragile (race conditions, unchecked nulls, silent errors)
- 🔵 **nit** — style or naming
- ❓ **q** — genuine question, not directive

## Example
`L42: 🔴 bug: user can be null after .find(). Add guard before .email.`

## Omit
- Hedging ("maybe", "you might consider")
- Throat-clearing ("great code but...")
- Code behaviour repetition
- Motivational asides

## Expand for
- Security findings (CVE level)
- Architectural disputes
- Onboarding contexts

## Scope
Output comments ready to paste into PR. Do not write fixes, do not approve, do not run linter.

---

**See also**: `/utils/caveman` for general terse communication · `/utils/caveman-commit` for commit messages

---

$ARGUMENTS
