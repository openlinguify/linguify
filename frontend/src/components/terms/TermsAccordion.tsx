'use client';

import React, { useState, useEffect } from 'react';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { Printer, Download } from 'lucide-react';
import { AvailableLocale, CURRENT_TERMS_VERSION } from './termsContent';

// Import translations
import enTranslations from '@/core/i18n/translations/en/terms.json';
import esTranslations from '@/core/i18n/translations/es/terms.json';
import frTranslations from '@/core/i18n/translations/fr/terms.json';
import nlTranslations from '@/core/i18n/translations/nl/terms.json';

interface TermsAccordionProps {
  onAccept?: () => void;
  version?: string;
  showAcceptButton?: boolean;
  defaultValue?: string;
  locale?: AvailableLocale;
}

export default function TermsAccordion({
  onAccept,
  version = CURRENT_TERMS_VERSION,
  showAcceptButton = true,
  defaultValue,
  locale = 'fr'
}: TermsAccordionProps) {
  const [accepted, setAccepted] = useState(false);

  // Get translations based on locale
  const getTranslation = (localeCode: AvailableLocale) => {
    const translationMap: Record<AvailableLocale, any> = {
      fr: frTranslations.fr,
      en: enTranslations.en,
      es: esTranslations.es,
      nl: nlTranslations.nl
    };
    return translationMap[localeCode] || translationMap.fr;
  };

  // Get current translation
  const t = getTranslation(locale);

  // Handle print
  const handlePrint = () => {
    const printContent = document.getElementById('terms-print-content');
    const printWindow = window.open('', '_blank');
    if (printWindow && printContent) {
      printWindow.document.write(`
        <html>
          <head>
            <title>Linguify - ${t.title}</title>
            <style>
              body { font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; }
              h1 { text-align: center; color: #4F46E5; }
              .section { margin-bottom: 20px; }
              .section-title { font-weight: bold; margin-bottom: 10px; }
              .footer { margin-top: 40px; text-align: center; font-size: 12px; color: #666; }
            </style>
          </head>
          <body>
            <h1>Linguify - ${t.title} (${version})</h1>
            <div>${t.lastUpdate} ${new Date().toLocaleDateString(locale === 'en' ? 'en-US' : locale === 'es' ? 'es-ES' : locale === 'nl' ? 'nl-NL' : 'fr-FR')}</div>
            ${t.sections.map((section: any) => `
              <div class="section">
                <div class="section-title">${section.title}</div>
                <div>${section.content.replace(/\n/g, '<br>')}</div>
              </div>
            `).join('')}
            <div class="footer">
              © ${new Date().getFullYear()} Linguify. ${t.copyright}
            </div>
          </body>
        </html>
      `);
      printWindow.document.close();
      printWindow.print();
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto p-4 bg-white rounded-lg shadow">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">{t.title} {version}</h2>
        <div className="flex space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handlePrint}
            className="flex items-center gap-1.5"
          >
            <Printer className="h-4 w-4" />
            <span className="hidden sm:inline">{t.print}</span>
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => alert('Téléchargement du PDF...')}
            className="flex items-center gap-1.5"
          >
            <Download className="h-4 w-4" />
            <span className="hidden sm:inline">{t.download}</span>
          </Button>
        </div>
      </div>

      <div className="text-sm text-gray-500 mb-4">
        {t.lastUpdate} {new Date().toLocaleDateString(locale === 'en' ? 'en-US' : locale === 'es' ? 'es-ES' : locale === 'nl' ? 'nl-NL' : 'fr-FR')}
      </div>

      <div id="terms-print-content">
        <Accordion 
          type="single" 
          collapsible 
          defaultValue={defaultValue}
          className="mb-6"
        >
          {t.sections && t.sections.map((section: any) => (
            <AccordionItem value={section.id} key={section.id}>
              <AccordionTrigger className="text-left">
                {section.title}
              </AccordionTrigger>
              <AccordionContent className="whitespace-pre-line">
                {section.content}
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </div>

      {showAcceptButton && onAccept && (
        <div className="pt-4 border-t">
          <div className="flex items-center space-x-2 mb-4">
            <Checkbox
              id="terms-accept"
              checked={accepted}
              onCheckedChange={(checked) => setAccepted(checked === true)}
            />
            <Label htmlFor="terms-accept">
              {t.acceptLabel}
            </Label>
          </div>

          <Button
            onClick={onAccept}
            disabled={!accepted}
            className="w-full sm:w-auto"
          >
            {t.acceptButton}
          </Button>
        </div>
      )}
    </div>
  );
}