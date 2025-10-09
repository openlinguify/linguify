{
    'name': 'AI Documents',
    'version': '1.0.0',
    'category': 'AI/Documents',
    'summary': 'Génération intelligente de flashcards à partir de documents (PDF, images, texte)',
    'description': """
AI Documents - Génération de Flashcards
========================================

Permet aux utilisateurs d'uploader des documents et de générer automatiquement
des flashcards intelligentes grâce à l'IA.

Fonctionnalités:
* Upload drag & drop de documents (PDF, images, texte)
* Extraction de texte (PyMuPDF, OCR avec pytesseract)
* Génération automatique de flashcards via IA (OpenAI)
* Filtrage et classification bayésienne (optionnel)
* Interface HTMX pour affichage dynamique
    """,
    'author': 'Linguify',
    'depends': [
        'apps.revision',
        'apps.authentication',
    ],
    'data': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
