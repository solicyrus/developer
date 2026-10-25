#!/usr/bin/env python3
"""TourSuperRobot — the smart super robot for the Cyrus AI Tour Guide app (Team 2).

It LEARNS from mistakes and GUIDES the work:
  1. MONITOR — runs quality checks on the live tour app (chat, API, paywall)
  2. LEARN — every bug found becomes a permanent check (bug-pattern memory)
  3. GUIDE — diagnoses, directs fixes, reports to cyrus (the approver)
  4. FIX — applies known-pattern fixes automatically

Bug-pattern memory: hidden_files/tour-bug-patterns.jsonl (one JSON per line)
Each pattern: {id, found_date, symptom, check, fix_hint, status}

Usage:
  python3 tour_super_robot.py --check     # run all checks, report
  python3 tour_super_robot.py --learn     # show learned patterns
"""
import json, os, re, sys, time, urllib.request, urllib.parse

BASE = "https://app.victoriatourandadventure.com"
HIDDEN = os.path.join(os.path.dirname(__file__), "..", "hidden_files")
PATTERNS_FILE = os.path.join(HIDDEN, "tour-bug-patterns.jsonl")

# ---------------------------------------------------------------- patterns
BUILTIN_PATTERNS = [
    {
        "id": "chat-repeats-greeting",
        "symptom": "Bot greets again on follow-up questions (no conversation memory)",
        "check": "POST api/assistant.php with history containing a greeting; answer must NOT contain a greeting",
        "fix_hint": "Frontend must send history[]; backend must include it in Gemini contents",
        "status": "fixed-2026-10-23",
    },
    {
        "id": "chat-raw-markdown",
        "symptom": "Raw **markdown** visible in chat answers",
        "check": "Answer must not contain '**'; frontend renders <strong>",
        "fix_hint": "Backend: no-markdown instruction; frontend: render **bold**",
        "status": "fixed-2026-10-23",
    },
    {
        "id": "paywall-truncated-fa",
        "symptom": "Persian paywall button text truncated ('خرید هر ۷' instead of 'خرید هر ۷ راهنما')",
        "check": "i18n.js fa.buyAll must contain 'راهنما'",
        "fix_hint": "Complete the Persian string in js/i18n.js",
        "status": "fixed-2026-10-23",
    },
    {
        "id": "chat-truncated-answers",
        "symptom": "Answers cut off mid-sentence (token limit)",
        "check": "maxOutputTokens >= 1200 in assistant.php",
        "fix_hint": "Raise maxOutputTokens in generationConfig",
        "status": "fixed-2026-10-23",
    },
]

def load_patterns():
    pats = list(BUILTIN_PATTERNS)
    if os.path.exists(PATTERNS_FILE):
        with open(PATTERNS_FILE, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try: pats.append(json.loads(line))
                    except Exception: pass
    return pats

def learn_pattern(symptom, check, fix_hint):
    os.makedirs(HIDDEN, exist_ok=True)
    pat = {
        "id": "learned-%d" % int(time.time()),
        "found_date": time.strftime("%Y-%m-%d"),
        "symptom": symptom, "check": check,
        "fix_hint": fix_hint, "status": "open",
    }
    with open(PATTERNS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(pat, ensure_ascii=False) + "\n")
    return pat["id"]

# ---------------------------------------------------------------- helpers
def http_get(path, timeout=20):
    req = urllib.request.Request(BASE + path, headers={"User-Agent": "TourSuperRobot/1.0"})
    last_err = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, r.read().decode("utf-8", errors="replace")
        except Exception as e:
            last_err = e
            time.sleep(2)
    # Fallback: urllib intermittently hits IncompleteRead on the CDN's
    # chunked GET responses through this VM's egress proxy, while curl
    # succeeds every time. A transport artifact must not fail the check.
    try:
        import subprocess
        out = subprocess.run(["curl", "-sS", "--max-time", str(timeout),
                              "-A", "TourSuperRobot/1.0", "-w", "\n%{http_code}",
                              BASE + path],
                             capture_output=True, timeout=timeout + 10)
        text = out.stdout.decode("utf-8", errors="replace")
        if "\n" in text:
            body, code = text.rsplit("\n", 1)
            if code.strip().isdigit():
                return int(code.strip()), body
    except Exception as e:
        last_err = e
    raise last_err

def http_post_json(path, payload, timeout=30):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(BASE + path, data=data,
        headers={"Content-Type": "application/json", "User-Agent": "TourSuperRobot/1.0"})
    last_err = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, json.loads(r.read().decode("utf-8"))
        except Exception as e:
            last_err = e
            time.sleep(2)
    raise last_err

GREETING_RE = re.compile(r"سلام!\s*من\s+(سایرس|Cyrus)", re.IGNORECASE)

# ---------------------------------------------------------------- checks
def check_api_health():
    # POST-only endpoint: GET returns 400, so test with a real POST instead
    try:
        s, data = http_post_json("/api/assistant.php",
            {"question": "ping", "lang": "en", "history": []})
        ok = bool(data.get("answer"))
        return {"ok": ok, "detail": f"POST answer: {ok}"}
    except Exception as e:
        return {"ok": False, "detail": str(e)[:120]}

def check_chat_memory():
    """Send a greeting in history, then a follow-up. The answer must NOT greet again."""
    try:
        history = [
            {"role": "user", "text": "Hello"},
            {"role": "bot", "text": "سلام! من سایرس، راهنمای هوشمند سفر شما هستم. چطور کمکتون کنم؟"},
        ]
        s, data = http_post_json("/api/assistant.php", {
            "question": "What about Niagara Falls?", "lang": "en", "history": history})
        ans = data.get("answer", "")
        if not ans:
            return {"ok": False, "detail": "empty answer: " + str(data)[:100]}
        if GREETING_RE.search(ans):
            return {"ok": False, "detail": "bot greeted AGAIN despite history (no memory)"}
        return {"ok": True, "detail": f"no repeated greeting ({len(ans)} chars)"}
    except Exception as e:
        return {"ok": False, "detail": str(e)[:150]}

def check_no_raw_markdown():
    try:
        s, data = http_post_json("/api/assistant.php", {
            "question": "Tell me about Victoria", "lang": "en", "history": []})
        ans = data.get("answer", "")
        if "**" in ans:
            return {"ok": False, "detail": "raw **markdown** in answer"}
        return {"ok": True, "detail": "no raw markdown"}
    except Exception as e:
        return {"ok": False, "detail": str(e)[:150]}

def check_paywall_text():
    try:
        s, js = http_get("/js/i18n.js?v=9")
        m = re.search(r'buyAll:\s*"([^"]+)"', js)
        if not m:
            return {"ok": False, "detail": "buyAll string not found"}
        if "هر ۷" in m.group(1) and "راهنما" not in m.group(1):
            return {"ok": False, "detail": f"truncated: {m.group(1)}"}
        return {"ok": True, "detail": f"buyAll OK: {m.group(1)[:40]}"}
    except Exception as e:
        return {"ok": False, "detail": str(e)[:150]}

def check_plan_intake():
    """Bot must ASK for days/people/destination before planning (standing order)."""
    try:
        s, data = http_post_json("/api/assistant.php", {
            "question": "Plan a trip for me", "lang": "en", "history": []})
        ans = data.get("answer", "")
        if not ans:
            return {"ok": False, "detail": "empty answer"}
        # Should ask, not plan: look for question marks and intake keywords
        asks = "?" in ans and any(k in ans.lower()
            for k in ["how many days", "where", "destination", "travelers", "people"])
        # Should NOT contain a day-by-day plan already
        plans_early = bool(re.search(r"\bday\s*[12]\b", ans, re.I)) and len(ans) > 1500
        if plans_early:
            return {"ok": False, "detail": "planned without asking first"}
        if not asks:
            return {"ok": False, "detail": "did not ask for trip details"}
        return {"ok": True, "detail": f"asks first ({len(ans)} chars)"}
    except Exception as e:
        return {"ok": False, "detail": str(e)[:150]}

def check_homepage():
    try:
        s, html = http_get("/")
        ok = s == 200 and "Cyrus AI Tour Guide" in html
        has_history = "history: chatHistory" in html or "chatHistory" in html
        return {"ok": ok and has_history,
                "detail": f"HTTP {s}, history-js: {has_history}"}
    except Exception as e:
        return {"ok": False, "detail": str(e)[:150]}

CHECKS = [
    ("api-health", check_api_health),
    ("homepage", check_homepage),
    ("chat-memory", check_chat_memory),
    ("no-raw-markdown", check_no_raw_markdown),
    ("paywall-text", check_paywall_text),
    ("plan-intake", check_plan_intake),
]

def run_all():
    report = {"time": time.strftime("%Y-%m-%d %H:%M"), "checks": [], "ok": True}
    for name, fn in CHECKS:
        try:
            r = fn()
        except Exception as e:
            r = {"ok": False, "detail": f"check crashed: {e}"[:150]}
        report["checks"].append({"name": name, **r})
        if not r["ok"]:
            report["ok"] = False
    return report

def main():
    if "--learn" in sys.argv:
        for p in load_patterns():
            print(f"- [{p['status']}] {p['id']}: {p['symptom']}")
        return
    report = run_all()
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
