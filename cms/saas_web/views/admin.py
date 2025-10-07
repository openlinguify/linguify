"""
Admin views for SaaS management.
"""
from django.shortcuts import render
from django.views import View
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator


@method_decorator([login_required, staff_member_required], name='dispatch')
class AdminFixAppsView(View):
    """Vue d'administration pour corriger les apps"""
    
    def get(self, request):
        context = {
            'title': _('Fix Apps - Administration'),
        }
        return render(request, 'saas_web/admin/fix_apps.html', context)