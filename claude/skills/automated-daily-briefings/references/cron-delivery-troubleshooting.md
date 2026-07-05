# AI Daily Briefing Cron Delivery Troubleshooting

Use this reference when an automated daily briefing pipeline generates its JSON/HTML artifacts but the user does not receive the scheduled message or attachment.

## Diagnostic sequence

1. Check the cron job record first.

```bash
hermes cron list
hermes cron status
```

Look for:

- `last_status` and `last_run_at`.
- The exact `model` and `provider` recorded on the job.
- `deliver` target. If the job was created with `deliver=origin` outside an inbound gateway event, Hermes may log that it is falling back to the home channel.

2. Check scheduler and gateway logs around the run time.

```bash
grep -R "JOB_ID\|JOB_NAME\|completed successfully\|failed:\|delivered to\|live adapter delivery\|send chunk failed\|send_document failed" ~/.hermes/logs | tail -120
```

Interpretation:

- `Job ... completed successfully` means agent execution finished.
- Generated data/artifacts may still exist even if delivery failed.
- `delivered to weixin:... via live adapter` confirms live gateway delivery at that timestamp.
- `live adapter delivery ... failed, falling back to standalone` means Hermes tried a second delivery path; inspect subsequent gateway errors.
- `Cannot connect to host ilinkai.weixin.qq.com:443 ssl:default [None]` points to Weixin gateway network connectivity, not briefing collection/rendering.
- `send_document failed ... No such file or directory` means the final response used an invalid `MEDIA:` path or a templated placeholder path.

3. Verify artifacts independently of delivery.

```bash
python3 -m json.tool data/YYYY-MM-DD.json >/tmp/briefing-json-ok
ls -lh data/YYYY-MM-DD.json output/YYYY-MM-DD.html
```

If the files exist and parse/open correctly, do not debug the collector first; debug delivery.

4. Separate model failures from delivery failures.

Examples:

- `HTTP 503 ... No available channel for model ...` before any tool calls is a model/provider availability failure.
- API call logs plus tool completion logs followed by `Turn ended` and `completed successfully` mean the model run succeeded; any missing message is a delivery issue.

5. Keep scheduled prompts self-contained and short enough that the model does not repeatedly read full JSON chunks. Prefer telling the model to read/inspect only top items or generate the text from a pre-ranked subset when JSON is large.

## Operational lessons

- For Weixin delivery, a failed live adapter can still leave `hermes cron list` showing an older `last_status` until the scheduler record updates. Use logs for the freshest truth immediately after a run.
- If the user asks "I did not receive it", check both artifact generation and gateway delivery logs before re-triggering.
- If delivery fails but artifacts exist, report the local `MEDIA:/absolute/path/to/output.html` path in the current chat as a fallback preview.
- Do not conflate collector proxy settings with Weixin gateway networking. `--proxy http://127.0.0.1:7897` can fix HF/arXiv collection while Weixin delivery to `ilinkai.weixin.qq.com:443` may still fail separately.
