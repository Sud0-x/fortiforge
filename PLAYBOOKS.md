# Playbooks Guide

Playbooks in FortiForge are YAML files describing idempotent tasks, with simulate/apply/rollback metadata.

Layout:
- Name and description
- Targets (labels, groups, or explicit hosts)
- Tasks: each task has idempotency checks, simulate, apply, rollback

Sample playbooks are under playbooks/samples.

Creating a playbook:
- `fortiforge playbook create --name harden-nginx --targets label:web --from-templates nginx_hardening,tls_hsts`
- Edit generated YAML, then test with simulation.

Simulation:
- Runs tasks in dry-run, producing a diff of expected changes.
- No changes are applied.

Auditing:
- Playbook executions are signed and stored in ~/.fortiforge/audits.
