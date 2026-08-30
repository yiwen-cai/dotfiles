# Weixin Cron Staggering Notes

## Session takeaway

When multiple Hermes cron jobs deliver to the same Weixin home channel, schedule them at least 20-30 minutes apart if the payload is long or split into multiple chunks. In this session, the daily AIHOT briefing moved from `09:00` to `09:30`, the Saturday reminder moved from `09:00` to `09:50`, and the medication reminder moved from `23:00` to `23:20` to reduce rate-limit collisions.

## Why this matters

Weixin delivery can fail even when the cron job itself reports `last_status=ok`. The scheduler may first attempt the live adapter, then fall back to standalone delivery, which can still hit the same rate limit. Spacing jobs reduces the chance that several messages share the same gateway cooldown window.
