from django.urls import path, include
from . import views

app_name = 'public_web'

urlpatterns = [
    # Landing et pages principales
    path('', views.LandingView.as_view(), name='landing'),
    # SEO aliases for brand variations
    path('openlinguify/', views.LandingView.as_view(), name='openlinguify'),
    path('features/', views.FeaturesView.as_view(), name='features'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('blog/', views.BlogView.as_view(), name='blog'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    
    # Pages légales
    path('privacy/', views.PrivacyView.as_view(), name='privacy'),
    path('terms/', views.TermsView.as_view(), name='terms'),
    path('cookies/', views.CookiesView.as_view(), name='cookies'),
    
    # Annexes (legacy URLs for SEO) - redirect to legal/
    path('annexes/terms/', views.TermsView.as_view(), name='annexes_terms'),
    path('annexes/privacy/', views.PrivacyView.as_view(), name='annexes_privacy'),
    path('annexes/cookies/', views.CookiesView.as_view(), name='annexes_cookies'),
    
    # Legal pages (current structure)
    path('legal/terms/', views.TermsView.as_view(), name='legal_terms'),
    path('legal/privacy/', views.PrivacyView.as_view(), name='legal_privacy'),
    path('legal/cookies/', views.CookiesView.as_view(), name='legal_cookies'),
    
    # SEO brand page
    path('brand/', views.BrandView.as_view(), name='brand'),
    
    # Présentation des applications (legacy)
    path('apps/', views.DynamicAppsListView.as_view(), name='apps'),
    path('apps/courses/', views.AppCoursesView.as_view(), name='app_courses'),
    path('apps/revision/', views.AppRevisionView.as_view(), name='app_revision'),
    path('apps/notebook/', views.AppNotebookView.as_view(), name='app_notebook'),
    path('apps/quizz/', views.AppQuizzView.as_view(), name='app_quizz'),
    path('apps/language-ai/', views.AppLanguageAIView.as_view(), name='app_language_ai'),
    
    # Dynamic app routes (new system)
    path('apps/<str:app_slug>/', views.DynamicAppDetailView.as_view(), name='dynamic_app_detail'),
    
    # SEO Files
    path('robots.txt', views.RobotsTxtView.as_view(), name='robots_txt'),
    path('sitemap.xml', views.SitemapXmlView.as_view(), name='sitemap_xml'),
]