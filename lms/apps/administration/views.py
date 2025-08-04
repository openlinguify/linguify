from django.shortcuts import render
from django.http import HttpResponse

def administration_list(request, org_slug=None):
    """List view for administration"""
    context = {}
    if hasattr(request, 'organization') and request.organization:
        context['organization'] = request.organization
    return render(request, 'administration/list.html', context)
