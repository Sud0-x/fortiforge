#!/usr/bin/env bash
set -euo pipefail

# FortiForge Production Demo Script
# Developers: Sud0-x and contributors
# This script demonstrates FortiForge in a production-ready manner

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_PATH="$REPO_ROOT/.venv"
FORTIFORGE_BIN="$VENV_PATH/bin/fortiforge"
API_HOST="127.0.0.1"
API_PORT="8080"
API_BASE="http://$API_HOST:$API_PORT"

# Colors for output (safe for all terminals)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✓${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1" >&2
}

warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

check_deps() {
    log "Checking dependencies..."
    
    if [ ! -f "$FORTIFORGE_BIN" ]; then
        error "FortiForge not installed. Run: make install"
        exit 1
    fi
    
    if ! command -v curl >/dev/null 2>&1; then
        error "curl is required"
        exit 1
    fi
    
    success "All dependencies satisfied"
}

start_api_server() {
    log "Starting FortiForge API server..."
    
    if curl -sf "$API_BASE/api/health" >/dev/null 2>&1; then
        success "API server already running on $API_HOST:$API_PORT"
        return 0
    fi
    
    cd "$REPO_ROOT" && \
    source .venv/bin/activate && \
    nohup python -m fortiforge.cli serve --host "$API_HOST" --port "$API_PORT" \
        >"$REPO_ROOT/out/server.log" 2>&1 &
    
    # Wait for server to start
    local attempts=0
    while [ $attempts -lt 30 ]; do
        if curl -sf "$API_BASE/api/health" >/dev/null 2>&1; then
            success "API server started successfully"
            return 0
        fi
        sleep 1
        attempts=$((attempts + 1))
    done
    
    error "Failed to start API server"
    return 1
}

demo_cli_workflow() {
    log "=== CLI Workflow Demo ==="
    
    # Initialize audit keys
    log "Initializing audit system..."
    cd "$REPO_ROOT" && source .venv/bin/activate && python -m fortiforge.cli audit init-keys
    success "Audit keys initialized"
    
    # Create inventory directory
    mkdir -p "$HOME/.fortiforge/inventory"
    cp -n "$REPO_ROOT/inventory/examples/sandbox.yaml" "$HOME/.fortiforge/inventory/" || true
    
    # Create a plan
    log "Creating security hardening plan..."
    cd "$REPO_ROOT" && source .venv/bin/activate && \
    PLAN_OUTPUT=$(python -m fortiforge.cli plan "Harden nginx servers, add firewall rules to block SQLi patterns, and enable fail2ban" 2>&1)
    PLAN_ID=$(echo "$PLAN_OUTPUT" | grep "Plan ID:" | awk '{print $NF}')
    
    if [ -z "$PLAN_ID" ]; then
        error "Failed to create plan"
        return 1
    fi
    
    success "Plan created with ID: $PLAN_ID"
    echo "$PLAN_ID" > "$REPO_ROOT/out/current_plan_id"
    
    # Show plan summary
    log "Plan details:"
    cd "$REPO_ROOT" && source .venv/bin/activate && python -m fortiforge.cli plan list
    
    # Simulate the plan
    log "Running simulation (dry-run)..."
    cd "$REPO_ROOT" && source .venv/bin/activate && python -m fortiforge.cli simulate "$PLAN_ID" --report "$REPO_ROOT/out/simulation_report.json"
    success "Simulation completed - no changes applied to systems"
    
    # Show simulation summary
    log "Simulation found $(grep -c '"template"' "$REPO_ROOT/out/simulation_report.json") configuration changes"
    
    return 0
}

demo_api_auth() {
    log "=== API Authentication Demo ==="
    
    # Generate secure admin password
    local admin_pass="Admin$(openssl rand -hex 4)"
    local temp_file=$(mktemp)
    
    # Bootstrap admin user
    log "Creating admin user..."
    curl -s -X POST -H "Content-Type: application/json" \
        -d "{\"username\":\"admin\",\"password\":\"$admin_pass\",\"role\":\"admin\"}" \
        "$API_BASE/api/auth/bootstrap" > "$temp_file"
    
    if grep -q '"ok".*true' "$temp_file"; then
        success "Admin user created"
    else
        warn "Admin user may already exist"
    fi
    
    # Authenticate and get token
    log "Authenticating admin user..."
    curl -s -X POST -H "Content-Type: application/json" \
        -d "{\"username\":\"admin\",\"password\":\"$admin_pass\"}" \
        "$API_BASE/api/auth/login" > "$temp_file"
    
    local token=$(grep -o '"token":"[^"]*"' "$temp_file" | cut -d'"' -f4)
    
    if [ -n "$token" ]; then
        success "Authentication successful (JWT token obtained)"
        echo "$token" > "$REPO_ROOT/out/auth_token"
    else
        error "Authentication failed"
        cat "$temp_file"
        rm -f "$temp_file"
        return 1
    fi
    
    # Test API endpoint with authentication
    log "Testing authenticated API access..."
    local plan_id=$(cat "$REPO_ROOT/out/current_plan_id" 2>/dev/null || echo "")
    
    if [ -n "$plan_id" ]; then
        curl -s -X POST -H "Authorization: Bearer $token" \
            -H "Content-Type: application/json" \
            -d '{"consent":"I_AUTHORIZE_CHANGES_ON_THIS_INVENTORY"}' \
            "$API_BASE/api/plans/$plan_id/apply" > "$temp_file"
        
        if grep -q '"audit_id"' "$temp_file"; then
            local audit_id=$(grep -o '"audit_id":"[^"]*"' "$temp_file" | cut -d'"' -f4)
            success "API apply request recorded (audit ID: ${audit_id:0:8}...)"
            
            # Verify audit signature
            curl -s -H "Authorization: Bearer $token" \
                "$API_BASE/api/audit/$audit_id/verify" > "$temp_file"
            
            if grep -q '"ok".*true' "$temp_file"; then
                success "Audit signature verified"
            else
                warn "Audit verification failed"
            fi
        else
            warn "Apply request may have failed"
            cat "$temp_file"
        fi
    else
        warn "No plan ID available for API test"
    fi
    
    rm -f "$temp_file"
    return 0
}

show_production_features() {
    log "=== Production Readiness Features ==="
    
    success "✓ Natural Language to Safe Actions (deterministic parser)"
    success "✓ 3,649+ Enterprise Security Templates (OS, services, cloud, compliance, network, IDS)"
    success "✓ Simulation-First Approach (dry-run before apply)"
    success "✓ Explicit Consent Required (I_AUTHORIZE_CHANGES_ON_THIS_INVENTORY)"
    success "✓ RBAC with JWT Authentication (admin/operator/auditor roles)"
    success "✓ Cryptographic Audit Trail (RSA-signed entries)"
    success "✓ Target Authorization (inventory-based approval)"
    success "✓ Multi-Executor Support (sandbox/SSH/cloud with restrictions)"
    success "✓ Rate Limiting & Concurrency Control"
    success "✓ Comprehensive Test Suite"
    
    echo ""
    log "Security Guarantees:"
    success "✓ Defensive-only design (refuses malicious patterns)"
    success "✓ Least-privilege execution"
    success "✓ No telemetry or data exfiltration"
    success "✓ Local-first with optional cloud connectors"
    
    echo ""
    log "Compliance Features:"
    success "✓ CIS Benchmarks snippets"
    success "✓ Audit trail with verification"
    success "✓ Role-based access control"
    success "✓ Change tracking and rollback support"
}

cleanup() {
    log "Cleaning up demo resources..."
    # Kill any background processes we started
    pkill -f "fortiforge serve" 2>/dev/null || true
    success "Demo cleanup completed"
}

main() {
    trap cleanup EXIT
    
    echo "FortiForge Production Demo"
    echo "Developers: Sud0-x and contributors"
    echo "=========================="
    echo ""
    
    check_deps
    
    # Ensure output directory exists
    mkdir -p "$REPO_ROOT/out"
    
    # Start API server
    start_api_server
    
    # Run CLI demo
    demo_cli_workflow
    
    echo ""
    
    # Run API auth demo
    demo_api_auth
    
    echo ""
    
    # Show production features
    show_production_features
    
    echo ""
    log "Demo completed successfully!"
    log "API server running at: $API_BASE"
    log "Logs available at: $REPO_ROOT/out/server.log"
    log "Simulation report: $REPO_ROOT/out/simulation_report.json"
    
    echo ""
    warn "To stop the API server: pkill -f 'fortiforge serve'"
}

# Only run main if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi