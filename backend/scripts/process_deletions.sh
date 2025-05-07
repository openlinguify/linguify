#!/bin/bash

# Script to process account deletions and send reminders
# This script should be scheduled to run daily via cron

# Change to the project directory
cd "$(dirname "$0")/.."

# Activate virtual environment if available
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the management command and log output
echo "===== Running account deletion process at $(date) =====" >> logs/deletion.log
python manage.py process_deleted_accounts >> logs/deletion.log 2>&1

# Exit code
exit_code=$?
if [ $exit_code -ne 0 ]; then
    echo "ERROR: Process failed with exit code $exit_code" >> logs/deletion.log
    exit $exit_code
fi

echo "Account deletion process completed successfully" >> logs/deletion.log