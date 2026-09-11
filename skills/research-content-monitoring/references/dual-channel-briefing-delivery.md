# Dual-channel briefing delivery: Weixin plus email

Use this pattern when a scheduled briefing should go to a messaging platform and an email inbox, but the email platform is not exposed as a Hermes delivery target.

## Pattern

1. Keep the cron job in `no_agent=True` mode with a deterministic script.
2. Let Hermes cron deliver the script stdout to the messaging target, including any `MEDIA:/absolute/path` attachment line.
3. Inside the script, attempt email delivery separately before printing the final messaging summary.
4. Include the exact email-send status in the messaging summary, for example:
   - `邮箱已发送至 user@example.com。`
   - `邮箱未发送：himalaya 超时...`
   - `邮箱未发送：缺少 SMTP_HOST/SMTP_USERNAME/SMTP_PASSWORD/SMTP_FROM 配置。`
5. Do not report successful email delivery unless the send command actually returned success.

## Email send order

Recommended fallback order:

1. Existing local mail CLI, usually `himalaya template send`, if configured.
2. SMTP environment variables:
   - `SMTP_HOST`
   - `SMTP_PORT`
   - `SMTP_USERNAME`
   - `SMTP_PASSWORD`
   - `SMTP_FROM`
3. Optional aliases for compatibility, such as `EMAIL_USERNAME`, `EMAIL_PASSWORD`, `MAIL_HOST`, or `GMAIL_APP_PASSWORD`.

For SMTP ports:

- Port `465`: use implicit TLS, e.g. Python `smtplib.SMTP_SSL`.
- Port `587`: use STARTTLS, e.g. Python `smtplib.SMTP(...); starttls()`.

## Scheduling pitfall

If another daily briefing already sends to Weixin at the same minute, schedule the new job several minutes later, such as `09:10` instead of `09:00`, to reduce gateway rate-limit collisions. Still verify `last_delivery_error`; `last_status=ok` only proves the script ran.

## Verification checklist

- Run `ruff format` after editing Python scripts.
- Run the script once outside cron and confirm it prints a readable summary plus `MEDIA:/absolute/path`.
- Confirm generated JSON/HTML files exist and have non-zero size.
- Check email status from the real send attempt; do not infer success from account presence alone.
- Create the cron only after script-level verification succeeds.
