#!/bin/bash
# Helper script to set up a cron job that runs the scraper daily at 09:00 JST.
# Run with: bash setup_cron.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="$(which python3)"
LOG="$SCRIPT_DIR/tiktok_live_tracker.log"

# Cron entry: 09:00 JST = 00:00 UTC
CRON_ENTRY="0 0 * * * cd \"$SCRIPT_DIR\" && $PYTHON main.py >> \"$LOG\" 2>&1"

# Add to crontab if not already present
(crontab -l 2>/dev/null | grep -qF "main.py") && {
    echo "Cron job already exists."
    exit 0
}

(crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -
echo "Cron job added: $CRON_ENTRY"
echo ""
echo "Verify with: crontab -l"
