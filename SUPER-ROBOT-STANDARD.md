# SUPER ROBOT STANDARD (standing order 2026-10-23)

Every AI in every team thinks like a SUPER ROBOT. This is the canonical pattern.
Keep it updated to the best available. Applied team-wide.

## The pattern
Before answering, silently reason step by step:
1. What is really being asked?
2. What context do I have (history, knowledge)?
3. What is the most helpful, specific answer?
Then give ONLY the final answer — never show the reasoning.

## Where it's applied
- **Tour app bot** (api/assistant.php): THINK LIKE A SUPER ROBOT in system prompt ✅
- **Website bot** (api/chat-api-premium.php): prepended to system prompt ✅
- **Ultimate robot team** (brain/llm.py): SUPER_THINK prepended in ask() — all 12 robots ✅
- **Factory agents** (agents/llm.py): uses same pattern via system prompts
- **Super-brain core** (core/llm.py): think() with Persian JSON reasoning ✅

## Standing rules (all bots)
- Conversation memory: never repeat greetings, use history
- Match answer length to the question
- Trip plans: ask destination/days/people first, then organized day-by-day output
- Hours/addresses/prices: only from verified knowledge, never invented
- Learn from every mistake — each bug becomes a permanent check

## Update policy
- Review monthly: is there a better model or better reasoning pattern?
- User (Cyrus) approves model changes (cost implications)
- Prompt improvements: cyrus can apply directly (no cost change)

## Python super-robot rollout (2026-10-24, Cyrus's order: Python only, PHP excluded)
- Ultimate team brain/llm.py already carries SUPER_THINK (all robots that use it).
- Factory agents/llm.py now carries SUPER_THINK too (added 2026-10-24, stub-tested:
  prepended to every call, caller system kept, empty prompt still returns None).
  Every factory agent that calls the shared ask() backend now thinks like the super robot.
- Rule-based agents that never call an LLM (e.g. the English-app guardian) keep their
  fixed rules on purpose: a brain would make their checks less exact, not better.
- Super Brain core/llm.py IS the super brain itself; it is not given the instruction
  because its JSON decision format must stay exact.
- PHP bots (tour app assistant.php, website chat-api-premium.php) are OUT of this
  rollout per his order: "Forget about the PHP, PHP is different."
