# teaching/views.py
from django.shortcuts import render
from django.contrib.auth.forms import UserChangeForm

def teaching(request):
    return render(request, 'teaching/teaching_dashboard.html')

# teaching/views.py

@login_required
def teacher_dashboard(request):
    if not hasattr(request.user, 'teacher'):
        return redirect('teaching_dashboard')

    students = request.user.teacher.get_students()
    return render(request, 'teaching/teacher_dashboard.html', {'students': students})


def teaching_dashbaord(request):
    language_filter = request.GET.get('language')
    if language_filter:
        teachers = Teacher.objects.filter(language=language_filter)
    else:
        teachers = Teacher.objects.all()
    
    if request.method == 'POST':
        teacher_id = request.POST.get('teacher_id')
        student_id = request.POST.get('student_id')
        date = request.POST.get('date')
        duration = request.POST.get('duration')
        language = request.POST.get('language')
        
        teacher = Teacher.objects.get(pk=teacher_id)
        student = User.objects.get(pk=student_id)
        
        selection = Selection(teacher=teacher, student=student, date=date, duration=duration, language=language)
        selection.save()
        return redirect('confirm_reservation')
    return render(request, 'teaching/teaching_dashboard.html', {'teachers': teachers})

# teaching/views.py

def confirm_reservation(request):
    # Récupérer la dernière sélection de l'utilisateur pour afficher les détails
    latest_selection = Selection.objects.filter(user=request.user).order_by('-selected_at').first()
    context = {
        'teacher': latest_selection.teacher if latest_selection else None,
    }
    return render(request, 'teaching/confirm_reservation.html', context)

# teaching/views.py

from django.contrib.auth.forms import UserChangeForm

@login_required
def update_profile(request):
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('teaching_dashboard')
    else:
        form = UserChangeForm(instance=request.user)
    
    return render(request, 'teaching/update_profile.html', {'form': form})


def cancel_reservation(request):
    return render(request, 'teaching/cancel_reservation.html')

def teacher_profile(request):
    return render(request, 'teaching/teacher_profile.html')

def selection_history(request):
    selections = Selection.objects.filter(user=request.user).order_by('-selected_at')
    return render(request, 'teaching/selection_history.html', {'selections': selections})
    

# Compare this snippet from teaching/urls.py:
# # teaching/urls.py
