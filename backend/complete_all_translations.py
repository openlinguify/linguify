#!/usr/bin/env python3
"""
Complete all missing translations for all languages based on the Portuguese reference
"""

import os
import shutil

def get_complete_translation_template():
    """Return the complete translation template based on Portuguese"""
    return '''# TRANSLATION FOR PUBLIC_WEB
# Copyright (C) 2025 Open Linguify
# This file is distributed under the same license as the Open Linguify package.
#
msgid ""
msgstr ""
"Project-Id-Version: Open Linguify Public Web\\n"
"Report-Msgid-Bugs-To: \\n"
"POT-Creation-Date: 2025-06-17 00:00+0000\\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n"
"Last-Translator: Open Linguify Team\\n"
"Language-Team: {language_name}\\n"
"Language: {lang_code}\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
"Plural-Forms: {plural_forms};\\n"

# SEO Meta Tags
msgid "Learn Languages with AI - Interactive Language Learning Platform"
msgstr "{seo_title}"

msgid "Master new languages with our AI-powered interactive platform. Personalized lessons, real-time feedback, and engaging exercises for effective language learning."
msgstr "{seo_description}"

msgid "language learning, AI, interactive, personalized, lessons, multilingual, education"
msgstr "{seo_keywords}"

# Navigation
msgid "Home"
msgstr "{home}"

msgid "Features"
msgstr "{features}"

msgid "Pricing"
msgstr "{pricing}"

msgid "About"
msgstr "{about}"

msgid "Contact"
msgstr "{contact}"

msgid "Get Started"
msgstr "{get_started}"

msgid "Sign In"
msgstr "{sign_in}"

msgid "Language"
msgstr "{language}"

# Hero Section
msgid "Master Languages with AI"
msgstr "{hero_title}"

msgid "Experience the future of language learning with our AI-powered platform. Personalized lessons, real-time feedback, and interactive exercises designed just for you."
msgstr "{hero_subtitle}"

msgid "Start Learning Now"
msgstr "{start_learning}"

msgid "Watch Demo"
msgstr "{watch_demo}"

# Stats Section
msgid "Active Learners"
msgstr "{active_learners}"

msgid "Languages Available"
msgstr "{languages_available}"

msgid "Lessons Completed"
msgstr "{lessons_completed}"

msgid "Success Rate"
msgstr "{success_rate}"

# Features Section
msgid "Why Choose Our Platform?"
msgstr "{why_choose}"

msgid "AI-Powered Learning"
msgstr "{ai_learning}"

msgid "Our advanced AI adapts to your learning style and pace, providing personalized recommendations and feedback."
msgstr "{ai_description}"

msgid "Interactive Exercises"
msgstr "{interactive_exercises}"

msgid "Engage with dynamic exercises including speaking practice, listening comprehension, and writing challenges."
msgstr "{exercises_description}"

msgid "Progress Tracking"
msgstr "{progress_tracking}"

msgid "Monitor your learning journey with detailed analytics and progress reports to stay motivated."
msgstr "{progress_description}"

msgid "Multi-Device Access"
msgstr "{multi_device}"

msgid "Learn anywhere, anytime with seamless synchronization across all your devices."
msgstr "{device_description}"

msgid "Expert Content"
msgstr "{expert_content}"

msgid "Curriculum designed by language experts and native speakers for authentic learning experiences."
msgstr "{expert_description}"

msgid "Community Support"
msgstr "{community_support}"

msgid "Join a vibrant community of learners and get support from fellow students and instructors."
msgstr "{community_description}"

# Pricing Section
msgid "Choose Your Plan"
msgstr "{choose_plan}"

msgid "Start your language learning journey with the plan that fits your needs."
msgstr "{plan_description}"

msgid "Free"
msgstr "{free}"

msgid "Perfect for getting started"
msgstr "{free_description}"

msgid "Access to basic lessons"
msgstr "{basic_access}"

msgid "Limited AI features"
msgstr "{limited_ai}"

msgid "Community support"
msgstr "{community_support_lower}"

msgid "Start Free"
msgstr "{start_free}"

msgid "Pro"
msgstr "{pro}"

msgid "month"
msgstr "{month}"

msgid "Best for serious learners"
msgstr "{pro_description}"

msgid "Unlimited lessons"
msgstr "{unlimited_lessons}"

msgid "Full AI-powered features"
msgstr "{full_ai}"

msgid "Priority support"
msgstr "{priority_support}"

msgid "Offline access"
msgstr "{offline_access}"

msgid "Choose Pro"
msgstr "{choose_pro}"

msgid "Enterprise"
msgstr "{enterprise}"

msgid "For teams and organizations"
msgstr "{enterprise_description}"

msgid "Custom solutions"
msgstr "{custom_solutions}"

msgid "Advanced analytics"
msgstr "{advanced_analytics}"

msgid "Dedicated support"
msgstr "{dedicated_support}"

msgid "Contact Sales"
msgstr "{contact_sales}"

# Footer
msgid "Ready to start your language learning journey?"
msgstr "{ready_start}"

msgid "Join thousands of learners who have already transformed their language skills with our AI-powered platform."
msgstr "{join_thousands}"

msgid "Product"
msgstr "{product}"

msgid "Courses"
msgstr "{courses}"

msgid "Mobile App"
msgstr "{mobile_app}"

msgid "API"
msgstr "{api}"

msgid "Company"
msgstr "{company}"

msgid "Blog"
msgstr "{blog}"

msgid "Careers"
msgstr "{careers}"

msgid "Press"
msgstr "{press}"

msgid "Support"
msgstr "{support}"

msgid "Help Center"
msgstr "{help_center}"

msgid "Privacy Policy"
msgstr "{privacy_policy}"

msgid "Terms of Service"
msgstr "{terms_service}"

msgid "Legal"
msgstr "{legal}"

msgid "Cookie Policy"
msgstr "{cookie_policy}"

msgid "All rights reserved."
msgstr "{all_rights}"

# Content specific
msgid "Open Source Education Apps"
msgstr "{open_source_apps}"

msgid "A complete suite of open source educational apps: memorization, flashcards, note-taking, quizzes, collaborative chat and much more."
msgstr "{complete_suite}"

msgid "Start for free"
msgstr "{start_for_free}"

msgid "Discover our apps"
msgstr "{discover_apps}"

msgid "Educational Apps"
msgstr "{educational_apps}"

msgid "Flashcards Created"
msgstr "{flashcards_created}"

msgid "Quizzes Generated"
msgstr "{quizzes_generated}"

msgid "Open Source"
msgstr "{open_source}"

msgid "Our Educational Apps"
msgstr "{our_apps}"

msgid "Discover our suite of 5 apps designed to transform your learning experience. Choose one for free or access all with Premium."
msgstr "{apps_description}"

msgid "Structured courses with progressive lessons, interactive exercises and personalized assessments."
msgstr "{courses_description}"

msgid "Revision"
msgstr "{revision}"

msgid "Spaced repetition system with smart flashcards for optimal memorization."
msgstr "{revision_description}"

msgid "Notebook"
msgstr "{notebook}"

msgid "Centralized note-taking with intelligent organization and advanced search."
msgstr "{notebook_description}"

msgid "Quiz"
msgstr "{quiz}"

msgid "Adaptive quiz system to test your knowledge and identify weak points."
msgstr "{quiz_description}"

msgid "Language AI"
msgstr "{language_ai}"

msgid "AI assistant for natural conversations and intelligent real-time corrections."
msgstr "{ai_assistant_description}"

msgid "New Educational Apps Coming Soon"
msgstr "{new_apps_coming}"

msgid "Our teams are actively working on innovative new educational apps to enrich our learning ecosystem. These upcoming tools will offer even more ways to master languages."
msgstr "{teams_working}"

msgid "AI Writing Assistant"
msgstr "{ai_writing}"

msgid "Pronunciation Trainer"
msgstr "{pronunciation}"

msgid "Cultural Immersion"
msgstr "{cultural}"

msgid "Grammar Checker"
msgstr "{grammar}"

msgid "Coming in 2025"
msgstr "{coming_2025}"

msgid "Neuroscience-based language acquisition"
msgstr "{neuroscience}"

msgid "Native speaker community"
msgstr "{native_speakers}"

msgid "Industry-recognized certifications"
msgstr "{certifications}"

msgid "Plans adapted to your needs"
msgstr "{plans_adapted}"

msgid "Choose the offer that matches your goals and learning pace."
msgstr "{choose_offer}"

msgid "forever"
msgstr "{forever}"

msgid "Perfect for discovering the platform"
msgstr "{perfect_discovering}"

msgid "Access to 1 app of your choice"
msgstr "{access_1_app}"

msgid "Full use of the chosen app"
msgstr "{full_use}"

msgid "Free updates"
msgstr "{free_updates}"

msgid "Most popular"
msgstr "{most_popular}"

msgid "per month"
msgstr "{per_month}"

msgid "Full access to all applications"
msgstr "{full_access}"

msgid "Access to all applications"
msgstr "{access_all}"

msgid "structured lessons"
msgstr "{structured_lessons}"

msgid "unlimited flashcards"
msgstr "{unlimited_flashcards}"

msgid "unlimited notes"
msgstr "{unlimited_notes}"

msgid "Quiz & Language AI included"
msgstr "{quiz_ai_included}"

msgid "Ready to revolutionize your learning?"
msgstr "{ready_revolutionize}"

msgid "Join our community and access a complete suite of open source educational apps."
msgstr "{join_community}"

msgid "Open source educational apps platform: memorization, flashcards, notes, quizzes and collaborative chat."
msgstr "{platform_description}"

msgid "Resources"
msgstr "{resources}"

msgid "Roadmap"
msgstr "{roadmap}"

msgid "Documentation"
msgstr "{documentation}"

msgid "Community"
msgstr "{community}"

msgid "Status"
msgstr "{status}"

msgid "Report a bug"
msgstr "{report_bug}"

msgid "Contact us"
msgstr "{contact_us}"

msgid "Privacy"
msgstr "{privacy}"

msgid "Terms"
msgstr "{terms}"

msgid "Cookies"
msgstr "{cookies}"

msgid "7-day free trial"
msgstr "{free_trial}"

msgid "My Notes"
msgstr "{my_notes}"

msgid "Join the waiting list"
msgstr "{waiting_list}"

msgid "Go to Dashboard"
msgstr "{go_dashboard}"

msgid "Access Dashboard"
msgstr "{access_dashboard}"
'''

def get_language_translations():
    """Return translations for each language"""
    return {
        'it': {
            'language_name': 'Italian',
            'plural_forms': 'nplurals=2; plural=(n != 1)',
            'seo_title': 'Impara le Lingue con AI - Piattaforma Interattiva per l\'Apprendimento delle Lingue',
            'seo_description': 'Padroneggia nuove lingue con la nostra piattaforma interattiva alimentata da AI. Lezioni personalizzate, feedback in tempo reale ed esercizi coinvolgenti per un apprendimento efficace delle lingue.',
            'seo_keywords': 'apprendimento lingue, AI, interattivo, personalizzato, lezioni, multilingue, educazione',
            'home': 'Home',
            'features': 'Caratteristiche',
            'pricing': 'Prezzi',
            'about': 'Chi Siamo',
            'contact': 'Contatto',
            'get_started': 'Inizia',
            'sign_in': 'Accedi',
            'language': 'Lingua',
            'hero_title': 'Padroneggia le Lingue con AI',
            'hero_subtitle': 'Sperimenta il futuro dell\'apprendimento delle lingue con la nostra piattaforma alimentata da AI. Lezioni personalizzate, feedback in tempo reale ed esercizi interattivi progettati solo per te.',
            'start_learning': 'Inizia ad Imparare Ora',
            'watch_demo': 'Guarda Demo',
            'active_learners': 'Studenti Attivi',
            'languages_available': 'Lingue Disponibili',
            'lessons_completed': 'Lezioni Completate',
            'success_rate': 'Tasso di Successo',
            'why_choose': 'Perché Scegliere la Nostra Piattaforma?',
            'ai_learning': 'Apprendimento Alimentato da AI',
            'ai_description': 'La nostra AI avanzata si adatta al tuo stile di apprendimento e ritmo, fornendo raccomandazioni personalizzate e feedback.',
            'interactive_exercises': 'Esercizi Interattivi',
            'exercises_description': 'Partecipa a esercizi dinamici inclusi pratica di conversazione, comprensione all\'ascolto e sfide di scrittura.',
            'progress_tracking': 'Monitoraggio Progressi',
            'progress_description': 'Monitora il tuo percorso di apprendimento con analisi dettagliate e report sui progressi per rimanere motivato.',
            'multi_device': 'Accesso Multi-Dispositivo',
            'device_description': 'Impara ovunque, in qualsiasi momento con sincronizzazione perfetta su tutti i tuoi dispositivi.',
            'expert_content': 'Contenuto Esperto',
            'expert_description': 'Curriculum progettato da esperti di lingue e madrelingua per esperienze di apprendimento autentiche.',
            'community_support': 'Supporto della Comunità',
            'community_description': 'Unisciti a una comunità vibrante di studenti e ricevi supporto da colleghi studenti e istruttori.',
            'choose_plan': 'Scegli il Tuo Piano',
            'plan_description': 'Inizia il tuo percorso di apprendimento delle lingue con il piano che si adatta alle tue esigenze.',
            'free': 'Gratis',
            'free_description': 'Perfetto per iniziare',
            'basic_access': 'Accesso a lezioni base',
            'limited_ai': 'Funzionalità AI limitate',
            'community_support_lower': 'Supporto della comunità',
            'start_free': 'Inizia Gratis',
            'pro': 'Pro',
            'month': 'mese',
            'pro_description': 'Migliore per studenti seri',
            'unlimited_lessons': 'Lezioni illimitate',
            'full_ai': 'Funzionalità AI complete',
            'priority_support': 'Supporto prioritario',
            'offline_access': 'Accesso offline',
            'choose_pro': 'Scegli Pro',
            'enterprise': 'Azienda',
            'enterprise_description': 'Per team e organizzazioni',
            'custom_solutions': 'Soluzioni personalizzate',
            'advanced_analytics': 'Analisi avanzate',
            'dedicated_support': 'Supporto dedicato',
            'contact_sales': 'Contatta Vendite',
            'ready_start': 'Pronto per iniziare il tuo percorso di apprendimento delle lingue?',
            'join_thousands': 'Unisciti a migliaia di studenti che hanno già trasformato le loro competenze linguistiche con la nostra piattaforma alimentata da AI.',
            'product': 'Prodotto',
            'courses': 'Corsi',
            'mobile_app': 'App Mobile',
            'api': 'API',
            'company': 'Azienda',
            'blog': 'Blog',
            'careers': 'Carriere',
            'press': 'Stampa',
            'support': 'Supporto',
            'help_center': 'Centro Aiuto',
            'privacy_policy': 'Politica Privacy',
            'terms_service': 'Termini di Servizio',
            'legal': 'Legale',
            'cookie_policy': 'Politica Cookie',
            'all_rights': 'Tutti i diritti riservati.',
            'open_source_apps': 'App Educative Open Source',
            'complete_suite': 'Una suite completa di app educative open source: memorizzazione, flashcard, prese di note, quiz, chat collaborativa e molto altro.',
            'start_for_free': 'Inizia gratis',
            'discover_apps': 'Scopri le nostre app',
            'educational_apps': 'App Educative',
            'flashcards_created': 'Flashcard Create',
            'quizzes_generated': 'Quiz Generati',
            'open_source': 'Open Source',
            'our_apps': 'Le Nostre App Educative',
            'apps_description': 'Scopri la nostra suite di 5 app progettate per trasformare la tua esperienza di apprendimento. Scegline una gratis o accedi a tutte con Premium.',
            'courses_description': 'Corsi strutturati con lezioni progressive, esercizi interattivi e valutazioni personalizzate.',
            'revision': 'Revisione',
            'revision_description': 'Sistema di ripetizione spaziata con flashcard intelligenti per memorizzazione ottimale.',
            'notebook': 'Quaderno',
            'notebook_description': 'Presa di note centralizzata con organizzazione intelligente e ricerca avanzata.',
            'quiz': 'Quiz',
            'quiz_description': 'Sistema di quiz adattivo per testare le tue conoscenze e identificare punti deboli.',
            'language_ai': 'AI Linguistico',
            'ai_assistant_description': 'Assistente AI per conversazioni naturali e correzioni intelligenti in tempo reale.',
            'new_apps_coming': 'Nuove App Educative in Arrivo',
            'teams_working': 'I nostri team stanno lavorando attivamente su nuove app educative innovative per arricchire il nostro ecosistema di apprendimento. Questi strumenti futuri offriranno ancora più modi per padroneggiare le lingue.',
            'ai_writing': 'Assistente Scrittura AI',
            'pronunciation': 'Trainer Pronuncia',
            'cultural': 'Immersione Culturale',
            'grammar': 'Correttore Grammaticale',
            'coming_2025': 'In Arrivo nel 2025',
            'neuroscience': 'Acquisizione linguistica basata su neuroscienze',
            'native_speakers': 'Comunità di madrelingua',
            'certifications': 'Certificazioni riconosciute dall\'industria',
            'plans_adapted': 'Piani adattati alle tue esigenze',
            'choose_offer': 'Scegli l\'offerta che corrisponde ai tuoi obiettivi e ritmo di apprendimento.',
            'forever': 'per sempre',
            'perfect_discovering': 'Perfetto per scoprire la piattaforma',
            'access_1_app': 'Accesso a 1 app di tua scelta',
            'full_use': 'Uso completo dell\'app scelta',
            'free_updates': 'Aggiornamenti gratuiti',
            'most_popular': 'Più popolare',
            'per_month': 'al mese',
            'full_access': 'Accesso completo a tutte le applicazioni',
            'access_all': 'Accesso a tutte le applicazioni',
            'structured_lessons': 'lezioni strutturate',
            'unlimited_flashcards': 'flashcard illimitate',
            'unlimited_notes': 'note illimitate',
            'quiz_ai_included': 'Quiz e AI Linguistico inclusi',
            'ready_revolutionize': 'Pronto a rivoluzionare il tuo apprendimento?',
            'join_community': 'Unisciti alla nostra comunità e accedi a una suite completa di app educative open source.',
            'platform_description': 'Piattaforma di app educative open source: memorizzazione, flashcard, note, quiz e chat collaborativa.',
            'resources': 'Risorse',
            'roadmap': 'Roadmap',
            'documentation': 'Documentazione',
            'community': 'Comunità',
            'status': 'Stato',
            'report_bug': 'Segnala un bug',
            'contact_us': 'Contattaci',
            'privacy': 'Privacy',
            'terms': 'Termini',
            'cookies': 'Cookie',
            'free_trial': 'Prova gratuita di 7 giorni',
            'my_notes': 'Le Mie Note',
            'waiting_list': 'Unisciti alla lista d\'attesa',
            'go_dashboard': 'Vai alla Dashboard',
            'access_dashboard': 'Accedi alla Dashboard'
        },
        'ru': {
            'language_name': 'Russian',
            'plural_forms': 'nplurals=4; plural=(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<12 || n%100>14) ? 1 : n%10==0 || (n%10>=5 && n%10<=9) || (n%100>=11 && n%100<=14)? 2 : 3)',
            'seo_title': 'Изучайте языки с ИИ - Интерактивная платформа изучения языков',
            'seo_description': 'Овладейте новыми языками с нашей интерактивной платформой на основе ИИ. Персонализированные уроки, обратная связь в реальном времени и увлекательные упражнения для эффективного изучения языков.',
            'seo_keywords': 'изучение языков, ИИ, интерактивный, персонализированный, уроки, многоязычный, образование',
            'home': 'Главная',
            'features': 'Функции',
            'pricing': 'Цены',
            'about': 'О нас',
            'contact': 'Контакты',
            'get_started': 'Начать',
            'sign_in': 'Войти',
            'language': 'Язык',
            'hero_title': 'Овладейте языками с ИИ',
            'hero_subtitle': 'Познакомьтесь с будущим изучения языков с нашей платформой на основе ИИ. Персонализированные уроки, обратная связь в реальном времени и интерактивные упражнения, разработанные специально для вас.',
            'start_learning': 'Начать изучение сейчас',
            'watch_demo': 'Смотреть демо',
            'active_learners': 'Активные учащиеся',
            'languages_available': 'Доступные языки',
            'lessons_completed': 'Завершенные уроки',
            'success_rate': 'Уровень успеха',
            'why_choose': 'Почему выбрать нашу платформу?',
            'ai_learning': 'Обучение на основе ИИ',
            'ai_description': 'Наш продвинутый ИИ адаптируется к вашему стилю и темпу обучения, предоставляя персонализированные рекомендации и обратную связь.',
            'interactive_exercises': 'Интерактивные упражнения',
            'exercises_description': 'Участвуйте в динамичных упражнениях, включая практику речи, понимание на слух и письменные задания.',
            'progress_tracking': 'Отслеживание прогресса',
            'progress_description': 'Отслеживайте свой путь обучения с подробной аналитикой и отчетами о прогрессе, чтобы оставаться мотивированными.',
            'multi_device': 'Доступ с нескольких устройств',
            'device_description': 'Учитесь где угодно и когда угодно с бесшовной синхронизацией на всех ваших устройствах.',
            'expert_content': 'Экспертный контент',
            'expert_description': 'Учебная программа, разработанная экспертами по языкам и носителями языка для аутентичного опыта обучения.',
            'community_support': 'Поддержка сообщества',
            'community_description': 'Присоединяйтесь к яркому сообществу учащихся и получайте поддержку от однокурсников и преподавателей.',
            'choose_plan': 'Выберите ваш план',
            'plan_description': 'Начните свое путешествие изучения языков с планом, который подходит вашим потребностям.',
            'free': 'Бесплатно',
            'free_description': 'Идеально для начала',
            'basic_access': 'Доступ к базовым урокам',
            'limited_ai': 'Ограниченные функции ИИ',
            'community_support_lower': 'Поддержка сообщества',
            'start_free': 'Начать бесплатно',
            'pro': 'Про',
            'month': 'месяц',
            'pro_description': 'Лучше всего для серьезных учащихся',
            'unlimited_lessons': 'Неограниченные уроки',
            'full_ai': 'Полные функции ИИ',
            'priority_support': 'Приоритетная поддержка',
            'offline_access': 'Офлайн доступ',
            'choose_pro': 'Выбрать Про',
            'enterprise': 'Корпоративный',
            'enterprise_description': 'Для команд и организаций',
            'custom_solutions': 'Индивидуальные решения',
            'advanced_analytics': 'Расширенная аналитика',
            'dedicated_support': 'Выделенная поддержка',
            'contact_sales': 'Связаться с отделом продаж',
            'ready_start': 'Готовы начать свое путешествие изучения языков?',
            'join_thousands': 'Присоединяйтесь к тысячам учащихся, которые уже трансформировали свои языковые навыки с нашей платформой на основе ИИ.',
            'product': 'Продукт',
            'courses': 'Курсы',
            'mobile_app': 'Мобильное приложение',
            'api': 'API',
            'company': 'Компания',
            'blog': 'Блог',
            'careers': 'Карьера',
            'press': 'Пресса',
            'support': 'Поддержка',
            'help_center': 'Центр помощи',
            'privacy_policy': 'Политика конфиденциальности',
            'terms_service': 'Условия обслуживания',
            'legal': 'Юридическая информация',
            'cookie_policy': 'Политика файлов cookie',
            'all_rights': 'Все права защищены.',
            'open_source_apps': 'Образовательные приложения с открытым исходным кодом',
            'complete_suite': 'Полный набор образовательных приложений с открытым исходным кодом: запоминание, карточки, заметки, викторины, совместный чат и многое другое.',
            'start_for_free': 'Начать бесплатно',
            'discover_apps': 'Откройте наши приложения',
            'educational_apps': 'Образовательные приложения',
            'flashcards_created': 'Созданные карточки',
            'quizzes_generated': 'Сгенерированные викторины',
            'open_source': 'Открытый исходный код',
            'our_apps': 'Наши образовательные приложения',
            'apps_description': 'Откройте наш набор из 5 приложений, предназначенных для преобразования вашего опыта обучения. Выберите одно бесплатно или получите доступ ко всем с Premium.',
            'courses_description': 'Структурированные курсы с прогрессивными уроками, интерактивными упражнениями и персонализированными оценками.',
            'revision': 'Повторение',
            'revision_description': 'Система интервального повторения с умными карточками для оптимального запоминания.',
            'notebook': 'Блокнот',
            'notebook_description': 'Централизованное ведение заметок с интеллектуальной организацией и расширенным поиском.',
            'quiz': 'Викторина',
            'quiz_description': 'Адаптивная система викторин для проверки ваших знаний и выявления слабых мест.',
            'language_ai': 'Языковой ИИ',
            'ai_assistant_description': 'ИИ-помощник для естественных разговоров и интеллектуальных исправлений в реальном времени.',
            'new_apps_coming': 'Скоро новые образовательные приложения',
            'teams_working': 'Наши команды активно работают над инновационными новыми образовательными приложениями для обогащения нашей экосистемы обучения. Эти предстоящие инструменты предложат еще больше способов освоить языки.',
            'ai_writing': 'ИИ-помощник по письму',
            'pronunciation': 'Тренер произношения',
            'cultural': 'Культурное погружение',
            'grammar': 'Проверка грамматики',
            'coming_2025': 'Выйдет в 2025',
            'neuroscience': 'Освоение языка на основе нейронауки',
            'native_speakers': 'Сообщество носителей языка',
            'certifications': 'Признанные в отрасли сертификации',
            'plans_adapted': 'Планы, адаптированные к вашим потребностям',
            'choose_offer': 'Выберите предложение, которое соответствует вашим целям и темпу обучения.',
            'forever': 'навсегда',
            'perfect_discovering': 'Идеально для знакомства с платформой',
            'access_1_app': 'Доступ к 1 приложению по вашему выбору',
            'full_use': 'Полное использование выбранного приложения',
            'free_updates': 'Бесплатные обновления',
            'most_popular': 'Самый популярный',
            'per_month': 'в месяц',
            'full_access': 'Полный доступ ко всем приложениям',
            'access_all': 'Доступ ко всем приложениям',
            'structured_lessons': 'структурированные уроки',
            'unlimited_flashcards': 'неограниченные карточки',
            'unlimited_notes': 'неограниченные заметки',
            'quiz_ai_included': 'Викторина и языковой ИИ включены',
            'ready_revolutionize': 'Готовы революционизировать свое обучение?',
            'join_community': 'Присоединяйтесь к нашему сообществу и получите доступ к полному набору образовательных приложений с открытым исходным кодом.',
            'platform_description': 'Платформа образовательных приложений с открытым исходным кодом: запоминание, карточки, заметки, викторины и совместный чат.',
            'resources': 'Ресурсы',
            'roadmap': 'Дорожная карта',
            'documentation': 'Документация',
            'community': 'Сообщество',
            'status': 'Статус',
            'report_bug': 'Сообщить об ошибке',
            'contact_us': 'Свяжитесь с нами',
            'privacy': 'Конфиденциальность',
            'terms': 'Условия',
            'cookies': 'Файлы cookie',
            'free_trial': '7-дневная бесплатная пробная версия',
            'my_notes': 'Мои заметки',
            'waiting_list': 'Присоединиться к списку ожидания',
            'go_dashboard': 'Перейти к панели управления',
            'access_dashboard': 'Доступ к панели управления'
        },
        'pl': {
            'language_name': 'Polish', 
            'plural_forms': 'nplurals=4; plural=(n==1 ? 0 : (n%10>=2 && n%10<=4) && (n%100<12 || n%100>14) ? 1 : n!=1 && (n%10>=0 && n%10<=1) || (n%10>=5 && n%10<=9) || (n%100>=12 && n%100<=14) ? 2 : 3)',
            'seo_title': 'Ucz się języków z AI - Interaktywna platforma nauki języków',
            'seo_description': 'Opanuj nowe języki dzięki naszej interaktywnej platformie zasilanej AI. Spersonalizowane lekcje, informacje zwrotne w czasie rzeczywistym i angażujące ćwiczenia dla skutecznej nauki języków.',
            'seo_keywords': 'nauka języków, AI, interaktywny, spersonalizowany, lekcje, wielojęzyczny, edukacja',
            'home': 'Strona główna',
            'features': 'Funkcje',
            'pricing': 'Cennik',
            'about': 'O nas',
            'contact': 'Kontakt',
            'get_started': 'Rozpocznij',
            'sign_in': 'Zaloguj się',
            'language': 'Język',
            'hero_title': 'Opanuj języki z AI',
            'hero_subtitle': 'Doświadcz przyszłości nauki języków z naszą platformą zasilaną AI. Spersonalizowane lekcje, informacje zwrotne w czasie rzeczywistym i interaktywne ćwiczenia zaprojektowane specjalnie dla Ciebie.',
            'start_learning': 'Rozpocznij naukę teraz',
            'watch_demo': 'Zobacz demo',
            'active_learners': 'Aktywni uczniowie',
            'languages_available': 'Dostępne języki',
            'lessons_completed': 'Ukończone lekcje',
            'success_rate': 'Wskaźnik sukcesu',
            'why_choose': 'Dlaczego wybrać naszą platformę?',
            'ai_learning': 'Nauka zasilana AI',
            'ai_description': 'Nasza zaawansowana AI dostosowuje się do Twojego stylu i tempa nauki, zapewniając spersonalizowane rekomendacje i informacje zwrotne.',
            'interactive_exercises': 'Interaktywne ćwiczenia',
            'exercises_description': 'Angażuj się w dynamiczne ćwiczenia, w tym praktykę mówienia, rozumienie ze słuchu i wyzwania pisemne.',
            'progress_tracking': 'Śledzenie postępów',
            'progress_description': 'Monitoruj swoją podróż edukacyjną dzięki szczegółowej analityce i raportom postępów, aby pozostać zmotywowanym.',
            'multi_device': 'Dostęp z wielu urządzeń',
            'device_description': 'Ucz się wszędzie i o każdej porze dzięki bezproblemowej synchronizacji na wszystkich Twoich urządzeniach.',
            'expert_content': 'Treść ekspercka',
            'expert_description': 'Program nauczania opracowany przez ekspertów językowych i native speakerów dla autentycznych doświadczeń edukacyjnych.',
            'community_support': 'Wsparcie społeczności',
            'community_description': 'Dołącz do żywej społeczności uczniów i otrzymuj wsparcie od innych studentów i instruktorów.',
            'choose_plan': 'Wybierz swój plan',
            'plan_description': 'Rozpocznij swoją podróż nauki języków z planem, który odpowiada Twoim potrzebom.',
            'free': 'Darmowy',
            'free_description': 'Idealny do rozpoczęcia',
            'basic_access': 'Dostęp do podstawowych lekcji',
            'limited_ai': 'Ograniczone funkcje AI',
            'community_support_lower': 'wsparcie społeczności',
            'start_free': 'Rozpocznij za darmo',
            'pro': 'Pro',
            'month': 'miesiąc',
            'pro_description': 'Najlepsze dla poważnych uczniów',
            'unlimited_lessons': 'Nieograniczone lekcje',
            'full_ai': 'Pełne funkcje AI',
            'priority_support': 'Priorytetowe wsparcie',
            'offline_access': 'Dostęp offline',
            'choose_pro': 'Wybierz Pro',
            'enterprise': 'Enterprise',
            'enterprise_description': 'Dla zespołów i organizacji',
            'custom_solutions': 'Niestandardowe rozwiązania',
            'advanced_analytics': 'Zaawansowana analityka',
            'dedicated_support': 'Dedykowane wsparcie',
            'contact_sales': 'Skontaktuj się z działem sprzedaży',
            'ready_start': 'Gotowy, aby rozpocząć swoją podróż nauki języków?',
            'join_thousands': 'Dołącz do tysięcy uczniów, którzy już przekształcili swoje umiejętności językowe dzięki naszej platformie zasilanej AI.',
            'product': 'Produkt',
            'courses': 'Kursy',
            'mobile_app': 'Aplikacja mobilna',
            'api': 'API',
            'company': 'Firma',
            'blog': 'Blog',
            'careers': 'Kariera',
            'press': 'Prasa',
            'support': 'Wsparcie',
            'help_center': 'Centrum pomocy',
            'privacy_policy': 'Polityka prywatności',
            'terms_service': 'Warunki świadczenia usług',
            'legal': 'Informacje prawne',
            'cookie_policy': 'Polityka plików cookie',
            'all_rights': 'Wszystkie prawa zastrzeżone.',
            'open_source_apps': 'Aplikacje edukacyjne open source',
            'complete_suite': 'Kompletny zestaw aplikacji edukacyjnych open source: zapamiętywanie, fiszki, robienie notatek, quizy, czat współpracy i wiele więcej.',
            'start_for_free': 'Rozpocznij za darmo',
            'discover_apps': 'Odkryj nasze aplikacje',
            'educational_apps': 'Aplikacje edukacyjne',
            'flashcards_created': 'Utworzone fiszki',
            'quizzes_generated': 'Wygenerowane quizy',
            'open_source': 'Open source',
            'our_apps': 'Nasze aplikacje edukacyjne',
            'apps_description': 'Odkryj nasz zestaw 5 aplikacji zaprojektowanych do przekształcenia Twojego doświadczenia edukacyjnego. Wybierz jedną za darmo lub uzyskaj dostęp do wszystkich z Premium.',
            'courses_description': 'Strukturalne kursy z progresywnymi lekcjami, interaktywnymi ćwiczeniami i spersonalizowanymi ocenami.',
            'revision': 'Powtórka',
            'revision_description': 'System powtórek rozłożonych w czasie z inteligentnymi fiszkami dla optymalnego zapamiętywania.',
            'notebook': 'Notatnik',
            'notebook_description': 'Scentralizowane robienie notatek z inteligentną organizacją i zaawansowanym wyszukiwaniem.',
            'quiz': 'Quiz',
            'quiz_description': 'Adaptacyjny system quizów do testowania Twojej wiedzy i identyfikowania słabych punktów.',
            'language_ai': 'AI językowe',
            'ai_assistant_description': 'Asystent AI do naturalnych rozmów i inteligentnych poprawek w czasie rzeczywistym.',
            'new_apps_coming': 'Wkrótce nowe aplikacje edukacyjne',
            'teams_working': 'Nasze zespoły aktywnie pracują nad innowacyjnymi nowymi aplikacjami edukacyjnymi, aby wzbogacić nasz ekosystem nauki. Te nadchodzące narzędzia zaoferują jeszcze więcej sposobów na opanowanie języków.',
            'ai_writing': 'Asystent pisania AI',
            'pronunciation': 'Trener wymowy',
            'cultural': 'Zanurzenie kulturowe',
            'grammar': 'Sprawdzanie gramatyki',
            'coming_2025': 'Nadchodzi w 2025',
            'neuroscience': 'Nabywanie języka oparte na neuronaukach',
            'native_speakers': 'Społeczność native speakerów',
            'certifications': 'Certyfikaty uznane przez branżę',
            'plans_adapted': 'Plany dostosowane do Twoich potrzeb',
            'choose_offer': 'Wybierz ofertę, która odpowiada Twoim celom i tempie nauki.',
            'forever': 'na zawsze',
            'perfect_discovering': 'Idealny do odkrywania platformy',
            'access_1_app': 'Dostęp do 1 aplikacji do wyboru',
            'full_use': 'Pełne korzystanie z wybranej aplikacji',
            'free_updates': 'Darmowe aktualizacje',
            'most_popular': 'Najpopularniejszy',
            'per_month': 'miesięcznie',
            'full_access': 'Pełny dostęp do wszystkich aplikacji',
            'access_all': 'Dostęp do wszystkich aplikacji',
            'structured_lessons': 'strukturalne lekcje',
            'unlimited_flashcards': 'nieograniczone fiszki',
            'unlimited_notes': 'nieograniczone notatki',
            'quiz_ai_included': 'Quiz i AI językowe w zestawie',
            'ready_revolutionize': 'Gotowy zrewolucjonizować swoją naukę?',
            'join_community': 'Dołącz do naszej społeczności i uzyskaj dostęp do kompletnego zestawu aplikacji edukacyjnych open source.',
            'platform_description': 'Platforma aplikacji edukacyjnych open source: zapamiętywanie, fiszki, notatki, quizy i czat współpracy.',
            'resources': 'Zasoby',
            'roadmap': 'Mapa drogowa',
            'documentation': 'Dokumentacja',
            'community': 'Społeczność',
            'status': 'Status',
            'report_bug': 'Zgłoś błąd',
            'contact_us': 'Skontaktuj się z nami',
            'privacy': 'Prywatność',
            'terms': 'Warunki',
            'cookies': 'Pliki cookie',
            'free_trial': '7-dniowa darmowa wersja próbna',
            'my_notes': 'Moje notatki',
            'waiting_list': 'Dołącz do listy oczekujących',
            'go_dashboard': 'Idź do panelu',
            'access_dashboard': 'Dostęp do panelu'
        },
        'sv': {
            'language_name': 'Swedish',
            'plural_forms': 'nplurals=2; plural=(n != 1)',
            'seo_title': 'Lär dig språk med AI - Interaktiv språkinlärningsplattform',
            'seo_description': 'Bemästra nya språk med vår AI-drivna interaktiva plattform. Personaliserade lektioner, realtidsfeedback och engagerande övningar för effektiv språkinlärning.',
            'seo_keywords': 'språkinlärning, AI, interaktiv, personaliserad, lektioner, flerspråkig, utbildning',
            'home': 'Hem',
            'features': 'Funktioner',
            'pricing': 'Prissättning',
            'about': 'Om oss',
            'contact': 'Kontakt',
            'get_started': 'Kom igång',
            'sign_in': 'Logga in',
            'language': 'Språk',
            'hero_title': 'Bemästra språk med AI',
            'hero_subtitle': 'Upplev framtiden för språkinlärning med vår AI-drivna plattform. Personaliserade lektioner, realtidsfeedback och interaktiva övningar designade just för dig.',
            'start_learning': 'Börja lära nu',
            'watch_demo': 'Se demo',
            'active_learners': 'Aktiva elever',
            'languages_available': 'Tillgängliga språk',
            'lessons_completed': 'Slutförda lektioner',
            'success_rate': 'Framgångsgrad',
            'why_choose': 'Varför välja vår plattform?',
            'ai_learning': 'AI-driven inlärning',
            'ai_description': 'Vår avancerade AI anpassar sig till din inlärningsstil och takt, och ger personaliserade rekommendationer och feedback.',
            'interactive_exercises': 'Interaktiva övningar',
            'exercises_description': 'Delta i dynamiska övningar inklusive talövning, hörförståelse och skrivutmaningar.',
            'progress_tracking': 'Framstegsspårning',
            'progress_description': 'Övervaka din inlärningsresa med detaljerad analys och framstegsrapporter för att hålla dig motiverad.',
            'multi_device': 'Flerdenhetsåtkomst',
            'device_description': 'Lär dig var som helst, när som helst med sömlös synkronisering över alla dina enheter.',
            'expert_content': 'Expertinnehåll',
            'expert_description': 'Kursplan utformad av språkexperter och modersmålstalare för autentiska inlärningsupplevelser.',
            'community_support': 'Gemenskapsstöd',
            'community_description': 'Gå med i en livlig gemenskap av elever och få stöd från medstudenter och instruktörer.',
            'choose_plan': 'Välj din plan',
            'plan_description': 'Börja din språkinlärningsresa med planen som passar dina behov.',
            'free': 'Gratis',
            'free_description': 'Perfekt för att komma igång',
            'basic_access': 'Tillgång till grundläggande lektioner',
            'limited_ai': 'Begränsade AI-funktioner',
            'community_support_lower': 'gemenskapsstöd',
            'start_free': 'Börja gratis',
            'pro': 'Pro',
            'month': 'månad',
            'pro_description': 'Bäst för seriösa elever',
            'unlimited_lessons': 'Obegränsade lektioner',
            'full_ai': 'Fullständiga AI-funktioner',
            'priority_support': 'Prioriterat stöd',
            'offline_access': 'Offline-tillgång',
            'choose_pro': 'Välj Pro',
            'enterprise': 'Företag',
            'enterprise_description': 'För team och organisationer',
            'custom_solutions': 'Anpassade lösningar',
            'advanced_analytics': 'Avancerad analys',
            'dedicated_support': 'Dedikerat stöd',
            'contact_sales': 'Kontakta försäljning',
            'ready_start': 'Redo att börja din språkinlärningsresa?',
            'join_thousands': 'Gå med tusentals elever som redan har transformerat sina språkfärdigheter med vår AI-drivna plattform.',
            'product': 'Produkt',
            'courses': 'Kurser',
            'mobile_app': 'Mobilapp',
            'api': 'API',
            'company': 'Företag',
            'blog': 'Blogg',
            'careers': 'Karriärer',
            'press': 'Press',
            'support': 'Stöd',
            'help_center': 'Hjälpcenter',
            'privacy_policy': 'Integritetspolicy',
            'terms_service': 'Användarvillkor',
            'legal': 'Juridisk',
            'cookie_policy': 'Cookie-policy',
            'all_rights': 'Alla rättigheter förbehållna.',
            'open_source_apps': 'Open source utbildningsappar',
            'complete_suite': 'En komplett uppsättning open source utbildningsappar: memorering, flashkort, anteckningar, quiz, samarbetschatt och mycket mer.',
            'start_for_free': 'Börja gratis',
            'discover_apps': 'Upptäck våra appar',
            'educational_apps': 'Utbildningsappar',
            'flashcards_created': 'Skapade flashkort',
            'quizzes_generated': 'Genererade quiz',
            'open_source': 'Open source',
            'our_apps': 'Våra utbildningsappar',
            'apps_description': 'Upptäck vår uppsättning av 5 appar designade för att transformera din inlärningsupplevelse. Välj en gratis eller få tillgång till alla med Premium.',
            'courses_description': 'Strukturerade kurser med progressiva lektioner, interaktiva övningar och personaliserade bedömningar.',
            'revision': 'Revision',
            'revision_description': 'Spaced repetition-system med smarta flashkort för optimal memorering.',
            'notebook': 'Anteckningsbok',
            'notebook_description': 'Centraliserad anteckningstagning med intelligent organisation och avancerad sökning.',
            'quiz': 'Quiz',
            'quiz_description': 'Adaptivt quizsystem för att testa dina kunskaper och identifiera svaga punkter.',
            'language_ai': 'Språk-AI',
            'ai_assistant_description': 'AI-assistent för naturliga konversationer och intelligenta realtidskorrigeringar.',
            'new_apps_coming': 'Nya utbildningsappar kommer snart',
            'teams_working': 'Våra team arbetar aktivt med innovativa nya utbildningsappar för att berika vårt inlärningsekosystem. Dessa kommande verktyg kommer att erbjuda ännu fler sätt att bemästra språk.',
            'ai_writing': 'AI-skrivassistent',
            'pronunciation': 'Uttalstränare',
            'cultural': 'Kulturell fördjupning',
            'grammar': 'Grammatikkontroll',
            'coming_2025': 'Kommer 2025',
            'neuroscience': 'Neurovetenskap-baserad språktillägnelse',
            'native_speakers': 'Modersmålstalar-gemenskap',
            'certifications': 'Branscherkända certifieringar',
            'plans_adapted': 'Planer anpassade till dina behov',
            'choose_offer': 'Välj erbjudandet som matchar dina mål och inlärningstakt.',
            'forever': 'för alltid',
            'perfect_discovering': 'Perfekt för att upptäcka plattformen',
            'access_1_app': 'Tillgång till 1 app av ditt val',
            'full_use': 'Full användning av den valda appen',
            'free_updates': 'Gratis uppdateringar',
            'most_popular': 'Mest populär',
            'per_month': 'per månad',
            'full_access': 'Full tillgång till alla applikationer',
            'access_all': 'Tillgång till alla applikationer',
            'structured_lessons': 'strukturerade lektioner',
            'unlimited_flashcards': 'obegränsade flashkort',
            'unlimited_notes': 'obegränsade anteckningar',
            'quiz_ai_included': 'Quiz och språk-AI inkluderat',
            'ready_revolutionize': 'Redo att revolutionera din inlärning?',
            'join_community': 'Gå med i vår gemenskap och få tillgång till en komplett uppsättning open source utbildningsappar.',
            'platform_description': 'Open source utbildningsappsplattform: memorering, flashkort, anteckningar, quiz och samarbetschatt.',
            'resources': 'Resurser',
            'roadmap': 'Färdplan',
            'documentation': 'Dokumentation',
            'community': 'Gemenskap',
            'status': 'Status',
            'report_bug': 'Rapportera en bugg',
            'contact_us': 'Kontakta oss',
            'privacy': 'Integritet',
            'terms': 'Villkor',
            'cookies': 'Cookies',
            'free_trial': '7-dagars gratis testversion',
            'my_notes': 'Mina anteckningar',
            'waiting_list': 'Gå med i väntelistan',
            'go_dashboard': 'Gå till instrumentpanel',
            'access_dashboard': 'Tillgång till instrumentpanel'
        },
        'uk': {
            'language_name': 'Ukrainian',
            'plural_forms': 'nplurals=4; plural=(n % 1 == 0 && n % 10 == 1 && n % 100 != 11 ? 0 : n % 1 == 0 && n % 10 >= 2 && n % 10 <= 4 && (n % 100 < 12 || n % 100 > 14) ? 1 : n % 1 == 0 && (n % 10 ==0 || (n % 10 >=5 && n % 10 <=9) || (n % 100 >=11 && n % 100 <=14 )) ? 2: 3)',
            'seo_title': 'Вивчайте мови з ШІ - Інтерактивна платформа вивчення мов',
            'seo_description': 'Опануйте нові мови з нашою інтерактивною платформою на основі ШІ. Персоналізовані уроки, зворотний зв\'язок у реальному часі та захоплюючі вправи для ефективного вивчення мов.',
            'seo_keywords': 'вивчення мов, ШІ, інтерактивний, персоналізований, уроки, багатомовний, освіта',
            'home': 'Головна',
            'features': 'Функції',
            'pricing': 'Ціни',
            'about': 'Про нас',
            'contact': 'Контакти',
            'get_started': 'Почати',
            'sign_in': 'Увійти',
            'language': 'Мова',
            'hero_title': 'Опануйте мови з ШІ',
            'hero_subtitle': 'Відчуйте майбутнє вивчення мов з нашою платформою на основі ШІ. Персоналізовані уроки, зворотний зв\'язок у реальному часі та інтерактивні вправи, розроблені спеціально для вас.',
            'start_learning': 'Почати вивчення зараз',
            'watch_demo': 'Дивитися демо',
            'active_learners': 'Активні учні',
            'languages_available': 'Доступні мови',
            'lessons_completed': 'Завершені уроки',
            'success_rate': 'Рівень успіху',
            'why_choose': 'Чому обрати нашу платформу?',
            'ai_learning': 'Навчання на основі ШІ',
            'ai_description': 'Наш передовий ШІ адаптується до вашого стилю та темпу навчання, надаючи персоналізовані рекомендації та зворотний зв\'язок.',
            'interactive_exercises': 'Інтерактивні вправи',
            'exercises_description': 'Берите участь у динамічних вправах, включаючи практику мовлення, розуміння на слух та письмові завдання.',
            'progress_tracking': 'Відстеження прогресу',
            'progress_description': 'Відстежуйте свою навчальну подорож з детальною аналітикою та звітами про прогрес, щоб залишатися мотивованими.',
            'multi_device': 'Доступ з кількох пристроїв',
            'device_description': 'Вчіться де завгодно та коли завгодно з безшовною синхронізацією на всіх ваших пристроях.',
            'expert_content': 'Експертний контент',
            'expert_description': 'Навчальна програма, розроблена експертами мов та носіями мови для автентичного навчального досвіду.',
            'community_support': 'Підтримка спільноти',
            'community_description': 'Приєднуйтесь до яскравої спільноти учнів та отримуйте підтримку від однокурсників та інструкторів.',
            'choose_plan': 'Оберіть ваш план',
            'plan_description': 'Почніть свою подорож вивчення мов з планом, який відповідає вашим потребам.',
            'free': 'Безкоштовно',
            'free_description': 'Ідеально для початку',
            'basic_access': 'Доступ до базових уроків',
            'limited_ai': 'Обмежені функції ШІ',
            'community_support_lower': 'підтримка спільноти',
            'start_free': 'Почати безкоштовно',
            'pro': 'Про',
            'month': 'місяць',
            'pro_description': 'Найкраще для серйозних учнів',
            'unlimited_lessons': 'Необмежені уроки',
            'full_ai': 'Повні функції ШІ',
            'priority_support': 'Пріоритетна підтримка',
            'offline_access': 'Офлайн доступ',
            'choose_pro': 'Обрати Про',
            'enterprise': 'Корпоративний',
            'enterprise_description': 'Для команд та організацій',
            'custom_solutions': 'Індивідуальні рішення',
            'advanced_analytics': 'Розширена аналітика',
            'dedicated_support': 'Виділена підтримка',
            'contact_sales': 'Зв\'язатися з відділом продажів',
            'ready_start': 'Готові почати свою подорож вивчення мов?',
            'join_thousands': 'Приєднуйтесь до тисяч учнів, які вже трансформували свої мовні навички з нашою платформою на основі ШІ.',
            'product': 'Продукт',
            'courses': 'Курси',
            'mobile_app': 'Мобільний додаток',
            'api': 'API',
            'company': 'Компанія',
            'blog': 'Блог',
            'careers': 'Кар\'єра',
            'press': 'Преса',
            'support': 'Підтримка',
            'help_center': 'Центр допомоги',
            'privacy_policy': 'Політика конфіденційності',
            'terms_service': 'Умови надання послуг',
            'legal': 'Правова інформація',
            'cookie_policy': 'Політика файлів cookie',
            'all_rights': 'Всі права захищені.',
            'open_source_apps': 'Освітні додатки з відкритим кодом',
            'complete_suite': 'Повний набір освітніх додатків з відкритим кодом: запам\'ятовування, картки, нотатки, вікторини, спільний чат та багато іншого.',
            'start_for_free': 'Почати безкоштовно',
            'discover_apps': 'Відкрийте наші додатки',
            'educational_apps': 'Освітні додатки',
            'flashcards_created': 'Створені картки',
            'quizzes_generated': 'Згенеровані вікторини',
            'open_source': 'Відкритий код',
            'our_apps': 'Наші освітні додатки',
            'apps_description': 'Відкрийте наш набір з 5 додатків, призначених для трансформації вашого навчального досвіду. Оберіть один безкоштовно або отримайте доступ до всіх з Premium.',
            'courses_description': 'Структуровані курси з прогресивними уроками, інтерактивними вправами та персоналізованими оцінками.',
            'revision': 'Повторення',
            'revision_description': 'Система інтервального повторення з розумними картками для оптимального запам\'ятовування.',
            'notebook': 'Записник',
            'notebook_description': 'Централізоване ведення нотаток з інтелектуальною організацією та розширеним пошуком.',
            'quiz': 'Вікторина',
            'quiz_description': 'Адаптивна система вікторин для перевірки ваших знань та виявлення слабких місць.',
            'language_ai': 'Мовний ШІ',
            'ai_assistant_description': 'ШІ-помічник для природних розмов та інтелектуальних виправлень у реальному часі.',
            'new_apps_coming': 'Незабаром нові освітні додатки',
            'teams_working': 'Наші команди активно працюють над інноваційними новими освітніми додатками для збагачення нашої навчальної екосистеми. Ці майбутні інструменти запропонують ще більше способів опанувати мови.',
            'ai_writing': 'ШІ-помічник з письма',
            'pronunciation': 'Тренер вимови',
            'cultural': 'Культурне занурення',
            'grammar': 'Перевірка граматики',
            'coming_2025': 'Вийде у 2025',
            'neuroscience': 'Засвоєння мови на основі нейронауки',
            'native_speakers': 'Спільнота носіїв мови',
            'certifications': 'Визнані в галузі сертифікації',
            'plans_adapted': 'Плани, адаптовані до ваших потреб',
            'choose_offer': 'Оберіть пропозицію, яка відповідає вашим цілям та темпу навчання.',
            'forever': 'назавжди',
            'perfect_discovering': 'Ідеально для знайомства з платформою',
            'access_1_app': 'Доступ до 1 додатку на ваш вибір',
            'full_use': 'Повне використання обраного додатку',
            'free_updates': 'Безкоштовні оновлення',
            'most_popular': 'Найпопулярніший',
            'per_month': 'на місяць',
            'full_access': 'Повний доступ до всіх додатків',
            'access_all': 'Доступ до всіх додатків',
            'structured_lessons': 'структуровані уроки',
            'unlimited_flashcards': 'необмежені картки',
            'unlimited_notes': 'необмежені нотатки',
            'quiz_ai_included': 'Вікторина та мовний ШІ включені',
            'ready_revolutionize': 'Готові революціонізувати своє навчання?',
            'join_community': 'Приєднуйтесь до нашої спільноти та отримайте доступ до повного набору освітніх додатків з відкритим кодом.',
            'platform_description': 'Платформа освітніх додатків з відкритим кодом: запам\'ятовування, картки, нотатки, вікторини та спільний чат.',
            'resources': 'Ресурси',
            'roadmap': 'Дорожна карта',
            'documentation': 'Документація',
            'community': 'Спільнота',
            'status': 'Статус',
            'report_bug': 'Повідомити про помилку',
            'contact_us': 'Зв\'яжіться з нами',
            'privacy': 'Конфіденційність',
            'terms': 'Умови',
            'cookies': 'Файли cookie',
            'free_trial': '7-денна безкоштовна пробна версія',
            'my_notes': 'Мої нотатки',
            'waiting_list': 'Приєднатися до списку очікування',
            'go_dashboard': 'Перейти до панелі управління',
            'access_dashboard': 'Доступ до панелі управління'
        }
    }

def complete_language_file(lang_code, lang_data):
    """Complete a language file with all translations"""
    
    template = get_complete_translation_template()
    
    # Replace all placeholders in the template
    completed_content = template.format(
        lang_code=lang_code,
        **lang_data
    )
    
    # Path to the .po file
    po_file_path = f'/mnt/c/Users/louis/WebstormProjects/linguify/backend/public_web/i18n/{lang_code}/LC_MESSAGES/django.po'
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(po_file_path), exist_ok=True)
    
    # Write the completed translation file
    with open(po_file_path, 'w', encoding='utf-8') as f:
        f.write(completed_content)
    
    print(f"✅ Completed translation for {lang_code}: {lang_data['language_name']}")
    
    return True

def main():
    """Complete all missing language translations"""
    
    print("🌍 Completing all missing language translations...")
    print("=" * 60)
    
    languages = get_language_translations()
    
    completed_count = 0
    
    for lang_code, lang_data in languages.items():
        try:
            complete_language_file(lang_code, lang_data)
            completed_count += 1
        except Exception as e:
            print(f"❌ Error completing {lang_code}: {e}")
    
    print(f"\n📊 Results:")
    print(f"  ✅ Completed: {completed_count}/{len(languages)} languages")
    
    if completed_count > 0:
        print(f"\n🎉 Translation completion finished!")
        print(f"📋 Next steps:")
        print(f"  1. Run: python3 compile_translations_manual.py")
        print(f"  2. Restart Django server")
        print(f"  3. Test all languages!")
    
    return completed_count > 0

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✨ All languages are now complete! Run the compilation script next.")
    else:
        print("\n💡 Check for any errors above.")