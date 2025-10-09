# Security Policy

- Defensive-only: FortiForge must never be used to attack, infiltrate, or violate privacy.
- Consent required: All apply/rollback require explicit consent phrase and host authorization in inventory.
- Least privilege: Executors run with minimal privileges; sudo prompts are explicit and logged.
- Auditing: All actions are recorded as signed JSON audit entries with verification support.
- Privacy: No telemetry or data exfiltration. Plans and artifacts remain local by default.
- LLM usage: Optional and not trusted for execution. Never executes network/system changes.

Report security issues privately to maintainers.
