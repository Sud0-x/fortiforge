# FortiForge Production Deployment Guide

**Developer:** Sud0-x

## Overview

FortiForge is a production-ready defensive security automation & orchestration platform that converts natural language instructions into safe, auditable security configurations.

## ✅ Successfully Demonstrated Features

### Core Natural Language Processing
- ✅ **Intent Parser**: Deterministic rule-based parser with explainable evidence mapping
- ✅ **Action Planner**: Converts natural language to ordered security tasks with dependency resolution
- ✅ **Template Engine**: 3,649+ enterprise security templates across multiple categories
- ✅ **Simulation Engine**: Dry-run execution with diff preview (no system changes)

### Security & Compliance
- ✅ **Defensive-Only Design**: Refuses malicious or ambiguous patterns
- ✅ **Explicit Consent Gates**: Requires `I_AUTHORIZE_CHANGES_ON_THIS_INVENTORY`
- ✅ **Target Authorization**: Inventory-based host approval with `authorized: true` flag
- ✅ **Cryptographic Auditing**: RSA-signed audit entries with verification
- ✅ **RBAC Implementation**: Admin/Operator/Auditor roles with JWT authentication

### Template Database Coverage
- **Firewall Rules**: iptables, nftables, pf, AWS Security Groups, Azure NSG
- **OS Hardening**: Debian, Ubuntu, RHEL, CentOS system configurations
- **Service Hardening**: nginx, Apache, PostgreSQL, MySQL, SSH configurations
- **IDS Signatures**: Suricata, Zeek, OSSEC detection rules
- **Compliance**: CIS Benchmarks snippets and security baselines

## Production Architecture

```
Natural Language Input
         ↓
    Intent Parser (deterministic)
         ↓
    Action Planner (dependency resolution)
         ↓
    Template Engine (curated rules DB)
         ↓
    Simulator (dry-run with diffs)
         ↓
    [Consent Gate + Authorization Check]
         ↓
    Executor (sandbox/SSH/cloud)
         ↓
    Audit Logger (RSA-signed entries)
```

## Installation & Setup

### Requirements
- Python 3.9+
- Docker (optional, for sandbox)
- 2GB RAM minimum
- Linux/Unix environment

### Quick Install
```bash
# Clone and install
git clone <repository>
cd fortiforge
python3 -m venv .venv
. .venv/bin/activate
pip install -e . -r requirements.txt

# Initialize
fortiforge audit init-keys
mkdir -p ~/.fortiforge/inventory
cp inventory/examples/sandbox.yaml ~/.fortiforge/inventory/
```

### Production Deployment
```bash
# Build production image
docker build -t fortiforge:prod .

# Or create standalone binary
pip install pyinstaller
bash scripts/build_bundle.sh
```

## Usage Examples

### CLI Workflow
```bash
# Create security plan from natural language
fortiforge plan "Harden nginx servers, block SQLi attacks, enable fail2ban"

# Review plan
fortiforge plan list
fortiforge plan show <PLAN_ID>

# Simulate (dry-run, no system changes)
fortiforge simulate <PLAN_ID> --report simulation.json

# Apply to authorized targets (requires consent)
fortiforge apply <PLAN_ID> --consent="I_AUTHORIZE_CHANGES_ON_THIS_INVENTORY"
```

### API Workflow
```bash
# Start API server
fortiforge serve --host 127.0.0.1 --port 8080

# Bootstrap admin user
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"secure123","role":"admin"}' \
  http://localhost:8080/api/auth/bootstrap

# Authenticate
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"secure123"}' \
  http://localhost:8080/api/auth/login

# Apply with JWT token
curl -X POST -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"consent":"I_AUTHORIZE_CHANGES_ON_THIS_INVENTORY"}' \
  http://localhost:8080/api/plans/<PLAN_ID>/apply
```

## Security Controls

### Built-in Safeguards
1. **Simulation-First**: All operations default to dry-run mode
2. **Consent Required**: Explicit consent phrase required for applies
3. **Target Authorization**: Hosts must be explicitly authorized in inventory
4. **Audit Trail**: All actions cryptographically signed and verifiable
5. **Role-Based Access**: Admin/Operator/Auditor permissions
6. **Rate Limiting**: Configurable concurrency and rate controls

### Non-Sandbox Deployment
By default, FortiForge restricts applies to sandbox mode. For production:

```bash
export FORTIFORGE_ALLOW_NON_SANDBOX=1
# Ensure inventory has authorized: true for target hosts
```

## Monitoring & Observability

### Audit Verification
```bash
fortiforge audit verify-audit <AUDIT_ID>
```

### Logs
- API logs: `~/.fortiforge/server.log`
- Audit entries: `~/.fortiforge/audits/*.json`
- Plans: `~/.fortiforge/plans/*.json`

## Integration Examples

### CI/CD Integration
```yaml
- name: Security Hardening
  run: |
    fortiforge plan "Apply CIS benchmarks to web servers"
    fortiforge simulate $PLAN_ID --report security-changes.json
    # Review changes before applying
```

### Terraform Integration
```hcl
resource "null_resource" "security_hardening" {
  provisioner "local-exec" {
    command = "fortiforge apply ${var.plan_id} --consent='I_AUTHORIZE_CHANGES_ON_THIS_INVENTORY'"
  }
}
```

## Compliance & Reporting

### Available Reports
- Security posture changes
- Configuration drift detection  
- Compliance gap analysis
- Audit trail verification

### Regulatory Support
- CIS Benchmarks alignment
- SOC 2 audit trails
- PCI DSS configuration templates
- NIST framework mappings

## Troubleshooting

### Common Issues
1. **Authentication failures**: Check JWT token expiry and user roles
2. **Unauthorized targets**: Ensure `authorized: true` in inventory
3. **Simulation errors**: Verify template compatibility with target OS
4. **API connectivity**: Check firewall rules for port 8080

### Debug Mode
```bash
FORTIFORGE_DEBUG=1 fortiforge plan "..."
```

## Support & Contributing

- **Security Issues**: Report privately to maintainers
- **Feature Requests**: Use GitHub issues
- **Documentation**: See `/docs` directory
- **Testing**: Run `pytest` for full test suite

## License

Apache 2.0 - See LICENSE file

---

**Production Status**: ✅ Ready for production deployment with proper security controls and monitoring.