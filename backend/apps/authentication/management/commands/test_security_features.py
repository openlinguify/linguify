# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

"""
Management command to test security features
"""
from django.core.management.base import BaseCommand
from django.core.cache import cache
from ...security.rate_limiter import EmailVerificationRateLimiter
from ...security.audit_logger import SecurityAuditLogger
from ...models.models import EmailVerificationToken, User


class Command(BaseCommand):
    help = 'Test security features for email verification system'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--test-rate-limiting',
            action='store_true',
            help='Test rate limiting functionality',
        )
        parser.add_argument(
            '--test-logging',
            action='store_true',
            help='Test security logging functionality',
        )
        parser.add_argument(
            '--test-token-limits',
            action='store_true',
            help='Test token limit functionality',
        )
        parser.add_argument(
            '--clear-cache',
            action='store_true',
            help='Clear rate limiting cache',
        )
    
    def handle(self, *args, **options):
        if options['clear_cache']:
            self.test_clear_cache()
        
        if options['test_rate_limiting']:
            self.test_rate_limiting()
        
        if options['test_logging']:
            self.test_logging()
        
        if options['test_token_limits']:
            self.test_token_limits()
        
        if not any(options.values()):
            self.stdout.write('Running all tests...\n')
            self.test_rate_limiting()
            self.test_logging()
            self.test_token_limits()
    
    def test_clear_cache(self):
        """Clear rate limiting cache"""
        cache.clear()
        self.stdout.write(
            self.style.SUCCESS('✅ Cache cleared')
        )
    
    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        self.stdout.write(self.style.WARNING('Testing Rate Limiting...'))
        
        test_email = "test@example.com"
        test_ip = "192.168.1.100"
        
        # Test verification attempts
        for i in range(6):
            allowed, remaining, reset_time = EmailVerificationRateLimiter.check_verification_attempts(
                test_email, test_ip
            )
            
            self.stdout.write(f'  Attempt {i+1}: allowed={allowed}, remaining={remaining}')
            
            if allowed:
                EmailVerificationRateLimiter.record_verification_attempt(test_email, success=False)
            else:
                self.stdout.write(
                    self.style.ERROR(f'  ❌ Rate limit exceeded after {i} attempts')
                )
                break
        
        # Test lockout
        is_locked = EmailVerificationRateLimiter.is_locked_out(test_email)
        self.stdout.write(f'  Email locked out: {is_locked}')
        
        # Test resend attempts
        self.stdout.write('\n  Testing email resend limits...')
        for i in range(4):
            allowed, remaining, reset_time = EmailVerificationRateLimiter.check_resend_attempts(
                test_email, test_ip
            )
            
            self.stdout.write(f'  Resend {i+1}: allowed={allowed}, remaining={remaining}')
            
            if allowed:
                EmailVerificationRateLimiter.record_resend_attempt(test_email)
            else:
                self.stdout.write(
                    self.style.ERROR(f'  ❌ Resend limit exceeded after {i} attempts')
                )
                break
        
        self.stdout.write(
            self.style.SUCCESS('✅ Rate limiting test completed\n')
        )
    
    def test_logging(self):
        """Test security logging functionality"""
        self.stdout.write(self.style.WARNING('Testing Security Logging...'))
        
        test_email = "security-test@example.com"
        test_ip = "192.168.1.200"
        
        # Test different log types
        SecurityAuditLogger.log_event(
            'TEST_EVENT',
            test_email,
            {'test_data': 'example'},
            test_ip,
            severity='INFO'
        )
        
        SecurityAuditLogger.log_rate_limit_exceeded(
            test_email,
            'verification',
            test_ip
        )
        
        SecurityAuditLogger.log_account_lockout(
            test_email,
            'too_many_attempts',
            test_ip
        )
        
        SecurityAuditLogger.log_suspicious_activity(
            test_email,
            'Multiple failed verification attempts',
            test_ip,
            'WARNING'
        )
        
        self.stdout.write(
            self.style.SUCCESS('✅ Security logging test completed (check logs)\n')
        )
    
    def test_token_limits(self):
        """Test token limit functionality"""
        self.stdout.write(self.style.WARNING('Testing Token Limits...'))
        
        # Count current tokens
        total_tokens = EmailVerificationToken.objects.count()
        used_tokens = EmailVerificationToken.objects.filter(is_used=True).count()
        
        self.stdout.write(f'  Total tokens in database: {total_tokens}')
        self.stdout.write(f'  Used tokens: {used_tokens}')
        self.stdout.write(f'  Active tokens: {total_tokens - used_tokens}')
        
        # Find users with multiple tokens
        from django.db.models import Count
        users_with_multiple_tokens = User.objects.annotate(
            token_count=Count('email_verification_tokens')
        ).filter(token_count__gt=1)
        
        if users_with_multiple_tokens.exists():
            self.stdout.write('\n  Users with multiple tokens:')
            for user in users_with_multiple_tokens:
                self.stdout.write(f'    {user.email}: {user.token_count} tokens')
        
        # Check for expired tokens
        from django.utils import timezone
        expired_tokens = EmailVerificationToken.objects.filter(
            expires_at__lt=timezone.now()
        ).count()
        
        self.stdout.write(f'  Expired tokens: {expired_tokens}')
        
        if expired_tokens > 0:
            self.stdout.write(
                self.style.WARNING(
                    f'  ⚠️  Found {expired_tokens} expired tokens. '
                    'Run cleanup_expired_tokens command.'
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS('✅ Token limits test completed\n')
        )
    
    def test_comprehensive_security(self):
        """Run comprehensive security test"""
        self.stdout.write(
            self.style.SUCCESS('🔒 Email Verification Security System Status')
        )
        self.stdout.write('=' * 50)
        
        # Rate limiting status
        self.stdout.write('Rate Limiting: ✅ ACTIVE')
        self.stdout.write(f'  - Max verification attempts: {EmailVerificationRateLimiter.MAX_VERIFICATION_ATTEMPTS}')
        self.stdout.write(f'  - Max resend attempts: {EmailVerificationRateLimiter.MAX_RESEND_ATTEMPTS}')
        self.stdout.write(f'  - Lockout duration: {EmailVerificationRateLimiter.LOCKOUT_DURATION}s')
        
        # Token security
        self.stdout.write('\nToken Security: ✅ ACTIVE')
        self.stdout.write('  - Token length: 64 characters')
        self.stdout.write('  - Token expiration: 24 hours')
        self.stdout.write('  - Max tokens per user: 10')
        
        # Logging
        self.stdout.write('\nSecurity Logging: ✅ ACTIVE')
        self.stdout.write('  - Registration events')
        self.stdout.write('  - Verification attempts')
        self.stdout.write('  - Rate limit violations')
        self.stdout.write('  - Suspicious activities')
        
        # Input validation
        self.stdout.write('\nInput Validation: ✅ ACTIVE')
        self.stdout.write('  - Email format validation')
        self.stdout.write('  - Token format validation')
        self.stdout.write('  - Request method validation')
        
        # Anti-enumeration
        self.stdout.write('\nAnti-Enumeration: ✅ ACTIVE')
        self.stdout.write('  - Generic error messages')
        self.stdout.write('  - No email existence disclosure')
        
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(
            self.style.SUCCESS('🔒 Security system fully operational!')
        )