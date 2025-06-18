"""
Management command to generate statistics about terms acceptance
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Count, Case, When, IntegerField, DateTimeField
from apps.authentication.models import User
import csv
import os
from datetime import timedelta


class Command(BaseCommand):
    help = 'Generates statistics about terms and conditions acceptance'

    def add_arguments(self, parser):
        parser.add_argument(
            '--export',
            type=str,
            help='Export statistics to CSV file (provide filename)'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to include in the report'
        )

    def handle(self, *args, **options):
        export_file = options.get('export')
        days = options.get('days')

        # Calculate the date range
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        # Get total user count
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        
        # Get terms acceptance stats
        accepted = User.objects.filter(terms_accepted=True).count()
        not_accepted = User.objects.filter(terms_accepted=False).count()
        
        # Get stats for active users
        active_accepted = User.objects.filter(is_active=True, terms_accepted=True).count()
        active_not_accepted = User.objects.filter(is_active=True, terms_accepted=False).count()
        
        # Get stats for recent acceptances
        recent_acceptances = User.objects.filter(
            terms_accepted=True,
            terms_accepted_at__gte=start_date,
            terms_accepted_at__lte=end_date
        ).count()
        
        # Get terms version distribution
        version_stats = User.objects.filter(
            terms_accepted=True
        ).values('terms_version').annotate(
            count=Count('id')
        ).order_by('terms_version')
        
        # Display statistics
        self.stdout.write(self.style.SUCCESS(f"Terms & Conditions Acceptance Statistics (Last {days} days)"))
        self.stdout.write("=" * 60)
        self.stdout.write(f"Total users: {total_users}")
        self.stdout.write(f"Active users: {active_users}")
        self.stdout.write("-" * 60)
        self.stdout.write(f"Terms accepted: {accepted} ({accepted/total_users*100:.1f}% of all users)")
        self.stdout.write(f"Terms not accepted: {not_accepted} ({not_accepted/total_users*100:.1f}% of all users)")
        self.stdout.write("-" * 60)
        self.stdout.write(f"Active users who accepted terms: {active_accepted} ({active_accepted/active_users*100:.1f}% of active users)")
        self.stdout.write(f"Active users who haven't accepted terms: {active_not_accepted} ({active_not_accepted/active_users*100:.1f}% of active users)")
        self.stdout.write("-" * 60)
        self.stdout.write(f"Recent acceptances (last {days} days): {recent_acceptances}")
        
        # Display version distribution
        self.stdout.write("\nTerms version distribution:")
        for version in version_stats:
            ver = version['terms_version'] or 'Not specified'
            count = version['count']
            percent = count/accepted*100 if accepted > 0 else 0
            self.stdout.write(f"  {ver}: {count} ({percent:.1f}%)")
        
        # Export to CSV if requested
        if export_file:
            self.export_to_csv(export_file, total_users, active_users, accepted, not_accepted, 
                           active_accepted, active_not_accepted, recent_acceptances, version_stats)
            self.stdout.write(self.style.SUCCESS(f"\nStatistics exported to {export_file}"))
    
    def export_to_csv(self, filename, total_users, active_users, accepted, not_accepted, 
                     active_accepted, active_not_accepted, recent_acceptances, version_stats):
        """Export statistics to a CSV file"""
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write summary statistics
            writer.writerow(['Statistic', 'Value', 'Percentage'])
            writer.writerow(['Total users', total_users, '100%'])
            writer.writerow(['Active users', active_users, f'{active_users/total_users*100:.1f}%'])
            writer.writerow(['Terms accepted', accepted, f'{accepted/total_users*100:.1f}%'])
            writer.writerow(['Terms not accepted', not_accepted, f'{not_accepted/total_users*100:.1f}%'])
            writer.writerow(['Active users who accepted terms', active_accepted, 
                          f'{active_accepted/active_users*100:.1f}% of active users'])
            writer.writerow(['Active users who haven\'t accepted terms', active_not_accepted, 
                          f'{active_not_accepted/active_users*100:.1f}% of active users'])
            
            # Write version distribution
            writer.writerow([])
            writer.writerow(['Terms Version', 'Count', 'Percentage'])
            for version in version_stats:
                ver = version['terms_version'] or 'Not specified'
                count = version['count']
                percent = count/accepted*100 if accepted > 0 else 0
                writer.writerow([ver, count, f'{percent:.1f}%'])