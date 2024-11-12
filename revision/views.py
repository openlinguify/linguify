import csv

from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from platforme.models import Vocabulaire
from .forms import ImportForm, RevisionForm
from .models import Revision


def paginate_queryset(request, queryset, items_per_page=10):
    """
    Utility function for paginating a queryset.
    """
    paginator = Paginator(queryset, items_per_page)
    page_number = request.GET.get('page')
    try:
        return paginator.page(page_number)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        return paginator.page(paginator.num_pages)
def revision(request):
    return render(request, 'revision/revision.html')
def add_revision(request):
    form = RevisionForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Révision ajoutée avec succès.')
        return redirect('reviewed_vocabulaire_list')
    elif request.method == 'POST':
        messages.error(request, 'Erreur lors de l\'ajout de la révision.')

    return render(request, 'revision/add_revision.html', {'form': form})
def reviewed_vocabulaire_list(request):
    search_query = request.GET.get('search', '')
    type_filter = request.GET.get('type', '')
    level_filter = request.GET.get('level', '')
    revision_date_filter = request.GET.get('revision_date', '')

    revisions = Revision.objects.select_related('vocabulaire').order_by('-revision_date')

    # Filtering logic
    if search_query:
        revisions = revisions.filter(vocabulaire__word__icontains=search_query)
    if type_filter:
        revisions = revisions.filter(vocabulaire__type_word=type_filter)
    if level_filter:
        revisions = revisions.filter(vocabulaire__lesson__level_language=level_filter)
    if revision_date_filter:
        revisions = revisions.filter(revision_date=revision_date_filter)

    # Paginate the filtered queryset
    page_obj = paginate_queryset(request, revisions)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'type_filter': type_filter,
        'level_filter': level_filter,
        'revision_date_filter': revision_date_filter,
    }
    return render(request, 'revision/reviewed_vocabulaire_list.html', context)
def delete_revision(request, revision_id):
    revision = get_object_or_404(Revision, pk=revision_id)
    if request.method == 'POST':
        revision.delete()
        messages.success(request, 'Révision supprimée avec succès.')
        return redirect('reviewed_vocabulaire_list')
    return render(request, 'revision/delete_revision.html', {'revision': revision})
def import_revisions(request):
    form = ImportForm(request.POST, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        file = request.FILES.get('file')
        if file and file.name.endswith('.csv'):
            try:
                reader = csv.reader(file.read().decode('utf-8').splitlines())
                for row in reader:
                    if len(row) != 7:
                        messages.error(request, 'Le fichier CSV doit avoir exactement 7 colonnes.')
                        return redirect('import_revisions')

                    word, translation, type_word, definition, example, example_translation, lesson_id = row
                    vocabulaire, created = Vocabulaire.objects.get_or_create(
                        word=word,
                        defaults={
                            'translation': translation,
                            'type_word': type_word,
                            'definition': definition,
                            'example': example,
                            'example_translation': example_translation,
                            'lesson_id': lesson_id,
                        }
                    )
                    # Avoid duplicating revisions
                    if not Revision.objects.filter(vocabulaire=vocabulaire).exists():
                        Revision.objects.create(vocabulaire=vocabulaire)

                messages.success(request, 'Importation des révisions réussie.')
            except Exception as e:
                messages.error(request, f'Erreur lors de l\'importation des révisions : {str(e)}')
        else:
            messages.error(request, 'Le fichier doit être un fichier CSV.')

        return redirect('reviewed_vocabulaire_list')

    return render(request, 'revision/import_revisions.html', {'form': form})
def export_revisions(request):
    revisions = Revision.objects.select_related('vocabulaire')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="revisions.csv"'

    writer = csv.writer(response)
    writer.writerow(['Word', 'Translation', 'Type', 'Definition', 'Example', 'Example Translation', 'Lesson ID'])

    for revision in revisions:
        writer.writerow([
            revision.vocabulaire.word,
            revision.vocabulaire.translation,
            revision.vocabulaire.type_word,
            revision.vocabulaire.definition,
            revision.vocabulaire.example,
            revision.vocabulaire.example_translation,
            revision.vocabulaire.lesson.id if revision.vocabulaire.lesson else '',
        ])

    return response
def delete_selected_revisions(request):
    if request.method == 'POST':
        selected_revisions = request.POST.getlist('selected_revisions')
        revisions = Revision.objects.filter(id__in=selected_revisions)
        count = revisions.count()
        revisions.delete()
        messages.success(request, f'{count} révisions supprimées avec succès.')
    else:
        messages.error(request, 'Requête invalide.')
    return redirect('reviewed_vocabulaire_list')
def edit_revision(request, revision_id):
    revision = get_object_or_404(Revision, id=revision_id)
    form = RevisionForm(request.POST or None, instance=revision)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Révision modifiée avec succès.')
        return redirect('reviewed_vocabulaire_list')

    return render(request, 'revision/edit_revision.html', {'form': form, 'revision': revision})
def select_multiple_revisions(request):
    selected_revisions = request.POST.getlist('selected_revisions')
    revisions = Revision.objects.filter(id__in=selected_revisions)
    if not revisions.exists():
        messages.error(request, 'Aucune révision sélectionnée.')
        return redirect('reviewed_vocabulaire_list')

    return render(request, 'revision/select_revision.html', {'revisions': revisions})
def revision_card(request):
    revisions = Revision.objects.select_related('vocabulaire')
    return render(request, 'revision/revision_card.html', {'revisions': revisions})
def revision_list(request):
    user = request.user
    mots_a_etudier = Revision.objects.filter(user=user, known=False)
    mots_revises = Revision.objects.filter(user=user, known=True)
    return render(request, 'revision/revision_list.html', {
        'mots_a_etudier': mots_a_etudier,
        'mots_revises': mots_revises,
    })

def mark_as_known(request, revision_id):
    revision = get_object_or_404(Revision, id=revision_id, user=request.user)
    revision.known = True
    revision.last_reviewed = timezone.now()
    revision.save()
    messages.success(request, f"Vous avez marqué '{revision.vocabulaire.word}' comme connu.")
    return redirect('revision_list')

def mark_as_not_known(request, revision_id):
    revision = get_object_or_404(Revision, id=revision_id, user=request.user)
    revision.known = False
    revision.last_reviewed = timezone.now()
    revision.save()
    messages.info(request, f"Vous avez marqué '{revision.vocabulaire.word}' comme à étudier encore.")
    return redirect('revision_list')

def reset_revisions(request):
    user = request.user
    Revision.objects.filter(user=user).update(known=False, last_reviewed=timezone.now())
    messages.warning(request, "Toutes les révisions ont été réinitialisées.")
    return redirect('revision_list')