'use client';

import React, { useState, useEffect } from "react";
import { TermsAccordion } from '@/components/terms';
import { AvailableLocale } from '@/components/terms/termsContent';

export default function TermsAndConditions() {
  const [currentLocale, setCurrentLocale] = useState<AvailableLocale>('fr');

  // Traductions pour les titres et descriptions
  const translations = {
    fr: {
      title: "Conditions Générales d'Utilisation",
      description: "Veuillez lire attentivement ces conditions générales d'utilisation régissant votre utilisation de Linguify, notre plateforme d'apprentissage de langues.",
      help: "Besoin d'aide?",
      helpText: "Si vous avez des questions concernant nos conditions générales d'utilisation, n'hésitez pas à nous contacter.",
      contact: "Contactez-nous"
    },
    en: {
      title: "Terms and Conditions",
      description: "Please carefully read these terms and conditions governing your use of Linguify, our language learning platform.",
      help: "Need help?",
      helpText: "If you have any questions regarding our terms and conditions, please don't hesitate to contact us.",
      contact: "Contact us"
    },
    es: {
      title: "Términos y Condiciones",
      description: "Por favor, lea detenidamente estos términos y condiciones que rigen su uso de Linguify, nuestra plataforma de aprendizaje de idiomas.",
      help: "¿Necesita ayuda?",
      helpText: "Si tiene alguna pregunta sobre nuestros términos y condiciones, no dude en contactarnos.",
      contact: "Contáctenos"
    },
    nl: {
      title: "Algemene Voorwaarden",
      description: "Lees deze algemene voorwaarden zorgvuldig door die uw gebruik van Linguify, ons taalplatform, regelen.",
      help: "Hulp nodig?",
      helpText: "Als u vragen heeft over onze algemene voorwaarden, aarzel dan niet om contact met ons op te nemen.",
      contact: "Neem contact op"
    }
  };

  // Load language from localStorage on startup
  useEffect(() => {
    const savedLanguage = localStorage.getItem('language');
    if (savedLanguage && ['fr', 'en', 'es', 'nl'].includes(savedLanguage)) {
      setCurrentLocale(savedLanguage as AvailableLocale);
    }
  }, []);

  // Listen for language changes from other components
  useEffect(() => {
    const handleLanguageChange = () => {
      const savedLanguage = localStorage.getItem('language');
      if (savedLanguage && ['fr', 'en', 'es', 'nl'].includes(savedLanguage)) {
        setCurrentLocale(savedLanguage as AvailableLocale);
      }
    };

    window.addEventListener('languageChanged', handleLanguageChange);

    return () => {
      window.removeEventListener('languageChanged', handleLanguageChange);
    };
  }, []);

  // Get current translation
  const t = translations[currentLocale] || translations.fr;

  return (
    <div className="py-10 px-4 md:px-6 max-w-5xl mx-auto">
      <div className="text-center mb-10">
        <h1 className="text-3xl font-bold text-primary mb-4">{t.title}</h1>
        <p className="text-muted-foreground max-w-3xl mx-auto">
          {t.description}
        </p>
      </div>

      <TermsAccordion
        showAcceptButton={false}
        defaultValue="item-1"
        locale={currentLocale}
      />

      <div className="mt-10 p-6 border rounded-lg bg-slate-50">
        <h2 className="text-xl font-semibold mb-4">{t.help}</h2>
        <p className="mb-4">
          {t.helpText}
        </p>
        <p className="flex flex-col sm:flex-row sm:space-x-4">
          <a href="mailto:support@linguify.com" className="text-primary hover:underline mb-2 sm:mb-0">
            support@linguify.com
          </a>
          <span className="hidden sm:inline text-slate-300">|</span>
          <a href="/contact" className="text-primary hover:underline">
            {t.contact}
          </a>
        </p>
      </div>
    </div>
  );
}