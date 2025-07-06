from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import StudentProfile, CourseEnrollment

@login_required
def student_list(request, org_slug=None):
    """Liste des étudiants pour une organisation"""
    if not hasattr(request, 'organization') or not request.organization:
        return JsonResponse({'error': 'Organization context required'}, status=400)
    
    # Check basic authentication only - very permissive for testing
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    # Obtenir les étudiants de la base tenant
    db_name = request.organization.database_name
    try:
        students = StudentProfile.objects.using(db_name).filter(
            organization_id=request.organization.slug
        ).select_related('user').order_by('student_id')
        
        # Pagination
        paginator = Paginator(students, 25)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'organization': request.organization,
            'students': page_obj,
            'total_students': paginator.count,
            'user_role': user_role,
        }
        
        return render(request, 'students/student_list.html', context)
        
    except Exception as e:
        context = {
            'organization': request.organization,
            'error': f"Base de données non configurée: {e}",
            'user_role': user_role,
        }
        return render(request, 'students/student_list.html', context)

@login_required
def student_detail(request, org_slug=None, student_id=None):
    """Détail d'un étudiant"""
    if not hasattr(request, 'organization') or not request.organization:
        return JsonResponse({'error': 'Organization context required'}, status=400)
    
    user_role = getattr(request, 'user_role', 'guest')
    if user_role not in ['owner', 'administrator', 'instructor']:
        return JsonResponse({'error': 'Insufficient permissions'}, status=403)
    
    db_name = request.organization.database_name
    try:
        student = get_object_or_404(
            StudentProfile.objects.using(db_name),
            student_id=student_id,
            organization_id=request.organization.slug
        )
        
        # Obtenir les inscriptions
        enrollments = CourseEnrollment.objects.using(db_name).filter(
            student=student
        ).order_by('-enrolled_at')
        
        context = {
            'organization': request.organization,
            'student': student,
            'enrollments': enrollments,
            'user_role': user_role,
        }
        
        return render(request, 'students/student_detail.html', context)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def students_list(request):
    """Legacy view - redirect to organization context"""
    return render(request, 'students/list.html')

@login_required
def students_admin_interface(request, org_slug=None):
    """Interface admin style pour les étudiants"""
    if not hasattr(request, 'organization') or not request.organization:
        return JsonResponse({'error': 'Organization context required'}, status=400)
    
    # Very permissive permissions - allow any authenticated user
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    # Utiliser l'admin personnalisé
    from .admin_views import TenantStudentAdmin
    admin_instance = TenantStudentAdmin(request.organization.slug, request.organization.database_name)
    
    return admin_instance.changelist_view(request)
