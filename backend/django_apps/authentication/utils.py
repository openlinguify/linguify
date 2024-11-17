# backend/django_apps/authentication/utils.py

from django.core.mail import send_mail

def notify_coach_of_commission_change(coach_profile):
    """
    Notify the coach that their commission rate has been changed.
    """
    coach_email = coach_profile.user.email
    subject = "Important Update: Your Commission Rate Has Changed"
    message = (
        f"Dear {coach_profile.user.first_name},\n\n"
        "We hope this message finds you well.\n\n"
        "We are reaching out to let you know that your commission rate has recently been updated.\n\n"
        "Here are the details of this update:\n"
        "---------------------------------------------------\n"
        "- New Commission Rate: Please log in to view details\n"
        "- Effective Date: Effective immediately\n"
        "---------------------------------------------------\n\n"
        "To view the new commission rate and learn more about how it affects your earnings, please visit your coach profile here:\n"
        "👉 [View My Profile](https://platform.com/coach/profile)\n\n"
        "If you have any questions or concerns about this update, please feel free to reach out to us. We are here to ensure that your experience on our platform remains smooth and transparent.\n\n"
        "Thank you for your continued dedication and the positive impact you bring to your students. We sincerely appreciate having you as a valuable part of our community.\n\n"
        "Warm regards,\n"
        "The Platform Team"
    )
    send_mail(subject, message, 'noreply@platform.com', [coach_email])
