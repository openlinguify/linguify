# Development settings override
from .settings import *

# TEMPORARY: Enable authentication bypass for development
BYPASS_AUTH_FOR_DEVELOPMENT = True

# This will make the Supabase authentication return a fake user
# Remove this in production!
print("⚠️  WARNING: Authentication bypass is enabled for development!")
print("⚠️  This should NEVER be used in production!")