from django.contrib import admin
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import path, reverse
from django.utils.html import format_html
from django.contrib.admin.views.main import ChangeList
from .models import StudentProfile, CourseEnrollment


class TenantStudentAdmin:
    """Interface admin pour les étudiants dans le contexte d'une organisation"""
    
    def __init__(self, org_slug, db_name):
        self.org_slug = org_slug
        self.db_name = db_name
    
    def get_queryset(self):
        """Obtenir les étudiants de cette organisation"""
        return StudentProfile.objects.using(self.db_name).filter(
            organization_id=self.org_slug
        )
    
    def get_urls(self):
        """URLs pour l'interface admin des étudiants"""
        return [
            path('', self.changelist_view, name='students_changelist'),
            path('<str:student_id>/change/', self.change_view, name='students_change'),
            path('add/', self.add_view, name='students_add'),
        ]
    
    @login_required
    def changelist_view(self, request):
        """Vue liste des étudiants"""
        if not hasattr(request, 'organization'):
            return JsonResponse({'error': 'Organization context required'}, status=400)
        
        # Very permissive - allow any authenticated user
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        try:
            students = self.get_queryset().select_related('user').order_by('student_id')
            
            context = {
                'title': f'Étudiants - {request.organization.name}',
                'students': students,
                'organization': request.organization,
                'opts': StudentProfile._meta,
                'has_add_permission': True,
                'has_change_permission': True,
                'has_delete_permission': True,
            }
            
            return render(request, 'admin/students/studentprofile/change_list.html', context)
            
        except Exception as e:
            context = {
                'title': f'Étudiants - {request.organization.name}',
                'error': f"Erreur base de données: {e}",
                'organization': request.organization,
                'opts': StudentProfile._meta,
            }
            return render(request, 'admin/students/studentprofile/change_list.html', context)
    
    @login_required
    def change_view(self, request, student_id):
        """Vue modification d'un étudiant"""
        try:
            student = StudentProfile.objects.using(self.db_name).get(
                student_id=student_id,
                organization_id=self.org_slug
            )
            
            enrollments = CourseEnrollment.objects.using(self.db_name).filter(
                student=student
            )
            
            context = {
                'title': f'Modifier {student.user.get_full_name()}',
                'student': student,
                'enrollments': enrollments,
                'organization': request.organization,
                'opts': StudentProfile._meta,
            }
            
            return render(request, 'admin/students/studentprofile/change_form.html', context)
            
        except StudentProfile.DoesNotExist:
            return JsonResponse({'error': 'Étudiant non trouvé'}, status=404)
    
    @login_required  
    def add_view(self, request):
        """Vue ajout d'un étudiant"""
        context = {
            'title': 'Ajouter un étudiant',
            'organization': request.organization,
            'opts': StudentProfile._meta,
        }
        
        return render(request, 'admin/students/studentprofile/add_form.html', context)