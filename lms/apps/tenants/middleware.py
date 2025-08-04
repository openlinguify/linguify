"""
Middleware to handle multi-tenant database routing
"""

from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.db import connections
from .models import Organization, OrganizationMembership
from .db_router import set_current_database, clear_current_database
import logging

logger = logging.getLogger(__name__)


class TenantMiddleware(MiddlewareMixin):
    """
    Middleware that:
    1. Identifies the current organization from the request
    2. Sets the appropriate database for the request
    3. Ensures user has access to the organization
    """
    
    def process_request(self, request):
        """Process incoming request to determine organization context"""
        
        # Clear any previous database setting
        clear_current_database()
        
        # Skip tenant logic for static files and public URLs
        if self._is_public_url(request.path):
            return None
        
        # Try to identify organization
        organization = self._get_organization(request)
        
        if organization:
            # Check if database exists in settings
            if organization.database_name not in settings.DATABASES:
                # Dynamically add the database configuration
                self._create_database_config(organization)
            
            # Set the current database for this request
            set_current_database(organization.database_name)
            
            # Add organization to request for easy access
            request.organization = organization
            
            # Verify user has access (if authenticated)
            if request.user.is_authenticated:
                if not self._user_has_access(request.user, organization):
                    return HttpResponseForbidden("You don't have access to this organization")
                
                # Add user role to request for easy access
                request.user_role = self._get_user_role(request.user, organization)
        else:
            # No organization context - use default database
            request.organization = None
            
        return None
    
    def process_response(self, request, response):
        """Clean up after request"""
        clear_current_database()
        return response
    
    def process_exception(self, request, exception):
        """Clean up on exception"""
        clear_current_database()
        return None
    
    def _is_public_url(self, path):
        """Check if URL should bypass tenant logic"""
        public_urls = [
            '/admin/',
            '/static/',
            '/media/',
            '/login/',
            '/logout/',
            '/tenants/',
            '/api/public/',
        ]
        # Also allow root path without organization context
        if path == '/' or path == '':
            return True
        return any(path.startswith(url) for url in public_urls)
    
    def _get_organization(self, request):
        """
        Identify organization from request
        Can use subdomain, domain, URL path, or session
        """
        organization = None
        
        # Method 1: From URL path (e.g., /org/mit/)
        if '/org/' in request.path:
            import re
            match = re.match(r'^/org/([^/]+)/', request.path)
            if match:
                org_slug = match.group(1)
                try:
                    organization = Organization.objects.get(
                        slug=org_slug,
                        is_active=True
                    )
                    # Store in session for consistency
                    request.session['organization_id'] = str(organization.id)
                except Organization.DoesNotExist:
                    pass
        
        # Method 2: From subdomain (e.g., harvard.lms.linguify.com)
        if not organization:
            host = request.get_host().lower()
            if '.' in host:
                subdomain = host.split('.')[0]
                if subdomain and subdomain != 'www' and subdomain != 'localhost':
                    try:
                        organization = Organization.objects.get(
                            slug=subdomain,
                            is_active=True
                        )
                    except Organization.DoesNotExist:
                        pass
        
        # Method 3: From custom domain
        if not organization:
            try:
                organization = Organization.objects.get(
                    domain=host,
                    is_active=True
                )
            except Organization.DoesNotExist:
                pass
        
        # Method 4: From session (for development)
        if not organization and hasattr(request, 'session'):
            org_id = request.session.get('organization_id')
            if org_id:
                try:
                    organization = Organization.objects.get(
                        id=org_id,
                        is_active=True
                    )
                except Organization.DoesNotExist:
                    pass
        
        return organization
    
    def _user_has_access(self, user, organization):
        """Check if user has access to organization"""
        return OrganizationMembership.objects.filter(
            user=user,
            organization=organization
        ).exists()
    
    def _get_user_role(self, user, organization):
        """Get user's role in the organization"""
        try:
            membership = OrganizationMembership.objects.get(
                user=user,
                organization=organization
            )
            return membership.role
        except OrganizationMembership.DoesNotExist:
            return 'guest'
    
    def _create_database_config(self, organization):
        """Dynamically create database configuration for organization"""
        # Copy the default database config
        base_config = settings.DATABASES['default'].copy()
        
        # Update with organization-specific database
        base_config['NAME'] = organization.database_name
        
        # Add to DATABASES setting
        settings.DATABASES[organization.database_name] = base_config
        
        # Create connection
        connections.databases[organization.database_name] = base_config