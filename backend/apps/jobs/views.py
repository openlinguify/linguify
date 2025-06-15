from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import Q
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from .models import Department, JobPosition, JobApplication
from .serializers import (
    DepartmentSerializer, JobPositionListSerializer, 
    JobPositionDetailSerializer, JobApplicationCreateSerializer,
    JobApplicationSerializer
)


class DepartmentListView(generics.ListAPIView):
    """List all departments with their active job counts"""
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [AllowAny]


class JobPositionListView(generics.ListAPIView):
    """List all active job positions with filtering"""
    serializer_class = JobPositionListSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = JobPosition.objects.filter(is_active=True)
        
        # Manual filtering
        department = self.request.query_params.get('department', None)
        if department:
            queryset = queryset.filter(department_id=department)
            
        employment_type = self.request.query_params.get('employment_type', None)
        if employment_type:
            queryset = queryset.filter(employment_type=employment_type)
            
        experience_level = self.request.query_params.get('experience_level', None)
        if experience_level:
            queryset = queryset.filter(experience_level=experience_level)
            
        location = self.request.query_params.get('location', None)
        if location:
            queryset = queryset.filter(location__icontains=location)
        
        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(location__icontains=search)
            )
        
        # Featured first
        return queryset.order_by('-is_featured', '-posted_date')


class JobPositionDetailView(generics.RetrieveAPIView):
    """Get detailed information about a specific job position"""
    queryset = JobPosition.objects.filter(is_active=True)
    serializer_class = JobPositionDetailSerializer
    permission_classes = [AllowAny]


class JobApplicationCreateView(generics.CreateAPIView):
    """Submit a new job application"""
    queryset = JobApplication.objects.all()
    serializer_class = JobApplicationCreateSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Check if position is still open
        position = serializer.validated_data['position']
        if not position.is_open:
            return Response(
                {'error': 'This position is no longer accepting applications.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        return Response(
            {
                'message': 'Application submitted successfully!',
                'application_id': serializer.instance.id
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )
    
    def perform_create(self, serializer):
        application = serializer.save()
        
        # Send notification email to HR
        try:
            print(f"[DEBUG] Starting email process for application ID {application.id}")
            print(f"[DEBUG] Sending to linguify.info@gmail.com")
            print(f"[DEBUG] Resume file exists: {bool(application.resume_file)}")
            if application.resume_file:
                print(f"[DEBUG] Resume file path: {application.resume_file.path}")
                print(f"[DEBUG] Resume file name: {application.resume_file.name}")
                print(f"[DEBUG] Resume file size: {application.resume_file.size} bytes")
            subject = f"🚀 Nouvelle candidature: {application.position.title} - {application.first_name} {application.last_name}"
            
            # Create HTML message
            html_message = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; }}
                    .info-section {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                    .info-label {{ font-weight: bold; color: #555; }}
                    .cover-letter {{ background: #e9ecef; padding: 15px; border-left: 4px solid #667eea; margin: 15px 0; }}
                    .footer {{ background: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; color: #666; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>💼 Nouvelle candidature reçue</h1>
                    <p>Une nouvelle personne souhaite rejoindre l'équipe Linguify !</p>
                </div>
                
                <div class="content">
                    <div class="info-section">
                        <h2>📋 Informations sur le poste</h2>
                        <p><span class="info-label">Poste:</span> {application.position.title}</p>
                        <p><span class="info-label">Département:</span> {application.position.department.name}</p>
                        <p><span class="info-label">Localisation:</span> {application.position.location}</p>
                    </div>
                    
                    <div class="info-section">
                        <h2>👤 Informations du candidat</h2>
                        <p><span class="info-label">Nom complet:</span> {application.first_name} {application.last_name}</p>
                        <p><span class="info-label">Email:</span> <a href="mailto:{application.email}">{application.email}</a></p>
                        <p><span class="info-label">Téléphone:</span> {application.phone or 'Non fourni'}</p>
                        {f'<p><span class="info-label">Portfolio:</span> <a href="{application.portfolio_url}" target="_blank">{application.portfolio_url}</a></p>' if application.portfolio_url else ''}
                        {f'<p><span class="info-label">LinkedIn:</span> <a href="{application.linkedin_url}" target="_blank">{application.linkedin_url}</a></p>' if application.linkedin_url else ''}
                    </div>
                    
                    {f'''
                    <div class="cover-letter">
                        <h3>✉️ Lettre de motivation</h3>
                        <p>{application.cover_letter.replace(chr(10), "<br>")}</p>
                    </div>
                    ''' if application.cover_letter else ''}
                    
                    <div class="info-section">
                        <h3>📅 Détails de la candidature</h3>
                        <p><span class="info-label">Date de candidature:</span> {application.applied_at.strftime('%d/%m/%Y à %H:%M')}</p>
                        <p><span class="info-label">CV fourni:</span> {'✅ Oui (en pièce jointe)' if application.resume_file else '❌ Non'}</p>
                    </div>
                </div>
                
                <div class="footer">
                    <p>📧 Cet email a été généré automatiquement par le système de candidatures Linguify</p>
                    <p>Pour voir tous les détails dans l'admin: <a href="http://localhost:8000/admin/jobs/jobapplication/{application.id}/change/">Voir la candidature</a></p>
                </div>
            </body>
            </html>
            """
            
            # Create plain text fallback
            text_message = f"""
🚀 Nouvelle candidature reçue pour Linguify !

📋 POSTE
Position: {application.position.title}
Département: {application.position.department.name}
Localisation: {application.position.location}

👤 CANDIDAT
Nom: {application.first_name} {application.last_name}
Email: {application.email}
Téléphone: {application.phone or 'Non fourni'}
Portfolio: {application.portfolio_url or 'Non fourni'}
LinkedIn: {application.linkedin_url or 'Non fourni'}

✉️ LETTRE DE MOTIVATION
{application.cover_letter or 'Aucune lettre de motivation fournie'}

📅 DÉTAILS
Date de candidature: {application.applied_at.strftime('%d/%m/%Y à %H:%M')}
CV fourni: {'Oui (en pièce jointe)' if application.resume_file else 'Non'}

Admin: http://localhost:8000/admin/jobs/jobapplication/{application.id}/change/
            """
            
            # Create email message
            email = EmailMessage(
                subject=subject,
                body=text_message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@linguify.com'),
                to=['linguify.info@gmail.com'],
                reply_to=[application.email],
            )
            
            # Add HTML version
            email.content_subtype = 'html'
            email.body = html_message
            
            # Attach resume file if provided
            if application.resume_file:
                try:
                    email.attach_file(application.resume_file.path)
                except Exception as attach_error:
                    print(f"Failed to attach resume file: {attach_error}")
                    # Continue without attachment
            
            # Send email
            print(f"[DEBUG] About to send email...")
            result = email.send(fail_silently=False)
            print(f"[DEBUG] Email sent successfully! Result: {result}")
            
            # Check email settings
            print(f"[DEBUG] Email settings:")
            print(f"   FROM: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@linguify.com')}")
            print(f"   HOST: {getattr(settings, 'EMAIL_HOST', 'NOT SET')}")
            print(f"   PORT: {getattr(settings, 'EMAIL_PORT', 'NOT SET')}")
            print(f"   USE_TLS: {getattr(settings, 'EMAIL_USE_TLS', 'NOT SET')}")
            
            # Send confirmation email to candidate
            self._send_confirmation_email(application)
            
        except Exception as e:
            # Log the error but don't fail the application submission
            print(f"Failed to send email notification: {e}")
            import traceback
            traceback.print_exc()
    
    def _send_confirmation_email(self, application):
        """Send confirmation email to the candidate"""
        try:
            subject = f"✅ Candidature reçue - {application.position.title} chez Linguify"
            
            html_message = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; }}
                    .info-section {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                    .footer {{ background: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; color: #666; }}
                    .highlight {{ color: #667eea; font-weight: bold; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🚀 Merci pour votre candidature !</h1>
                    <p>Votre candidature a été reçue avec succès</p>
                </div>
                
                <div class="content">
                    <p>Bonjour <strong>{application.first_name}</strong>,</p>
                    
                    <p>Nous avons bien reçu votre candidature pour le poste de <span class="highlight">{application.position.title}</span> dans notre département {application.position.department.name}.</p>
                    
                    <div class="info-section">
                        <h3>📋 Récapitulatif de votre candidature</h3>
                        <p><strong>Poste:</strong> {application.position.title}</p>
                        <p><strong>Département:</strong> {application.position.department.name}</p>
                        <p><strong>Localisation:</strong> {application.position.location}</p>
                        <p><strong>Date de candidature:</strong> {application.applied_at.strftime('%d/%m/%Y à %H:%M')}</p>
                    </div>
                    
                    <p>🔍 <strong>Prochaines étapes:</strong></p>
                    <ul>
                        <li>Notre équipe RH va examiner votre candidature</li>
                        <li>Si votre profil correspond, nous vous recontacterons sous 5-10 jours ouvrés</li>
                        <li>Vous recevrez une confirmation par email pour toute mise à jour</li>
                    </ul>
                    
                    <p>💡 <strong>En attendant:</strong> N'hésitez pas à consulter notre site web pour en savoir plus sur Linguify et notre mission d'apprentissage des langues.</p>
                    
                    <p>Nous vous remercions de l'intérêt que vous portez à Linguify !</p>
                    
                    <p>Cordialement,<br>
                    <strong>L'équipe Linguify</strong></p>
                </div>
                
                <div class="footer">
                    <p>📧 Si vous avez des questions, n'hésitez pas à nous contacter à <a href="mailto:linguify.info@gmail.com">linguify.info@gmail.com</a></p>
                    <p>🌐 Visitez notre site: <a href="https://www.openlinguify.com">openlinguify.com</a></p>
                </div>
            </body>
            </html>
            """
            
            text_message = f"""
✅ Candidature reçue - {application.position.title} chez Linguify

Bonjour {application.first_name},

Nous avons bien reçu votre candidature pour le poste de {application.position.title} dans notre département {application.position.department.name}.

📋 RÉCAPITULATIF
Poste: {application.position.title}
Département: {application.position.department.name}
Localisation: {application.position.location}
Date de candidature: {application.applied_at.strftime('%d/%m/%Y à %H:%M')}

🔍 PROCHAINES ÉTAPES:
- Notre équipe RH va examiner votre candidature
- Si votre profil correspond, nous vous recontacterons sous 5-10 jours ouvrés
- Vous recevrez une confirmation par email pour toute mise à jour

💡 EN ATTENDANT: N'hésitez pas à consulter notre site web pour en savoir plus sur Linguify et notre mission d'apprentissage des langues.

Nous vous remercions de l'intérêt que vous portez à Linguify !

Cordialement,
L'équipe Linguify

📧 Questions? Contactez-nous: linguify.info@gmail.com
🌐 Site web: https://www.openlinguify.com
            """
            
            confirmation_email = EmailMessage(
                subject=subject,
                body=html_message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@linguify.com'),
                to=[application.email],
                reply_to=['linguify.info@gmail.com'],
            )
            
            confirmation_email.content_subtype = 'html'
            conf_result = confirmation_email.send(fail_silently=True)
            print(f"[DEBUG] Confirmation email sent! Result: {conf_result}")
            
        except Exception as e:
            print(f"Failed to send confirmation email: {e}")


@api_view(['GET'])
@permission_classes([AllowAny])
def job_stats(request):
    """Get general statistics about job openings"""
    total_positions = JobPosition.objects.filter(is_active=True).count()
    departments = Department.objects.all().count()
    featured_positions = JobPosition.objects.filter(is_active=True, is_featured=True).count()
    
    return Response({
        'total_positions': total_positions,
        'departments': departments,
        'featured_positions': featured_positions,
    })