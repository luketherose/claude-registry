# ZAP baseline scan (optional)

> Reference doc for `security-test-writer`. Read at runtime only when
> the user opts in to ZAP automation.

If `zap-baseline.py` is available in the env (Docker is fine: image
`owasp/zap2docker-stable`), produce `zap/zap-baseline.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
TARGET="${TOBE_FRONTEND_URL:-http://localhost:4200}"
docker run --rm -v "$(pwd)/zap:/zap/wrk" \
    -t owasp/zap2docker-stable zap-baseline.py \
    -t "${TARGET}" -r zap-baseline-report.html \
    -c rules.tsv
```

Document expected scan duration and run instructions in the report.
The supervisor will not run the scan automatically — it's an opt-in
gate for the user.

## Output layout addendum

```
zap/
├── zap-baseline.sh                     (runs zap-baseline.py against TOBE_FRONTEND_URL)
└── .zap/rules.tsv                      (rule ignore-list with justifications)
```
