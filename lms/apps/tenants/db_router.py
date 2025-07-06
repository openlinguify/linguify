"""
Database router for multi-tenant architecture
Routes queries to the appropriate database based on the current organization
"""

from django.conf import settings
import threading

# Thread-local storage for current database
_thread_locals = threading.local()

def set_current_database(db_name):
    """Set the current database for this thread"""
    _thread_locals.database = db_name

def get_current_database():
    """Get the current database for this thread"""
    return getattr(_thread_locals, 'database', 'default')

def clear_current_database():
    """Clear the current database setting"""
    if hasattr(_thread_locals, 'database'):
        del _thread_locals.database


class TenantRouter:
    """
    Route database operations based on current organization context
    """
    
    # Apps that should always use the master database
    MASTER_APPS = [
        'tenants',
        'sessions',
        'contenttypes',
        'auth',  # For the master user table
    ]
    
    # Apps that should use the tenant database
    TENANT_APPS = [
        'institutions',
        'courses', 
        'students',
        'instructors',
        'assessments',
        'analytics',
        'content',
        'administration',
    ]
    
    def db_for_read(self, model, **hints):
        """Determine which database to read from"""
        # Special case: OrganizationUser authentication should always use default
        if (model._meta.app_label == 'tenants' and 
            model._meta.model_name == 'organizationuser'):
            return 'default'
        elif model._meta.app_label in self.MASTER_APPS:
            return 'default'
        elif model._meta.app_label in self.TENANT_APPS:
            return get_current_database()
        return None
    
    def db_for_write(self, model, **hints):
        """Determine which database to write to"""
        if model._meta.app_label in self.MASTER_APPS:
            return 'default'
        elif model._meta.app_label in self.TENANT_APPS:
            return get_current_database()
        return None
    
    def allow_relation(self, obj1, obj2, **hints):
        """
        Relations between objects are allowed if:
        - Both are in master apps
        - Both are in tenant apps
        - One is auth.User (special case for user relations)
        """
        db_set = {self.db_for_read(obj1), self.db_for_read(obj2)}
        if len(db_set) == 1:
            return True
        
        # Allow relations with auth.User
        if (obj1._meta.label == 'auth.User' or obj2._meta.label == 'auth.User'):
            return True
            
        return None
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Ensure that:
        - Master apps only migrate on default database  
        - Tenant apps only migrate on tenant databases
        """
        if app_label in self.MASTER_APPS:
            return db == 'default'
        elif app_label in self.TENANT_APPS:
            return db != 'default'
        return None