# Dark War Operator Contribution Rules

- Never implement blind repeated coordinate clicks.
- Every state-changing action must declare and verify a visual postcondition.
- Fail closed on purchases, premium-currency spending, PvP, credentials, and account/alliance changes.
- Keep device control behind an adapter; the core must be runnable with a fake adapter.
- Add or update unit tests for every decision or verifier change.
