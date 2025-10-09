# FortiForge Usage Guide

**Developer:** Sud0-x | **License:** Apache 2.0 | **Templates:** 3,649+

## Prerequisites

- **Python 3.9+** (required)
- **Docker** (optional, for sandbox testing)
- **2GB RAM minimum** for full template database
- **Linux/Unix environment** (tested on Ubuntu, Debian, RHEL, CentOS)


## Installation

### Quick Install (Recommended)
```bash
# Clone from GitHub
git clone https://github.com/Sud0x-org/fortiforge.git
cd fortiforge

# Create virtual environment and install
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e . -r requirements.txt
```

### Development Install
```bash
# For contributors and advanced users
git clone https://github.com/Sud0x-org/fortiforge.git
cd fortiforge
python3 -m venv .venv
source .venv/bin/activate
pip install -e . -r requirements.txt -r requirements-enterprise.txt
```

Initialize local state:
- `fortiforge audit init-keys` (generate RSA keys for signing)
- `mkdir -p ~/.fortiforge/inventory && cp inventory/examples/sandbox.yaml ~/.fortiforge/inventory/`

Plan from natural language:
- `fortiforge plan "Harden nginx servers in prod cluster, add firewall rules to block SQLi patterns, and enable fail2ban"`

View plan details:
- `fortiforge plan list`
- `fortiforge plan show <PLAN_ID>`

Simulate a plan:
- `fortiforge simulate <PLAN_ID>`

Apply to sandbox (requires consent and authorization in inventory):
- `fortiforge apply <PLAN_ID> --consent="I_AUTHORIZE_CHANGES_ON_THIS_INVENTORY" --sandbox`

Rollback:
- `fortiforge rollback <PLAN_ID> --confirm`

Rules DB search:
- `fortiforge rules search --q "nginx tls"`

Import custom rule pack:
- `fortiforge rules import ./my_rules_pack`

Inventory commands:
- `fortiforge inventory list`
- `fortiforge inventory add --file ./inventory/examples/sandbox.yaml`

Run API/UI server (demo):
- `fortiforge serve --host 127.0.0.1 --port 8080`

## Advanced Examples

### Infrastructure Hardening
```bash
# OS hardening with CIS benchmarks
fortiforge plan "Apply CIS Level 2 benchmarks to Ubuntu 22.04 web servers"

# Multi-service hardening
fortiforge plan "Harden SSH, disable root login, configure fail2ban, and apply iptables rules"

# Cloud security hardening
fortiforge plan "Secure AWS S3 buckets with encryption and access logging"
```

### Compliance Automation
```bash
# PCI-DSS compliance
fortiforge plan "Implement PCI-DSS requirements for payment processing systems"

# GDPR compliance
fortiforge plan "Configure GDPR-compliant logging and data protection controls"

# NIST framework
fortiforge plan "Apply NIST 800-53 security controls to government infrastructure"
```

### Network Security
```bash
# Firewall configuration
fortiforge plan "Configure iptables to block SQLi and XSS attack patterns"

# IDS deployment
fortiforge plan "Deploy Suricata IDS with custom rules for web application protection"

# VPN hardening
fortiforge plan "Harden OpenVPN configuration with strong encryption and authentication"
```

## Safety & Security

### Built-in Safeguards
- **✅ Defensive-Only**: Refuses ambiguous or potentially offensive operations
- **✅ Explicit Consent**: Requires `I_AUTHORIZE_CHANGES_ON_THIS_INVENTORY` phrase
- **✅ Target Authorization**: Inventory-based host approval with `authorized: true`
- **✅ Simulation-First**: All operations default to safe dry-run mode
- **✅ Audit Trail**: Cryptographically signed entries with RSA verification

### Production Deployment
- **Sandbox Mode**: Default restriction to container-based testing
- **Non-Sandbox**: Set `FORTIFORGE_ALLOW_NON_SANDBOX=1` for production
- **RBAC**: Admin/Operator/Auditor roles with JWT authentication
- **Rate Limiting**: Configurable concurrency and operation limits
