# Super Robot Team — Shared Learning Memory

All customer-facing bots are ONE TEAM. They learn together and share what they learn.
Last updated: 2026-10-23

## Team members
1. **App Chat Bot** (api/assistant.php) — talks to app users
2. **Website Chat Bot** (api/chat-api-premium.php) — talks to website visitors
3. **TourSuperRobot** (monitor) — checks both daily, learns bug patterns, guides fixes

## Shared rules (learned together)
- THINK LIKE A SUPER ROBOT: silently reason step by step before answering
- CONVERSATION MEMORY: never greet twice, use history for follow-ups
- ANSWER LENGTH: match the question — short question = short answer + one clarifying question
- TRIP PLANNER INTAKE: ask destination + days + people BEFORE planning
- ORGANIZED PLANS: day-by-day, each stop with time + address + one line; never invent hours/addresses
- NO MARKDOWN: plain text, frontend renders bold
- CACHE: bump ?v= after every JS deploy; .htaccess no-cache on shell files

## How they work as a team
- TourSuperRobot runs 6 quality checks daily on both bots
- Any failure → diagnosed → fixed → pattern added here → all bots benefit
- cyrus (main agent) approves and deploys fixes, verifies live
- User (Cyrus) only gets the news in Persian

## Learning log
- 2026-10-23: chat-repeats-greeting → history support (fixed)
- 2026-10-23: chat-raw-markdown → no-markdown rule + frontend render (fixed)
- 2026-10-23: paywall-truncated-fa → complete Persian strings (fixed)
- 2026-10-23: chat-truncated-answers → 1500 tokens (fixed)
- 2026-10-23: stale-cache → bump ?v= + no-cache headers (fixed)
- 2026-10-23: verbose-answers → answer-length rule (fixed)
- 2026-10-23: plan-without-intake → intake rule (fixed)
- 2026-10-23: unorganized-plans → organized-plan rule (fixed)
- 2026-10-23: dumb-answers → super-robot thinking in both bots (deployed)

## STANDING ORDERS — TOUR PLAN FORMAT (permanent, from Cyrus 2026-10-24)
These are the super robot's standing instructions for the tour app, forever.
The robot must check this format on every daily run and fix any drift:
- Plans stay SHORT: compact day-by-day summary, 3-5 key stops per day.
- Each place: one EASY explanation of about 30 words, simple words anyone can understand.
- IN THE CHAT TEXT, tidy like a table: one place per box/cell.
- Each place name: BOLD gold line, CLICKABLE → opens that place's Google Maps page
  with its photos (Google photos cannot be embedded; the link opens Google's photos).
- NO hour-by-hour schedule, NO addresses unless the user asks.
- THE SAME table is EMAILED to the customer (chat asks for their email after the plan).
- Token cap 4000 stays as the safety net so no answer ever truncates mid-sentence.
- Full spec: ~/workspace/goals/self-guided-tour-app/hidden_files/plan-format-spec-2026-10-24.md
- Enforcing check (plan-format check in tour_super_robot.py) lands AFTER the table
  build is deployed and live-verified — do not alarm on the old format before then.
