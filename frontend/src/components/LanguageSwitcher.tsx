// components/LanguageSwitcher.tsx
'use client';
import { useState, useEffect } from 'react';
import { setLocale } from '@/hooks/useTranslations';

// Liste simplifiée des langues disponibles
const languages = [
  { code: 'fr', name: 'Français', flag: '🇫🇷' },
  { code: 'en', name: 'English', flag: '🇬🇧' },
  { code: 'es', name: 'Español', flag: '🇪🇸' },
  { code: 'de', name: 'Deutsch', flag: '🇩🇪' },
  { code: 'it', name: 'Italiano', flag: '🇮🇹' },
];

export default function LanguageSwitcher() {
  // État local pour la langue actuelle
  const [currentLocale, setCurrentLocale] = useState('fr');
  
  // Mettre à jour l'état local quand la langue change globalement
  useEffect(() => {
    const handleLocaleChange = () => {
      // Ici on pourrait récupérer la langue globale d'une autre manière si nécessaire
    };
    window.addEventListener('localeChange', handleLocaleChange);
    return () => window.removeEventListener('localeChange', handleLocaleChange);
  }, []);
  
  return (
    <div className="language-switcher">
      <select
        value={currentLocale}
        onChange={(e) => {
          const newLocale = e.target.value;
          setCurrentLocale(newLocale);
          setLocale(newLocale);
        }}
        className="lang-select"
      >
        {languages.map((lang) => (
          <option key={lang.code} value={lang.code}>
            {lang.flag} {lang.name}
          </option>
        ))}
      </select>
    </div>
  );
}