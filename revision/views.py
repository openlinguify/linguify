# linguify/revision/views.py
import csv
from django.shortcuts import render, get_object_or_404, redirect
from .models import Revision
from .forms import ImportForm, RevisionForm
from django.forms import modelform_factory
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.contrib import messages
from platforme.models import Vocabulaire


def revision(request):
    return render(request, 'revision/revision.html')

def add_revision(request):
    if request.method == 'POST':
        form = RevisionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Révision ajoutée avec succès.')
            return redirect('reviewed_vocabulaire_list')
        else:
            messages.error(request, 'Erreur lors de l\'ajout de la révision.')
    else:
        form = RevisionForm()

    return render(request, 'revision/add_revision.html', {'form': form})


def reviewed_vocabulaire_list(request):
    search_query = request.GET.get('search', '')
    type_filter = request.GET.get('type', '')
    level_filter = request.GET.get('level', '')
    revision_date_filter = request.GET.get('revision_date', '')

    revisions = Revision.objects.all().select_related('vocabulaire').order_by('-revision_date')

    if search_query:
        revisions = revisions.filter(vocabulaire__word__icontains=search_query)
    if type_filter:
        revisions = revisions.filter(vocabulaire__type_word=type_filter)
    if level_filter:
        revisions = revisions.filter(vocabulaire__lesson__level_language=level_filter)
    if revision_date_filter:
        revisions = revisions.filter(revision_date=revision_date_filter)

    paginator = Paginator(revisions, 10)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

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
        return redirect('reviewed_vocabulaire_list')

    return render(request, 'revision/delete_revision.html', {'revision': revision})


def import_revisions(request):
    if request.method == 'POST':
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            if file.name.endswith('.csv'):
                try:
                    reader = csv.reader(file.read().decode('utf-8').splitlines())
                    for row in reader:
                        if len(row) != 7:
                            raise ValueError('Le fichier CSV doit avoir exactement 7 colonnes.')

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
                        Revision.objects.create(vocabulaire=vocabulaire)

                    messages.success(request, 'Importation des révisions réussie.')
                except Exception as e:
                    messages.error(request, f'Erreur lors de l\'importation des révisions : {str(e)}')
            else:
                messages.error(request, 'Le fichier doit être un fichier CSV.')

            return redirect('reviewed_vocabulaire_list')
    else:
        form = ImportForm()

    return render(request, 'revision/import_revisions.html', {'form': form})


def export_revisions(request):
    # Handle export logic here if needed
    # Redirect to appropriate page after export
    return redirect('reviewed_vocabulaire_list')


def export_revisions(request):
    revisions = Revision.objects.all().select_related('vocabulaire')
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
        for revision_id in selected_revisions:
            revision = get_object_or_404(Revision, pk=revision_id)
            revision.delete()
        return redirect('reviewed_vocabulaire_list')
    return JsonResponse({'error': 'Invalid request'}, status=400)


def delete_selected_revisions(request):
    if request.method == 'POST':
        selected_revisions = request.POST.getlist('selected_revisions')
        revisions = Revision.objects.filter(id__in=selected_revisions)
        revisions.delete()
        messages.success(request, f'{revisions.count()} révisions supprimées avec succès.')
        return redirect('reviewed_vocabulaire_list')
    else:
        messages.error(request, 'Requête invalide.')
        return redirect('reviewed_vocabulaire_list')


def edit_revision(request, revision_id):
    revision = get_object_or_404(Revision, id=revision_id)
    if request.method == 'POST':
        form = RevisionForm(request.POST, instance=revision)
        if form.is_valid():
            form.save()
            return redirect('reviewed_vocabulaire_list')
    else:
        form = RevisionForm(instance=revision)
    return render(request, 'revision/edit_revision.html', {'form': form, 'revision': revision})
