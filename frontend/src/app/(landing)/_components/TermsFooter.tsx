'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { Info } from 'lucide-react';
import { TermsModal, TermsSummaryDrawer } from '@/components/terms';
import { AvailableLocale, getTermsSections, getTermsKeyPoints, CURRENT_TERMS_VERSION } from '@/components/terms/termsContent';

// Import translations
import enTranslations from '@/core/i18n/translations/en/footer.json';
import esTranslations from '@/core/i18n/translations/es/footer.json';
import frTranslations from '@/core/i18n/translations/fr/footer.json';
import nlTranslations from '@/core/i18n/translations/nl/footer.json';

// Translation types
type TranslationType = {
  terms: {
    title: string;
    legalNotice: string;
    privacyPolicy: string;
    termsOfService: string;
    contact: string;
    disclaimer: string;
  };
  copyright: {
    rights: string;
  };
};

export default function TermsFooter() {
  const [isTermsModalOpen, setIsTermsModalOpen] = useState(false);
  const [isPrivacyModalOpen, setIsPrivacyModalOpen] = useState(false);
  const [currentLocale, setCurrentLocale] = useState<AvailableLocale>('fr');
  
  const currentYear = new Date().getFullYear();
  
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

  // Translation helper function
  const getTranslation = (locale: AvailableLocale): TranslationType => {
    const translations: Record<AvailableLocale, any> = {
      fr: frTranslations.fr,
      en: enTranslations.en,
      es: esTranslations.es,
      nl: nlTranslations.nl
    };
    
    return translations[locale] || translations.en;
  };

  // Get current translation
  const t = getTranslation(currentLocale);
  
  // Initialize terms translations
  const termsTranslations = {
    fr: {
      title: "Termes et Conditions",
      legalNotice: "Mentions Légales",
      privacyPolicy: "Politique de Confidentialité",
      termsOfService: "Conditions d'Utilisation",
      contact: "Contact",
      disclaimer: "Linguify est une plateforme d'apprentissage des langues créée par GPI Software. En utilisant ce site, vous acceptez nos conditions générales d'utilisation et notre politique de confidentialité."
    },
    en: {
      title: "Terms and Conditions",
      legalNotice: "Legal Notice",
      privacyPolicy: "Privacy Policy",
      termsOfService: "Terms of Service",
      contact: "Contact",
      disclaimer: "Linguify is a language learning platform created by GPI Software. By using this site, you accept our terms and conditions and our privacy policy."
    },
    es: {
      title: "Términos y Condiciones",
      legalNotice: "Aviso Legal",
      privacyPolicy: "Política de Privacidad",
      termsOfService: "Condiciones de Servicio",
      contact: "Contacto",
      disclaimer: "Linguify es una plataforma de aprendizaje de idiomas creada por GPI Software. Al usar este sitio, acepta nuestros términos y condiciones y nuestra política de privacidad."
    },
    nl: {
      title: "Algemene Voorwaarden",
      legalNotice: "Juridische Kennisgeving",
      privacyPolicy: "Privacybeleid",
      termsOfService: "Gebruiksvoorwaarden",
      contact: "Contact",
      disclaimer: "Linguify is een taalplatform gemaakt door GPI Software. Door gebruik te maken van deze site accepteert u onze algemene voorwaarden en ons privacybeleid."
    }
  };
  
  // Get current terms translations
  const terms = termsTranslations[currentLocale] || termsTranslations.fr;
  
  return (
    <footer className="bg-slate-900 text-slate-300 py-6 mt-auto">
      <div className="container mx-auto px-4">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="mb-4 md:mb-0">
            <p className="text-sm">&copy; {currentYear} Linguify. {t.copyright?.rights || `Tous droits réservés.`}</p>
          </div>
          
          <nav className="flex flex-wrap gap-x-6 gap-y-2 justify-center text-sm">
            <TermsSummaryDrawer
              showAcceptButton={false}
              version={CURRENT_TERMS_VERSION}
              locale={currentLocale}
            >
              <span className="hover:text-white cursor-pointer transition-colors">
                {terms.termsOfService}
              </span>
            </TermsSummaryDrawer>
            
            <Link href="/annexes/legal" className="hover:text-white transition-colors">
              {terms.legalNotice}
            </Link>
            
            <button 
              onClick={() => setIsPrivacyModalOpen(true)}
              className="hover:text-white transition-colors text-left"
            >
              {terms.privacyPolicy}
            </button>
            
            <Link href="/contact" className="hover:text-white transition-colors">
              {terms.contact}
            </Link>
          </nav>
        </div>
        
        <div className="flex items-start gap-2 mt-6 max-w-2xl mx-auto text-xs text-slate-400">
          <Info className="h-4 w-4 flex-shrink-0 mt-0.5" />
          <p>
            {terms.disclaimer}
          </p>
        </div>
      </div>
      
      <TermsModal
        isOpen={isTermsModalOpen}
        onClose={() => setIsTermsModalOpen(false)}
        onAccept={() => setIsTermsModalOpen(false)}
        showAcceptance={false}
        standalone={true}
        version={CURRENT_TERMS_VERSION}
        locale={currentLocale}
      />

      {/* Placeholder pour la future fenêtre de politique de confidentialité */}
      <TermsModal
        isOpen={isPrivacyModalOpen}
        onClose={() => setIsPrivacyModalOpen(false)}
        onAccept={() => setIsPrivacyModalOpen(false)}
        showAcceptance={false}
        standalone={true}
        version={CURRENT_TERMS_VERSION}
        locale={currentLocale}
      />
    </footer>
  );
}