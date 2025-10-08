"""
Monetization models for teacher earnings and payouts.
"""
from django.db import models
from django.utils import timezone
from cms.core.models import TimestampedModel
from apps.teachers.models import Teacher
from apps.contentstore.models import CMSUnit

class Sale(TimestampedModel):
    """Record of course sales."""
    
    unit = models.ForeignKey(CMSUnit, on_delete=models.CASCADE, related_name='sales')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='sales')
    student_id = models.PositiveIntegerField(help_text="Student ID from backend")
    
    # Pricing
    sale_price = models.DecimalField(max_digits=8, decimal_places=2)
    platform_commission = models.DecimalField(max_digits=8, decimal_places=2)
    teacher_earnings = models.DecimalField(max_digits=8, decimal_places=2)
    
    # Transaction info
    transaction_id = models.CharField(max_length=100, unique=True)
    payment_method = models.CharField(max_length=50)
    
    class Meta:
        db_table = 'teacher_sales'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Sale: {self.unit.title} - €{self.sale_price}"

class Payout(TimestampedModel):
    """Teacher payout records."""
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'En attente'
        PROCESSING = 'processing', 'En cours'
        COMPLETED = 'completed', 'Effectué'
        FAILED = 'failed', 'Échoué'
    
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='payouts')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    
    # Payment details
    bank_account = models.CharField(max_length=34, help_text="IBAN used for payout")
    reference = models.CharField(max_length=100, unique=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'teacher_payouts'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payout: {self.teacher.full_name} - €{self.amount}"

class TeacherEarnings(TimestampedModel):
    """Aggregated earnings summary for teachers."""
    
    teacher = models.OneToOneField(Teacher, on_delete=models.CASCADE, related_name='earnings')
    
    # Earnings breakdown
    total_gross_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_commissions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_net_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Payout info
    total_paid_out = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pending_payout = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Stats
    total_sales_count = models.PositiveIntegerField(default=0)
    last_sale_date = models.DateTimeField(null=True, blank=True)
    last_payout_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'teacher_earnings'
    
    def __str__(self):
        return f"Earnings: {self.teacher.full_name} - €{self.total_net_earnings}"