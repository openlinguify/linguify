# -*- coding: utf-8 -*-
"""
XML Export Views - Export des notes au format XML
"""
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.template.loader import render_to_string
import xml.etree.ElementTree as ET
from xml.dom import minidom

from ..models import Note, NoteCategory


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_notes_xml(request):
    """Exporte toutes les notes de l'utilisateur au format XML"""
    notes = Note.objects.filter(user=request.user).select_related('category')[:10]  # Limiter pour l'exemple

    # Créer la structure XML
    root = ET.Element("linguify")
    data = ET.SubElement(root, "data")

    # Ajouter chaque note comme un record XML
    for note in notes:
        record = ET.SubElement(data, "record", id=f"note_{note.id}", model="notebook.note")

        # Titre
        title_field = ET.SubElement(record, "field", name="title")
        title_field.text = note.title

        # Contenu
        content_field = ET.SubElement(record, "field", name="content")
        content_field.text = note.content or ""

        # Catégorie
        if note.category:
            category_field = ET.SubElement(record, "field", name="category")
            category_field.text = note.category.name

        # Type de note
        type_field = ET.SubElement(record, "field", name="note_type")
        type_field.text = note.note_type

        # Langue
        if note.language:
            language_field = ET.SubElement(record, "field", name="language")
            language_field.text = note.language

        # Difficulté
        if note.difficulty:
            difficulty_field = ET.SubElement(record, "field", name="difficulty")
            difficulty_field.text = note.difficulty

        # Priorité
        priority_field = ET.SubElement(record, "field", name="priority")
        priority_field.text = note.priority

        # Épinglé
        pinned_field = ET.SubElement(record, "field", name="is_pinned")
        pinned_field.text = "true" if note.is_pinned else "false"

        # Archivé
        archived_field = ET.SubElement(record, "field", name="is_archived")
        archived_field.text = "true" if note.is_archived else "false"

        # Dates
        created_field = ET.SubElement(record, "field", name="created_at")
        created_field.text = note.created_at.isoformat() if note.created_at else ""

        updated_field = ET.SubElement(record, "field", name="updated_at")
        updated_field.text = note.updated_at.isoformat() if note.updated_at else ""

    # Formater le XML avec indentation
    rough_string = ET.tostring(root, encoding='unicode')
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ")

    # Nettoyer les lignes vides en trop
    lines = [line for line in pretty_xml.split('\n') if line.strip()]
    clean_xml = '\n'.join(lines)

    return HttpResponse(clean_xml, content_type='application/xml')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_single_note_xml(request, note_id):
    """Exporte une seule note au format XML"""
    try:
        note = Note.objects.get(id=note_id, user=request.user)

        # Créer la structure XML pour une seule note
        root = ET.Element("linguify")
        data = ET.SubElement(root, "data")

        record = ET.SubElement(data, "record", id=f"note_{note.id}", model="notebook.note")

        # Ajouter tous les champs de la note
        fields = {
            'title': note.title,
            'content': note.content or "",
            'category': note.category.name if note.category else "",
            'note_type': note.note_type,
            'language': note.language or "",
            'difficulty': note.difficulty or "",
            'priority': note.priority,
            'is_pinned': "true" if note.is_pinned else "false",
            'is_archived': "true" if note.is_archived else "false",
            'created_at': note.created_at.isoformat() if note.created_at else "",
            'updated_at': note.updated_at.isoformat() if note.updated_at else "",
        }

        for field_name, field_value in fields.items():
            field_element = ET.SubElement(record, "field", name=field_name)
            field_element.text = str(field_value)

        # Formater le XML
        rough_string = ET.tostring(root, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ")

        lines = [line for line in pretty_xml.split('\n') if line.strip()]
        clean_xml = '\n'.join(lines)

        return HttpResponse(clean_xml, content_type='application/xml')

    except Note.DoesNotExist:
        return HttpResponse(
            '<?xml version="1.0" encoding="UTF-8"?>\n<error>Note non trouvée</error>',
            content_type='application/xml',
            status=404
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_notes_odoo_style(request):
    """Exporte les notes dans un style Odoo/OpenERP plus authentique"""
    notes = Note.objects.filter(user=request.user).select_related('category')[:10]

    # Créer XML style Odoo
    root = ET.Element("openerp")
    data = ET.SubElement(root, "data")

    # Ajouter les catégories d'abord
    categories = set()
    for note in notes:
        if note.category:
            categories.add(note.category)

    for category in categories:
        cat_record = ET.SubElement(data, "record",
                                  id=f"category_{category.id}",
                                  model="note.category")

        name_field = ET.SubElement(cat_record, "field", name="name")
        name_field.text = category.name

        if category.description:
            desc_field = ET.SubElement(cat_record, "field", name="description")
            desc_field.text = category.description

    # Ajouter les notes
    for note in notes:
        record = ET.SubElement(data, "record",
                              id=f"note_{note.id}",
                              model="note.note")

        # Référence au modèle en style Odoo
        title_field = ET.SubElement(record, "field", name="name")  # 'name' au lieu de 'title' en style Odoo
        title_field.text = note.title

        content_field = ET.SubElement(record, "field", name="description")
        content_field.text = note.content or ""

        if note.category:
            category_field = ET.SubElement(record, "field", name="category_id", ref=f"category_{note.category.id}")

        state_field = ET.SubElement(record, "field", name="state")
        if note.is_archived:
            state_field.text = "archived"
        elif note.is_pinned:
            state_field.text = "pinned"
        else:
            state_field.text = "draft"

        # Priorité en style Odoo (0-3)
        priority_field = ET.SubElement(record, "field", name="priority")
        priority_map = {'LOW': '1', 'MEDIUM': '2', 'HIGH': '3'}
        priority_field.text = priority_map.get(note.priority, '2')

    # Formater et retourner
    rough_string = ET.tostring(root, encoding='unicode')
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="    ")

    lines = [line for line in pretty_xml.split('\n') if line.strip()]
    clean_xml = '\n'.join(lines)

    return HttpResponse(clean_xml, content_type='application/xml')