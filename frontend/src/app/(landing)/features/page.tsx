// src/app/(landing)/features/page.tsx
'use client';

// Importation de toutes les traductions
import frTranslations from '@/locales/fr/common.json';
import enTranslations from '@/locales/en/common.json';
import esTranslations from '@/locales/es/common.json';
import nlTranslations from '@/locales/nl/common.json';
import { useEffect, useState } from 'react';

// Définir un type pour les traductions
type TranslationType = typeof frTranslations;
type AvailableLocales = 'fr' | 'en' | 'es' | 'nl';

export default function Features() {
    // État local pour la langue (avec type restrictif)
    const [locale, setLocale] = useState<AvailableLocales>('fr');

    // Écouter les changements de langue
    useEffect(() => {
        // Fonction pour mettre à jour la langue
        const handleLanguageChange = () => {
            const savedLanguage = localStorage.getItem('language');
            console.log('Language changed to:', savedLanguage);
            if (savedLanguage && isValidLocale(savedLanguage)) {
                setLocale(savedLanguage as AvailableLocales);
            }
        };

        // Vérifier au chargement
        const savedLanguage = localStorage.getItem('language');
        if (savedLanguage && isValidLocale(savedLanguage)) {
            setLocale(savedLanguage as AvailableLocales);
        }

        // Écouter les changements futurs
        window.addEventListener('languageChanged', handleLanguageChange);
        
        // Nettoyage
        return () => {
            window.removeEventListener('languageChanged', handleLanguageChange);
        };
    }, []);

    // Helper function to check if a string is a valid locale
    function isValidLocale(locale: string): locale is AvailableLocales {
        return ['fr', 'en', 'es', 'nl'].includes(locale);
    }

    // Traductions disponibles
    const translations: Record<AvailableLocales, TranslationType> = {
        fr: frTranslations,
        en: enTranslations,
        es: esTranslations,
        nl: nlTranslations
    };

    console.log('Current locale:', locale);
    console.log('Available translations:', Object.keys(translations));
    
    // Fonction de traduction
    const t = (key: string) => {
        try {
            const keys = key.split('.');
            
            // S'assurer que la locale existe, sinon utiliser le français
            const currentTranslation = translations[locale] || translations['fr'];
            
            let value: any = currentTranslation;
            for (const k of keys) {
                if (!value || typeof value !== 'object') {
                    console.warn(`Translation key not found: ${key} (stopped at ${k})`);
                    return key;
                }
                value = value[k];
            }
            
            return typeof value === 'string' ? value : key;
        } catch (error) {
            console.error('Translation error:', error);
            return key;
        }
    };
    
    const features = [
        {
            title: t("learning.title"),
            description: t("learning.description"),
            image: "/img/feature1.png",
        },
        {
            title: t("flashcards.title"),
            description: t("flashcards.description"),
            image: "/img/feature2.png",
        },
        {
            title: t("notebook.title"),
            description: t("notebook.description"),
            image: "/img/feature3.png",
        },
        {
            title: t("community.title"),
            description: t("community.description"),
            image: "/img/feature4.png",
        },
        {
            title: t("chat.title"),
            description: t("chat.description"),
            image: "/img/feature5.png",
        },
        {
            title: t("coaching.title"),
            description: t("coaching.description"),
            image: "/img/feature6.png",
        },
    ];

    const onClick = (feature: { title: string; description: string; image: string }) => {
        console.log("Feature clicked:", feature.title);
    };

    return (
        <div className="features-container">
            <div className="features-header">
                <p>{t("header")}</p>
                {/* Afficher la langue actuelle pour débogage */}
                <p className="text-sm text-gray-500">Langue: {locale}</p>
            </div>
            <div className="features-grid">
                {features.map((feature) => (
                    <div 
                        key={feature.title} 
                        className="feature-card"
                        onClick={() => onClick(feature)}
                    >
                        <h3>{feature.title}</h3>
                        <p>{feature.description}</p>
                        <img src={feature.image} alt={feature.title} />
                    </div>
                ))}
            </div>
        </div>
    );
}