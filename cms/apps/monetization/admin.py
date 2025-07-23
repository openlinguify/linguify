from django.contrib import admin
from .models import Sale, Payout, TeacherEarnings

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['unit', 'teacher', 'sale_price', 'teacher_earnings', 'created_at']
    list_filter = ['created_at', 'payment_method']
    search_fields = ['unit__title_en', 'teacher__user__username', 'transaction_id']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'amount', 'status', 'created_at', 'processed_at']
    list_filter = ['status', 'created_at']
    search_fields = ['teacher__user__username', 'reference']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(TeacherEarnings)
class TeacherEarningsAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'total_net_earnings', 'pending_payout', 'total_sales_count']
    search_fields = ['teacher__user__username']
    readonly_fields = ['created_at', 'updated_at']