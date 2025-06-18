# linguify/scripts/tools/modules/create_new_module.py
#!/usr/bin/env python
"""
Linguify Module Generator

This script automates the creation of a new module for the Linguify application,
handling both Django backend and React frontend components.

Usage:
    python create_new_module.py <module_name> <module_icon> [--description "Module description"]

Example:
    python create_new_module.py quiz Brain --description "Quiz module for language learning"
"""

import os
import sys
import re
import json
import shutil
import argparse
from pathlib import Path

# Define the root directories for backend and frontend
BACKEND_ROOT = Path("backend")
FRONTEND_ROOT = Path("frontend")

# Template paths
TEMPLATES_DIR = Path("templates")

def validate_module_name(name):
    """Validate the module name is in the correct format."""
    if not re.match(r'^[a-z][a-z0-9_]*$', name):
        print(f"Error: Module name '{name}' is invalid. It should start with a lowercase letter and contain only lowercase letters, numbers, and underscores.")
        sys.exit(1)
    return name

def validate_icon_name(name):
    """Validate the icon name is a valid Lucide icon."""
    # This is a simplified validation - ideally you'd check against the actual Lucide icon list
    if not re.match(r'^[A-Z][A-Za-z0-9]*$', name):
        print(f"Error: Icon name '{name}' is invalid. It should be in PascalCase format (e.g., Brain, BookOpen).")
        sys.exit(1)
    return name

def create_django_app(module_name, description):
    """Create the Django app structure."""
    print(f"Creating Django app: {module_name}...")
    
    # Create the app directory and structure
    app_dir = BACKEND_ROOT / 'apps' / module_name
    if app_dir.exists():
        print(f"Warning: Directory {app_dir} already exists.")
    else:
        app_dir.mkdir(parents=True, exist_ok=True)
        
        # Create basic app files
        create_file(app_dir / '__init__.py', '')
        create_file(app_dir / 'admin.py', generate_django_admin(module_name))
        create_file(app_dir / 'apps.py', generate_django_apps(module_name))
        create_file(app_dir / 'models.py', generate_django_models(module_name, description))
        create_file(app_dir / 'serializers.py', generate_django_serializers(module_name))
        create_file(app_dir / 'views.py', generate_django_views(module_name))
        create_file(app_dir / 'urls.py', generate_django_urls(module_name))
        create_file(app_dir / 'tests.py', generate_django_tests(module_name))
        
        # Create migrations directory
        migrations_dir = app_dir / 'migrations'
        migrations_dir.mkdir(exist_ok=True)
        create_file(migrations_dir / '__init__.py', '')
    
    # Update settings.py to include the new app
    update_django_settings(module_name)
    
    # Update core/urls.py to include the new app's URLs
    update_django_urls(module_name)
    
    print(f"Django app '{module_name}' created successfully.")

def create_react_module(module_name, icon_name, description):
    """Create the React frontend module structure."""
    print(f"Creating React frontend module: {module_name}...")
    
    # Create the module directory structure
    module_dir = FRONTEND_ROOT / 'src' / 'addons' / module_name
    if module_dir.exists():
        print(f"Warning: Directory {module_dir} already exists.")
    else:
        module_dir.mkdir(parents=True, exist_ok=True)
        
        # Create components, api, and types directories
        components_dir = module_dir / 'components'
        hooks_dir = module_dir / 'hooks'
        services_dir = module_dir / 'services'
        api_dir = module_dir / 'api'
        types_dir = module_dir / 'types'
        
        components_dir.mkdir(exist_ok=True)
        hooks_dir.mkdir(exist_ok=True)
        services_dir.mkdir(exist_ok=True)
        api_dir.mkdir(exist_ok=True)
        types_dir.mkdir(exist_ok=True)
        
        # Create basic module files
        create_file(module_dir / 'index.ts', generate_react_index(module_name))
        create_file(api_dir / f'{module_name}API.ts', generate_react_api(module_name))
        create_file(types_dir / 'index.ts', generate_react_types(module_name, description))
        
        # Create main view component
        create_file(components_dir / f'{capitalize(module_name)}View.tsx', 
                   generate_react_view(module_name, icon_name, description))
        create_file(components_dir / 'index.ts', generate_react_components_index(module_name))
    
    # Add the module to the dashboard menu
    update_dashboard_menu(module_name, icon_name, description)
    
    print(f"React frontend module '{module_name}' created successfully.")

def update_django_settings(module_name):
    """Update Django settings.py to include the new app."""
    settings_path = BACKEND_ROOT / 'core' / 'settings.py'
    
    if not settings_path.exists():
        print(f"Warning: Could not find {settings_path}. Please add '{module_name}' to your INSTALLED_APPS manually.")
        return
    
    settings_content = settings_path.read_text()
    
    # Look for the INSTALLED_APPS section
    installed_apps_pattern = r'INSTALLED_APPS\s*=\s*\[(.*?)\]'
    match = re.search(installed_apps_pattern, settings_content, re.DOTALL)
    
    if match:
        installed_apps = match.group(1)
        
        # Check if the app is already in INSTALLED_APPS
        app_pattern = rf"'apps\.{module_name}'"
        if re.search(app_pattern, installed_apps):
            print(f"App 'apps.{module_name}' is already in INSTALLED_APPS.")
            return
        
        # Find where to insert the new app
        project_apps_pattern = r"# Project django_apps(.*?)# Django REST framework modules"
        project_apps_match = re.search(project_apps_pattern, installed_apps, re.DOTALL)
        
        if project_apps_match:
            project_apps = project_apps_match.group(1)
            
            # Insert the new app before the comment line or at the end of project apps
            new_project_apps = project_apps.rstrip() + f"\n    'apps.{module_name}',\n    "
            
            # Replace the project apps section
            new_installed_apps = installed_apps.replace(project_apps, new_project_apps)
            new_settings_content = settings_content.replace(match.group(1), new_installed_apps)
            
            # Write the updated settings.py
            settings_path.write_text(new_settings_content)
            print(f"Added 'apps.{module_name}' to INSTALLED_APPS.")
        else:
            print("Warning: Could not find the project apps section in INSTALLED_APPS. Please add the app manually.")
    else:
        print("Warning: Could not find INSTALLED_APPS in settings.py. Please add the app manually.")

def update_django_urls(module_name):
    """Update the main urls.py to include the new app's URLs."""
    urls_path = BACKEND_ROOT / 'core' / 'urls.py'
    
    if not urls_path.exists():
        print(f"Warning: Could not find {urls_path}. Please update your URL patterns manually.")
        return
    
    urls_content = urls_path.read_text()
    
    # Check if the app's URLs are already included
    url_pattern = rf"path\('api/v1/{module_name}/', include\('{module_name}.urls', namespace='{module_name}'\)\)"
    if re.search(url_pattern, urls_content):
        print(f"URL pattern for '{module_name}' is already in urls.py.")
        return
    
    # Find the urlpatterns list
    urlpatterns_match = re.search(r'urlpatterns\s*=\s*\[(.*?)\]', urls_content, re.DOTALL)
    
    if urlpatterns_match:
        urlpatterns = urlpatterns_match.group(1)
        
        # Find the last path line
        last_path_match = re.findall(r'^\s*path\(.*?\),\s*$', urlpatterns, re.MULTILINE)
        
        if last_path_match:
            last_path = last_path_match[-1]
            
            # Add the new URL pattern after the last path
            new_url_pattern = f"    path('api/v1/{module_name}/', include('{module_name}.urls', namespace='{module_name}')),\n"
            new_urlpatterns = urlpatterns.replace(last_path, last_path + new_url_pattern)
            
            # Replace the urlpatterns in the content
            new_urls_content = urls_content.replace(urlpatterns_match.group(1), new_urlpatterns)
            
            # Write the updated urls.py
            urls_path.write_text(new_urls_content)
            print(f"Added URL pattern for '{module_name}' to urls.py.")
        else:
            print("Warning: Could not find any path entries in urlpatterns. Please update manually.")
    else:
        print("Warning: Could not find urlpatterns in urls.py. Please update manually.")

def update_dashboard_menu(module_name, icon_name, description):
    """Update the dashboard home page to include the new module."""
    dashboard_path = FRONTEND_ROOT / 'src' / 'app' / 'dashboard' / 'page.tsx'
    
    # If the specific path doesn't exist, try to find the dashboard file
    if not dashboard_path.exists():
        # Try to find the dashboard component file in the codebase
        possible_paths = [
            FRONTEND_ROOT / 'src' / 'pages' / 'dashboard' / 'index.tsx',
            FRONTEND_ROOT / 'src' / 'components' / 'Dashboard' / 'index.tsx',
            FRONTEND_ROOT / 'src' / 'views' / 'Dashboard.tsx'
        ]
        
        for path in possible_paths:
            if path.exists():
                dashboard_path = path
                break
        
        if not dashboard_path.exists():
            print("Warning: Could not find the dashboard component file. Please update the dashboard menu manually.")
            print(f"Add the following to your dashboard menu items:")
            print(f"""{{
  titleKey: "dashboard.{module_name}Card.title",
  fallbackTitle: "{capitalize(module_name)}",
  icon: {icon_name},
  href: "/{module_name}",
  color: "bg-indigo-50 text-indigo-500 dark:bg-indigo-900/20 dark:text-indigo-400"
}}""")
            return
    
    dashboard_content = dashboard_path.read_text()
    
    # Check if the module is already in the menu items
    menu_item_pattern = rf'"/{module_name}"'
    if re.search(menu_item_pattern, dashboard_content):
        print(f"Module '{module_name}' is already in the dashboard menu.")
        return
    
    # Find the menuItems array
    menu_items_pattern = r'const\s+menuItems\s*=\s*\[(.*?)\];'
    menu_items_match = re.search(menu_items_pattern, dashboard_content, re.DOTALL)
    
    if menu_items_match:
        menu_items = menu_items_match.group(1)
        
        # Insert the new menu item before the last item (usually settings)
        last_item_pattern = r',\s*{[^{}]*}\s*$'
        last_item_match = re.search(last_item_pattern, menu_items, re.DOTALL)
        
        if last_item_match:
            last_item = last_item_match.group(0)
            
            # Create the new menu item
            new_menu_item = f"""
    {{
      titleKey: "dashboard.{module_name}Card.title",
      fallbackTitle: "{capitalize(module_name)}",
      icon: {icon_name},
      href: "/{module_name}",
      color: "bg-indigo-50 text-indigo-500 dark:bg-indigo-900/20 dark:text-indigo-400"
    }},{last_item}"""
            
            # Replace the last item with the new item + last item
            new_menu_items = menu_items.replace(last_item, new_menu_item)
            
            # Replace the menu items in the content
            new_dashboard_content = dashboard_content.replace(menu_items_match.group(1), new_menu_items)
            
            # Write the updated dashboard component
            dashboard_path.write_text(new_dashboard_content)
            print(f"Added '{module_name}' to the dashboard menu.")
        else:
            print("Warning: Could not find the last menu item. Please update the dashboard menu manually.")
    else:
        print("Warning: Could not find the menuItems array. Please update the dashboard menu manually.")
        print(f"Add the following to your dashboard menu items:")
        print(f"""{{
  titleKey: "dashboard.{module_name}Card.title",
  fallbackTitle: "{capitalize(module_name)}",
  icon: {icon_name},
  href: "/{module_name}",
  color: "bg-indigo-50 text-indigo-500 dark:bg-indigo-900/20 dark:text-indigo-400"
}}""")

# Template generators for Django files
def generate_django_admin(module_name):
    return f"""from django.contrib import admin
from .models import {capitalize(module_name)}

@admin.register({capitalize(module_name)})
class {capitalize(module_name)}Admin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_at', 'updated_at')
    search_fields = ('title', 'description')
    list_filter = ('created_at', 'updated_at')
"""

def generate_django_apps(module_name):
    return f"""from django.apps import AppConfig


class {capitalize(module_name)}Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.{module_name}'
    verbose_name = '{capitalize(module_name)}'
"""

def generate_django_models(module_name, description):
    return f"""from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class {capitalize(module_name)}(models.Model):
    \"\"\"
    {description or f'{capitalize(module_name)} model'}
    \"\"\"
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='{module_name}s')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '{capitalize(module_name)}'
        verbose_name_plural = '{capitalize(module_name)}s'
        ordering = ['-created_at']

    def __str__(self):
        return self.title
"""

def generate_django_serializers(module_name):
    return f"""from rest_framework import serializers
from .models import {capitalize(module_name)}


class {capitalize(module_name)}Serializer(serializers.ModelSerializer):
    class Meta:
        model = {capitalize(module_name)}
        fields = ['id', 'title', 'description', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
"""

def generate_django_views(module_name):
    return f"""from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import {capitalize(module_name)}
from .serializers import {capitalize(module_name)}Serializer


class {capitalize(module_name)}ViewSet(viewsets.ModelViewSet):
    serializer_class = {capitalize(module_name)}Serializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return {capitalize(module_name)}.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
    @action(detail=False, methods=['GET'], permission_classes=[AllowAny])
    def public(self, request):
        \"\"\"API endpoint to get public {module_name}s\"\"\"
        queryset = {capitalize(module_name)}.objects.all()[:10]  # Limit to 10 for demo
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
"""

def generate_django_urls(module_name):
    return f"""from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import {capitalize(module_name)}ViewSet

app_name = '{module_name}'

router = DefaultRouter()
router.register(r'{module_name}s', {capitalize(module_name)}ViewSet, basename='{module_name}')

urlpatterns = [
    path('', include(router.urls)),
]
"""

def generate_django_tests(module_name):
    return f"""from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import {capitalize(module_name)}

User = get_user_model()


class {capitalize(module_name)}TestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.{module_name} = {capitalize(module_name)}.objects.create(
            title='Test {capitalize(module_name)}',
            description='Test Description',
            user=self.user
        )

    def test_{module_name}_creation(self):
        {module_name} = {capitalize(module_name)}.objects.get(id=self.{module_name}.id)
        self.assertEqual({module_name}.title, 'Test {capitalize(module_name)}')
        self.assertEqual({module_name}.user, self.user)
"""

# Template generators for React files
def generate_react_index(module_name):
    return f"""// src/addons/{module_name}/index.ts
export * from './components';
export * from './types';

// Export the API for direct usage
import {module_name}API from './api/{module_name}API';
export {{ {module_name}API }};
"""

def generate_react_api(module_name):
    return f"""// src/addons/{module_name}/api/{module_name}API.ts
import apiClient from '@/core/api/apiClient';
import {{ {capitalize(module_name)} }} from '../types';

const {module_name}API = {{
  getAll: async () => {{
    try {{
      const response = await apiClient.get('/api/v1/{module_name}/{module_name}s/');
      return response.data;
    }} catch (err) {{
      console.error('Failed to fetch {module_name}s:', err);
      throw err;
    }}
  }},

  getById: async (id: number) => {{
    try {{
      const response = await apiClient.get(`/api/v1/{module_name}/{module_name}s/${{id}}/`);
      return response.data;
    }} catch (err) {{
      console.error(`Failed to fetch {module_name} #${{id}}:`, err);
      throw err;
    }}
  }},

  create: async (data: Partial<{capitalize(module_name)}>) => {{
    try {{
      const response = await apiClient.post('/api/v1/{module_name}/{module_name}s/', data);
      return response.data;
    }} catch (err) {{
      console.error('Failed to create {module_name}:', err);
      throw err;
    }}
  }},

  update: async (id: number, data: Partial<{capitalize(module_name)}>) => {{
    try {{
      const response = await apiClient.patch(`/api/v1/{module_name}/{module_name}s/${{id}}/`, data);
      return response.data;
    }} catch (err) {{
      console.error(`Failed to update {module_name} #${{id}}:`, err);
      throw err;
    }}
  }},

  delete: async (id: number) => {{
    try {{
      await apiClient.delete(`/api/v1/{module_name}/{module_name}s/${{id}}/`);
      return true;
    }} catch (err) {{
      console.error(`Failed to delete {module_name} #${{id}}:`, err);
      throw err;
    }}
  }},
  
  // Add more API methods as needed
}};

export default {module_name}API;
"""

def generate_react_types(module_name, description):
    return f"""// src/addons/{module_name}/types/index.ts

/**
 * {description or f'Interface for {capitalize(module_name)} data'}
 */
export interface {capitalize(module_name)} {{
  id: number;
  title: string;
  description?: string;
  created_at: string;
  updated_at: string;
}}

/**
 * Props for the {capitalize(module_name)}View component
 */
export interface {capitalize(module_name)}ViewProps {{
  // Add any props needed for the view
}}

// Add more types as needed
"""

def generate_react_view(module_name, icon_name, description):
    return f"""// src/addons/{module_name}/components/{capitalize(module_name)}View.tsx
'use client';

import React, {{ useState, useEffect }} from 'react';
import {{ {icon_name} }} from 'lucide-react';
import {{ Card, CardContent, CardDescription, CardHeader, CardTitle }} from '@/components/ui/card';
import {{ Button }} from '@/components/ui/button';
import {{ Alert, AlertDescription, AlertTitle }} from '@/components/ui/alert';
import {{ {capitalize(module_name)} }} from '../types';
import {module_name}API from '../api/{module_name}API';

const {capitalize(module_name)}View: React.FC = () => {{
  const [items, setItems] = useState<{capitalize(module_name)}[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {{
    const fetchData = async () => {{
      try {{
        setLoading(true);
        const data = await {module_name}API.getAll();
        setItems(data);
        setError(null);
      }} catch (err) {{
        setError('Failed to load {module_name}s. Please try again later.');
        console.error('Error fetching {module_name}s:', err);
      }} finally {{
        setLoading(false);
      }}
    }};

    fetchData();
  }}, []);

  if (loading) {{
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }}

  if (error) {{
    return (
      <Alert variant="destructive" className="my-4">
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>{{error}}</AlertDescription>
      </Alert>
    );
  }}

  return (
    <div className="container mx-auto p-4 max-w-7xl">
      <header className="mb-8 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-purple-100 rounded-full">
            <{icon_name} className="h-6 w-6 text-purple-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">{capitalize(module_name)}</h1>
            <p className="text-gray-600">{description or f'Your {module_name} module'}</p>
          </div>
        </div>
        <Button className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-400 text-white">
          Create New
        </Button>
      </header>

      {{items.length === 0 ? (
        <Card className="text-center p-12">
          <CardContent>
            <div className="flex flex-col items-center">
              <{icon_name} className="h-16 w-16 text-gray-300 mb-4" />
              <h3 className="text-xl font-semibold mb-2">No {module_name}s found</h3>
              <p className="text-gray-500 mb-4">Create your first {module_name} to get started</p>
              <Button className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-400 text-white">
                Create {capitalize(module_name)}
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {{items.map((item) => (
            <Card key={{item.id}} className="hover:shadow-md transition-shadow">
              <CardHeader>
                <CardTitle>{{item.title}}</CardTitle>
                <CardDescription>
                  Created on {{new Date(item.created_at).toLocaleDateString()}}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700">
                  {{item.description || 'No description provided'}}
                </p>
              </CardContent>
            </Card>
          ))}}
        </div>
      )}}
    </div>
  );
}};

export default {capitalize(module_name)}View;
"""

def generate_react_components_index(module_name):
    return f"""// src/addons/{module_name}/components/index.ts
export {{ default as {capitalize(module_name)}View }} from './{capitalize(module_name)}View';
// Export other components as they're created
"""

# Helper functions
def create_file(path, content):
    """Create a file with the given content."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    print(f"Created: {path}")

def capitalize(s):
    """Capitalize the first letter of a string."""
    return s[0].upper() + s[1:] if s else s

def create_react_app_route(module_name, description):
    """Create app route for Next.js (if using app directory)."""
    app_dir = FRONTEND_ROOT / 'src' / 'app' / module_name
    
    if not app_dir.exists():
        app_dir.mkdir(parents=True, exist_ok=True)
        
        # Create page.tsx
        create_file(app_dir / 'page.tsx', f"""
// src/app/{module_name}/page.tsx
import {{ {capitalize(module_name)}View }} from '@/addons/{module_name}/components';

export const metadata = {{
  title: '{capitalize(module_name)} | Linguify',
  description: '{description or f"{capitalize(module_name)} module for Linguify"}',
}};

export default function {capitalize(module_name)}Page() {{
  return <{capitalize(module_name)}View />;
}}
""")
        
        # Create layout.tsx (optional)
        create_file(app_dir / 'layout.tsx', f"""
// src/app/{module_name}/layout.tsx
import {{ ReactNode }} from 'react';

interface {capitalize(module_name)}LayoutProps {{
  children: ReactNode;
}}

export default function {capitalize(module_name)}Layout({{ children }}: {capitalize(module_name)}LayoutProps) {{
  return (
    <div className="h-full w-full">
      {{children}}
    </div>
  );
}}
""")
        
        print(f"Created Next.js app route for '{module_name}'.")
    else:
        print(f"App route directory {app_dir} already exists.")

def main():
    """Main function to process command-line arguments and create the module."""
    parser = argparse.ArgumentParser(description='Create a new Linguify module for both Django backend and React frontend.')
    parser.add_argument('module_name', help='Name of the module to create (lowercase, no spaces)')
    parser.add_argument('module_icon', help='Icon name from Lucide icons (PascalCase, e.g., Brain, BookOpen)')
    parser.add_argument('--description', '-d', help='Description of the module', default='')
    
    args = parser.parse_args()
    
    # Validate inputs
    module_name = validate_module_name(args.module_name)
    icon_name = validate_icon_name(args.module_icon)
    description = args.description
    
    print(f"Creating new Linguify module: {module_name}")
    print(f"Icon: {icon_name}")
    print(f"Description: {description}")
    
    # Create Django app
    create_django_app(module_name, description)
    
    # Create React frontend module
    create_react_module(module_name, icon_name, description)
    
    # Create React app route (for Next.js with app directory)
    create_react_app_route(module_name, description)
    
    print("\nModule creation completed!")
    print(f"To use the module:")
    print(f"1. Run migrations: python manage.py makemigrations {module_name}")
    print(f"2. Apply migrations: python manage.py migrate {module_name}")
    print(f"3. Access the module at: http://localhost:3000/{module_name}")

if __name__ == "__main__":
    main()