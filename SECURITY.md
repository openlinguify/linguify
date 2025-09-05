# Security Policy

## Overview

OpenLinguify takes security seriously. This document outlines our security practices and how to report security vulnerabilities.

## Data Protection

### Personal Information Security
All personal information has been secured throughout the codebase:
- Personal email addresses replaced with environment variables or generic examples
- Production configurations use secure environment variable management
- Development examples use placeholder values (e.g., `admin@example.com`)
- Test data uses sanitized examples to prevent information leakage

### Environment Variables
All sensitive configuration is managed through environment variables:

#### Backend (.env)
- `SECRET_KEY`: Django secret key (minimum 50 characters required)
- `DEFAULT_FROM_EMAIL`: Default sender email for system notifications
- `BUG_REPORT_EMAIL`: Bug report recipient email
- `EMAIL_HOST_USER`: SMTP authentication username
- `EMAIL_HOST_PASSWORD`: SMTP authentication password

#### Portal (.env)
- `SECRET_KEY`: Django secret key for portal application
- `DEFAULT_FROM_EMAIL`: Default sender email for portal communications
- `BUG_REPORT_EMAIL`: Bug report recipient email
- `ADMIN_EMAIL`: Administrator email for setup scripts

#### Docs (.env)
- `SECRET_KEY`: Django secret key for docs application
- `MAIN_SITE_URL`: Main website URL (www.openlinguify.com)
- `GITHUB_REPO_URL`: GitHub repository URL
- `DISCORD_URL`: Discord community invitation URL

### Database Security
- Production databases use secure connection strings via `DATABASE_URL`
- Development databases use local PostgreSQL with standard credentials
- Database migrations are version controlled and security reviewed

## Deployment Security

### Production Settings
- `DEBUG=False` enforced in all production environments
- Secure headers enabled (HSTS, secure cookies, XFrame protection)
- WhiteNoise middleware for secure static file serving
- Allowed hosts strictly configured per environment
- SECRET_KEY validation ensures minimum 50-character length

### Static Files & Assets
- Production uses compressed static files with manifest versioning
- Media files properly configured with access controls
- Official OpenLinguify branding sourced from secure locations
- Favicon generation using ImageMagick from official logo assets

## Email Security
- SMTP authentication required for production email sending
- Reply-to headers properly configured for user communications
- Email templates sanitized against injection attacks
- Development environments use console backend to prevent accidental sends
- HTML email content properly escaped and validated

## Code Security Practices

### Sensitive Data Handling
- Zero hardcoded credentials or personal information in source code
- All sensitive configuration managed through environment variables
- Example/placeholder values used in documentation and tests
- Git history cleaned of sensitive information exposure

### Django Security Framework
- SECRET_KEY validation with minimum length requirements
- CSRF protection enabled across all forms
- XSS protection through automatic template escaping
- SQL injection prevention through Django ORM usage
- Secure middleware configuration for production deployments

## Supported Versions

We actively support security updates for:

| Version | Supported          |
| ------- | ------------------ |
| Latest  | :white_check_mark: |
| Beta    | :white_check_mark: |
| < Beta  | :x:                |

## Reporting Security Issues

### How to Report

1. **Critical Vulnerabilities**: Email `info@openlinguify.com` immediately
2. **Non-sensitive Issues**: Create a GitHub issue with security label
3. **General Security Questions**: Contact `info@openlinguify.com`

**Important**: Do NOT create public GitHub issues for sensitive security vulnerabilities.

### What to Include

- Detailed description of the vulnerability
- Step-by-step reproduction instructions
- Potential impact assessment
- Affected versions/components
- Suggested mitigation or fix (if available)

### Response Process

1. **Acknowledgment**: Receipt confirmed within 24 hours
2. **Initial Assessment**: Security team review within 72 hours
3. **Fix Development**: Security patches prioritized for immediate development
4. **Testing**: Thorough testing in staging environments
5. **Deployment**: Coordinated deployment across all production environments
6. **Disclosure**: Public disclosure after fix verification and deployment

### Response Timeline

- **Critical Issues**: Target resolution within 48-72 hours
- **High Severity**: Target resolution within 7 days
- **Medium/Low Severity**: Target resolution within 30 days
- **Status Updates**: Provided weekly until resolution

## Security Implementation Details

### Authentication & Authorization
- Secure authentication implementation across all applications
- Role-based access control where applicable
- Session security with secure cookies
- Password security best practices enforced

### Input Validation & Sanitization
- All user inputs validated and sanitized
- Django forms with built-in validation
- Template auto-escaping to prevent XSS
- CSRF tokens on all state-changing operations

### Infrastructure Security
- HTTPS enforcement in production
- Secure headers configuration
- Database connection security
- File upload security with type validation

## Development Security Guidelines

### Local Development
- Use `.env.example` files as templates for secure configuration
- Never commit real credentials, API keys, or personal information
- Test with sanitized/anonymized data sets only
- Maintain strict separation between development and production data

### Code Review Process
- All code changes undergo security review
- Automated security scanning integrated into CI/CD
- Dependency vulnerability scanning with regular updates
- Secret scanning on all commits to prevent credential leaks

### Testing Security
- Security-focused test suites for authentication and authorization
- Input validation testing for all forms and APIs
- Email security testing with mock backends
- Integration tests for security middleware functionality

## Contact Information

- **Security Team**: `info@openlinguify.com`
- **General Questions**: `info@openlinguify.com`
- **Community**: [OpenLinguify Discord](https://discord.gg/PJ8uTzSS)
- **Repository**: [GitHub](https://github.com/openlinguify/linguify)

## Security Updates & Monitoring

- Security patches deployed immediately upon availability
- All environments updated simultaneously to maintain consistency
- Regular dependency auditing and updates for known vulnerabilities
- Continuous monitoring of security best practices and Django updates

---

**Last Updated**: August 2025  
**Version**: 2.0  
**Maintained by**: OpenLinguify Team
