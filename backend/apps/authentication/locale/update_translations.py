#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to update translation files for account settings
"""

TRANSLATIONS = {
    # Profile section
    "Profile picture": {
        "fr": "Photo de profil",
        "nl": "Profielfoto",
        "es": "Foto de perfil"
    },
    "Current profile picture": {
        "fr": "Photo de profil actuelle",
        "nl": "Huidige profielfoto",
        "es": "Foto de perfil actual"
    },
    "Change profile picture": {
        "fr": "Changer la photo de profil",
        "nl": "Profielfoto wijzigen",
        "es": "Cambiar foto de perfil"
    },
    "Accepted formats: JPG, PNG, WEBP. Max size: 5MB": {
        "fr": "Formats acceptés : JPG, PNG, WEBP. Taille max : 5MB",
        "nl": "Geaccepteerde formaten: JPG, PNG, WEBP. Max grootte: 5MB",
        "es": "Formatos aceptados: JPG, PNG, WEBP. Tamaño máx: 5MB"
    },

    # Personal Information
    "Personal Information": {
        "fr": "Informations personnelles",
        "nl": "Persoonlijke informatie",
        "es": "Información personal"
    },
    "First name": {
        "fr": "Prénom",
        "nl": "Voornaam",
        "es": "Nombre"
    },
    "Last name": {
        "fr": "Nom",
        "nl": "Achternaam",
        "es": "Apellido"
    },
    "Email": {
        "fr": "Email",
        "nl": "E-mail",
        "es": "Correo electrónico"
    },
    "Email cannot be changed": {
        "fr": "L'email ne peut pas être modifié",
        "nl": "E-mail kan niet worden gewijzigd",
        "es": "El correo no se puede cambiar"
    },
    "Phone number": {
        "fr": "Numéro de téléphone",
        "nl": "Telefoonnummer",
        "es": "Número de teléfono"
    },
    "Optional. Format: +32 123 456 789": {
        "fr": "Optionnel. Format : +32 123 456 789",
        "nl": "Optioneel. Formaat: +32 123 456 789",
        "es": "Opcional. Formato: +32 123 456 789"
    },
    "Username": {
        "fr": "Nom d'utilisateur",
        "nl": "Gebruikersnaam",
        "es": "Nombre de usuario"
    },
    "Biography": {
        "fr": "Biographie",
        "nl": "Biografie",
        "es": "Biografía"
    },
    "Tell us about yourself...": {
        "fr": "Parlez-nous de vous...",
        "nl": "Vertel iets over jezelf...",
        "es": "Cuéntanos sobre ti..."
    },

    # Language settings
    "Interface Language": {
        "fr": "Langue de l'interface",
        "nl": "Interface taal",
        "es": "Idioma de la interfaz"
    },
    "Choose the display language for the Linguify interface": {
        "fr": "Choisissez la langue d'affichage de l'interface Linguify",
        "nl": "Kies de weergavetaal voor de Linguify interface",
        "es": "Elige el idioma de visualización para la interfaz de Linguify"
    },

    # Privacy & Security
    "Privacy & Security": {
        "fr": "Confidentialité et sécurité",
        "nl": "Privacy & Beveiliging",
        "es": "Privacidad y seguridad"
    },
    "Public profile": {
        "fr": "Profil public",
        "nl": "Openbaar profiel",
        "es": "Perfil público"
    },
    "Allow other users to see your profile": {
        "fr": "Permettre aux autres utilisateurs de voir votre profil",
        "nl": "Andere gebruikers toestaan je profiel te zien",
        "es": "Permitir que otros usuarios vean tu perfil"
    },
    "Share my progress": {
        "fr": "Partager mes progrès",
        "nl": "Mijn voortgang delen",
        "es": "Compartir mi progreso"
    },
    "Display your learning stats on your profile": {
        "fr": "Afficher vos statistiques d'apprentissage sur votre profil",
        "nl": "Toon je leerstatistieken op je profiel",
        "es": "Mostrar tus estadísticas de aprendizaje en tu perfil"
    },

    # Learning Preferences
    "Learning Preferences": {
        "fr": "Préférences d'apprentissage",
        "nl": "Leervoorkeuren",
        "es": "Preferencias de aprendizaje"
    },
    "Native Language": {
        "fr": "Langue maternelle",
        "nl": "Moedertaal",
        "es": "Idioma nativo"
    },
    "Your native language for translations": {
        "fr": "Votre langue maternelle pour les traductions",
        "nl": "Je moedertaal voor vertalingen",
        "es": "Tu idioma nativo para traducciones"
    },
    "Target Language": {
        "fr": "Langue cible",
        "nl": "Doeltaal",
        "es": "Idioma objetivo"
    },
    "Language you are currently learning": {
        "fr": "Langue que vous apprenez actuellement",
        "nl": "Taal die je momenteel leert",
        "es": "Idioma que estás aprendiendo actualmente"
    },
    "Learning Level": {
        "fr": "Niveau d'apprentissage",
        "nl": "Leerniveau",
        "es": "Nivel de aprendizaje"
    },
    "Beginner (A1-A2)": {
        "fr": "Débutant (A1-A2)",
        "nl": "Beginner (A1-A2)",
        "es": "Principiante (A1-A2)"
    },
    "Intermediate (B1-B2)": {
        "fr": "Intermédiaire (B1-B2)",
        "nl": "Gemiddeld (B1-B2)",
        "es": "Intermedio (B1-B2)"
    },
    "Advanced (C1-C2)": {
        "fr": "Avancé (C1-C2)",
        "nl": "Gevorderd (C1-C2)",
        "es": "Avanzado (C1-C2)"
    },
    "Daily Goal": {
        "fr": "Objectif quotidien",
        "nl": "Dagelijks doel",
        "es": "Objetivo diario"
    },
    "5 minutes (Casual)": {
        "fr": "5 minutes (Décontracté)",
        "nl": "5 minuten (Casual)",
        "es": "5 minutos (Casual)"
    },
    "10 minutes (Regular)": {
        "fr": "10 minutes (Régulier)",
        "nl": "10 minuten (Regelmatig)",
        "es": "10 minutos (Regular)"
    },
    "15 minutes (Serious)": {
        "fr": "15 minutes (Sérieux)",
        "nl": "15 minuten (Serieus)",
        "es": "15 minutos (Serio)"
    },
    "30 minutes (Intense)": {
        "fr": "30 minutes (Intensif)",
        "nl": "30 minuten (Intensief)",
        "es": "30 minutos (Intenso)"
    },

    # Learning Methods
    "Learning Methods": {
        "fr": "Méthodes d'apprentissage",
        "nl": "Leermethoden",
        "es": "Métodos de aprendizaje"
    },
    "Flashcards": {
        "fr": "Cartes mémoire",
        "nl": "Flashcards",
        "es": "Tarjetas de memoria"
    },
    "Listening exercises": {
        "fr": "Exercices d'écoute",
        "nl": "Luisteroefeningen",
        "es": "Ejercicios de escucha"
    },
    "Speaking practice": {
        "fr": "Pratique orale",
        "nl": "Spreekoefeningen",
        "es": "Práctica oral"
    },
    "Grammar lessons": {
        "fr": "Leçons de grammaire",
        "nl": "Grammaticalessen",
        "es": "Lecciones de gramática"
    },

    # Notifications & Reminders
    "Notifications & Reminders": {
        "fr": "Notifications et rappels",
        "nl": "Meldingen & Herinneringen",
        "es": "Notificaciones y recordatorios"
    },
    "Daily study reminder": {
        "fr": "Rappel d'étude quotidien",
        "nl": "Dagelijkse studieherinnering",
        "es": "Recordatorio de estudio diario"
    },
    "Get reminded to practice every day": {
        "fr": "Recevez un rappel pour pratiquer chaque jour",
        "nl": "Krijg dagelijks een herinnering om te oefenen",
        "es": "Recibe recordatorios para practicar cada día"
    },
    "Streak notifications": {
        "fr": "Notifications de série",
        "nl": "Reeksmeldingen",
        "es": "Notificaciones de racha"
    },
    "Celebrate your learning streaks": {
        "fr": "Célébrez vos séries d'apprentissage",
        "nl": "Vier je leerreeksen",
        "es": "Celebra tus rachas de aprendizaje"
    },
    "Achievement notifications": {
        "fr": "Notifications de réussite",
        "nl": "Prestatiemeldingen",
        "es": "Notificaciones de logros"
    },
    "Get notified when you reach milestones": {
        "fr": "Soyez notifié lorsque vous atteignez des jalons",
        "nl": "Ontvang meldingen wanneer je mijlpalen bereikt",
        "es": "Recibe notificaciones cuando alcances hitos"
    },
    "Reminder Time": {
        "fr": "Heure de rappel",
        "nl": "Herinneringstijd",
        "es": "Hora del recordatorio"
    },
    "When to receive your daily reminder": {
        "fr": "Quand recevoir votre rappel quotidien",
        "nl": "Wanneer je dagelijkse herinnering ontvangen",
        "es": "Cuándo recibir tu recordatorio diario"
    }
}

def update_po_file(filepath, translations):
    """Update a .po file with new translations"""
    import os

    # Read existing file
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Add new translations if not present
    for en_text, trans in translations.items():
        if f'msgid "{en_text}"' not in content:
            # Add new translation entry
            entry = f'\nmsgid "{en_text}"\nmsgstr "{trans}"\n'
            content += entry
            print(f"Added: {en_text} -> {trans}")

    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Updated {filepath}")

def main():
    import os
    base_path = "/mnt/c/Users/louis/WebstormProjects/linguify/backend/apps/authentication/locale"

    # Update French translations
    fr_po = os.path.join(base_path, "fr/LC_MESSAGES/django.po")
    fr_translations = {en: trans["fr"] for en, trans in TRANSLATIONS.items()}
    update_po_file(fr_po, fr_translations)

    # Update Dutch translations
    nl_po = os.path.join(base_path, "nl/LC_MESSAGES/django.po")
    nl_translations = {en: trans["nl"] for en, trans in TRANSLATIONS.items()}
    update_po_file(nl_po, nl_translations)

    # Update Spanish translations
    es_po = os.path.join(base_path, "es/LC_MESSAGES/django.po")
    es_translations = {en: trans["es"] for en, trans in TRANSLATIONS.items()}
    update_po_file(es_po, es_translations)

    print("\nDon't forget to compile the translations with:")
    print("python manage.py compilemessages")

if __name__ == "__main__":
    main()