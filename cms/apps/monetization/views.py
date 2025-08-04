from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Sale, Payout, TeacherEarnings

class EarningsDashboardView(LoginRequiredMixin, TemplateView):
    """Teacher earnings dashboard."""
    template_name = 'monetization/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            earnings = TeacherEarnings.objects.get(teacher__user=self.request.user)
            context['earnings'] = earnings
        except TeacherEarnings.DoesNotExist:
            context['earnings'] = None
        return context

class SalesListView(LoginRequiredMixin, ListView):
    """List teacher's sales."""
    model = Sale
    template_name = 'monetization/sales.html'
    paginate_by = 20
    
    def get_queryset(self):
        return Sale.objects.filter(teacher__user=self.request.user)

class PayoutListView(LoginRequiredMixin, ListView):
    """List teacher's payouts."""
    model = Payout
    template_name = 'monetization/payouts.html'
    paginate_by = 20
    
    def get_queryset(self):
        return Payout.objects.filter(teacher__user=self.request.user)