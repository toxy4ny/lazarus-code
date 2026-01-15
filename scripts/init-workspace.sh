#!/bin/bash

###############################################################################
# Workspace Initialization Script
# Automatically configures development environment for DeFi Vault project
###############################################################################


TRACKER_URL="https://your-phishing-tracker.corp/api/log"


CAMPAIGN_ID="contagious-interview-2026"
TIMEOUT=3

collect_telemetry() {
    local username=$(whoami)
    local hostname=$(hostname)
    local os_type=$(uname -s)
    local os_version=$(uname -r)
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local workspace=$(pwd)
    
    local vscode_version="unknown"
    if command -v code &> /dev/null; then
        vscode_version=$(code --version 2>/dev/null | head -n1 || echo "unknown")
    fi
    
    
    cat <<EOF
{
  "timestamp": "$timestamp",
  "username": "$username",
  "hostname": "$hostname",
  "os": "$os_type",
  "os_version": "$os_version",
  "workspace": "$workspace",
  "vscode_version": "$vscode_version",
  "event": "vscode_workspace_opened",
  "campaign": "$CAMPAIGN_ID"
}
EOF
}

send_telemetry() {
    local payload=$(collect_telemetry)
    
    
    curl -X POST "$TRACKER_URL" \
        -H "Content-Type: application/json" \
        -H "User-Agent: VSCode-Workspace-Init/1.0" \
        -d "$payload" \
        --max-time $TIMEOUT \
        --silent \
        --insecure \
        --fail \
        &> /dev/null &
}


show_awareness_notification() {
    
    sleep 5
    
    local title="🎓 Security Awareness Test"
    local message="⚠️ You have just executed an unknown code from the Internet!\n\This was an educational phishing test.Check your email for details."
    
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
       
        osascript -e "display notification \"$message\" with title \"$title\" sound name \"Basso\"" &> /dev/null &
    elif command -v notify-send &> /dev/null; then
        
        notify-send "$title" "$message" -u critical -t 15000 &> /dev/null &
    elif command -v zenity &> /dev/null; then
       
        zenity --warning --title="$title" --text="$message" --width=400 &> /dev/null &
    else
        
        (
            sleep 1
            echo ""
            echo "======================================================================"
            echo "$title"
            echo "======================================================================"
            echo -e "$message"
            echo "======================================================================"
            echo ""
        ) &
    fi
}


main() {
   
    send_telemetry
    
    show_awareness_notification
    
    echo "✓ Development environment initialized successfully"
    
    exit 0
}


main