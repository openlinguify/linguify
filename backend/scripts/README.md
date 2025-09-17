# Backend Scripts

This directory contains utility scripts for backend operations.

## test_db_connection.py

Tests database connectivity without exposing credentials.

### Usage

```bash
# Set DATABASE_URL environment variable (don't commit this!)
export DATABASE_URL='postgresql://user:password@host/database'

# Run the test
python scripts/test_db_connection.py
```

### Security Note

Never commit DATABASE_URL or any credentials to the repository. Always use environment variables or secret management services.

## Other Scripts

Add documentation for other utility scripts here.