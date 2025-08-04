import os
from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
import markdown


def docs_home(request):
    """Documentation home page with navigation."""
    context = {
        'title': 'OpenLinguify Documentation',
        'description': 'Complete guide to building, contributing, and deploying the open source educational apps platform'
    }
    return render(request, 'docs/home.html', context)


def docs_page(request, page_path=''):
    """Serve documentation pages dynamically."""
    # Base path for documentation
    docs_base_path = os.path.join(settings.BASE_DIR.parent, 'docs')
    
    # Security: prevent directory traversal
    if '..' in page_path or page_path.startswith('/'):
        raise Http404("Page not found")
    
    # Determine file path
    if not page_path:
        file_path = os.path.join(docs_base_path, 'index.html')
    elif page_path.endswith('.html'):
        file_path = os.path.join(docs_base_path, page_path)
    elif page_path.endswith('.md'):
        file_path = os.path.join(docs_base_path, page_path)
    else:
        # Try both .html and .md
        html_path = os.path.join(docs_base_path, f"{page_path}.html")
        md_path = os.path.join(docs_base_path, f"{page_path}.md")
        
        if os.path.exists(html_path):
            file_path = html_path
        elif os.path.exists(md_path):
            file_path = md_path
        else:
            raise Http404("Page not found")
    
    # Check if file exists
    if not os.path.exists(file_path):
        raise Http404("Page not found")
    
    # Read and serve file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # If it's a markdown file, convert to HTML and wrap in template
        if file_path.endswith('.md'):
            md = markdown.Markdown(extensions=['codehilite', 'toc', 'tables'])
            html_content = md.convert(content)
            
            # Extract title from first h1 or use filename
            title = page_path.replace('/', ' - ').replace('.md', '').title()
            if content.startswith('# '):
                title = content.split('\n')[0][2:].strip()
            
            context = {
                'title': title,
                'content': mark_safe(html_content),
                'page_path': page_path,
            }
            return render(request, 'docs/markdown_page.html', context)
        
        # If it's HTML, extract content and integrate into portal layout
        elif file_path.endswith('.html'):
            # Extract title from HTML
            title = "Documentation"
            if '<title>' in content:
                title = content.split('<title>')[1].split('</title>')[0]
                title = title.replace(' - OpenLinguify Documentation', '')
            
            # Extract only the main content from the HTML
            body_content = content
            if '<main class="docs-main">' in content:
                # Extract content from the main section
                start = content.find('<main class="docs-main">') + len('<main class="docs-main">')
                end = content.find('</main>')
                if end != -1:
                    body_content = content[start:end]
                    # Remove the docs-content wrapper if present
                    if '<div class="docs-content">' in body_content:
                        start_content = body_content.find('<div class="docs-content">') + len('<div class="docs-content">')
                        end_content = body_content.rfind('</div>')
                        if end_content != -1:
                            body_content = body_content[start_content:end_content]
            elif '<body>' in content:
                # Fallback: extract body content
                start = content.find('<body>') + len('<body>')
                end = content.find('</body>')
                if end != -1:
                    body_content = content[start:end]
            
            # Clean up template tags and problematic content
            import re
            # Remove Django template tags that shouldn't be processed
            body_content = re.sub(r'{%\s*static\s*[^%]*%}', '', body_content)
            body_content = re.sub(r'{%\s*load\s*[^%]*%}', '', body_content)
            body_content = re.sub(r'{% extends [^%]*%}', '', body_content)
            body_content = re.sub(r'{% block [^%]*%}', '', body_content)
            body_content = re.sub(r'{% endblock [^%]*%}', '', body_content)
            
            # Fix any remaining broken links
            body_content = re.sub(r'href="{% static [^"]*%}"', 'href="#"', body_content)
            
            context = {
                'title': title,
                'html_content': mark_safe(body_content),
                'page_path': page_path,
            }
            return render(request, 'docs/html_page.html', context)
        
        else:
            # For other file types, return as-is
            with open(file_path, 'rb') as f:
                response = HttpResponse(f.read())
                response['Content-Type'] = 'application/octet-stream'
                return response
                
    except Exception as e:
        raise Http404(f"Error reading file: {str(e)}")


def quick_start(request):
    """Quick start guide."""
    return docs_page(request, 'setup/getting-started.html')


def environment_setup(request):
    """Environment setup guide."""
    return docs_page(request, 'setup/environment-setup.html')


def developer_guidelines(request):
    """Developer guidelines."""
    return docs_page(request, 'development/developer-guidelines.html')


def translation_guide(request):
    """Translation guide."""
    return docs_page(request, 'translations/translation-guide.md')


def api_reference(request):
    """API reference (placeholder)."""
    context = {
        'title': 'API Reference',
        'description': 'Complete REST API documentation - Coming Soon'
    }
    return render(request, 'docs/placeholder.html', context)