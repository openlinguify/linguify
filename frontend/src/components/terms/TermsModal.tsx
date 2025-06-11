'use client';

import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { ScrollArea } from '@/components/ui/scroll-area';
import { ChevronDown, Printer, Download, ExternalLink } from 'lucide-react';
import { AvailableLocale, getTranslations, TERMS_LAST_UPDATED, CURRENT_TERMS_VERSION, TermsSection } from './termsContent';
import { useTranslation } from '@/core/i18n/useTranslations';

interface TermsModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAccept: () => void;
  version?: string;
  standalone?: boolean;
  showAcceptance?: boolean;
  locale?: AvailableLocale;
}

export default function TermsModal({
  isOpen,
  onClose,
  onAccept,
  version = CURRENT_TERMS_VERSION,
  standalone = false,
  showAcceptance = true,
  locale = 'fr'
}: TermsModalProps) {
  const [isExpanded, setIsExpanded] = useState<boolean[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [accepted, setAccepted] = useState(false);
  
  const { t } = useTranslation();
  
  // Get translations for current locale
  const translations = getTranslations(locale);
  const sections = translations.sections;

  // Initialize expanded sections state
  useEffect(() => {
    setIsExpanded(new Array(sections.length).fill(false));
    setIsLoading(false);
  }, [sections.length]);

  // Toggle section expansion
  const toggleSection = (index: number) => {
    const newExpanded = [...isExpanded];
    newExpanded[index] = !newExpanded[index];
    setIsExpanded(newExpanded);
  };

  // Handle print
  const handlePrint = () => {
    const printContent = document.getElementById('terms-print-content');
    if (printContent) {
      const printWindow = window.open('', '_blank');
      if (printWindow) {
        printWindow.document.write(`
          <html>
            <head>
              <title>Linguify - ${translations.title}</title>
              <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; }
                h1 { text-align: center; color: #4F46E5; }
                .section { margin-bottom: 20px; }
                .section-title { font-weight: bold; margin-bottom: 10px; }
                .footer { margin-top: 40px; text-align: center; font-size: 12px; color: #666; }
              </style>
            </head>
            <body>
              <h1>Linguify - ${translations.title} (${version})</h1>
              <div>${translations.lastUpdate} ${new Date().toLocaleDateString(locale === 'en' ? 'en-US' : locale === 'es' ? 'es-ES' : locale === 'nl' ? 'nl-NL' : 'fr-FR')}</div>
              ${sections.map((section: any) => `
                <div class="section">
                  <div class="section-title">${section.title}</div>
                  <div>${section.content.replace(/\n/g, '<br>')}</div>
                </div>
              `).join('')}
              <div class="footer">
                © ${new Date().getFullYear()} Linguify. ${translations.copyright}
              </div>
            </body>
          </html>
        `);
        printWindow.document.close();
        printWindow.print();
      }
    }
  };

  // Handle download as PDF
  const handleDownload = () => {
    // In a real implementation, this would generate and download a PDF
    alert(translations.pdfAlert || 'Cette fonctionnalité téléchargerait les termes au format PDF.');
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className={`sm:max-w-2xl ${standalone ? 'h-[90vh]' : 'max-h-[90vh]'}`}>
        <DialogHeader>
          <DialogTitle className="flex justify-between items-center">
            <span>{translations.title} {version}</span>
            <div className="flex space-x-2">
              <Button
                variant="outline"
                size="sm"
                className="h-8 w-8 p-0"
                onClick={handlePrint}
                title={translations.print}
              >
                <Printer className="h-4 w-4" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="h-8 w-8 p-0"
                onClick={handleDownload}
                title={translations.download}
              >
                <Download className="h-4 w-4" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="h-8 w-8 p-0"
                onClick={() => window.open('/annexes/legal', '_blank')}
                title={translations.openNew || "Ouvrir dans une nouvelle fenêtre"}
              >
                <ExternalLink className="h-4 w-4" />
              </Button>
            </div>
          </DialogTitle>
          <DialogDescription>
            {translations.disclaimer || 'Conditions générales d\'utilisation de Linguify.'}
          </DialogDescription>
        </DialogHeader>

        <div className="text-sm text-muted-foreground mb-4">
          {translations.lastUpdate} {TERMS_LAST_UPDATED}
        </div>

        <ScrollArea className="max-h-[60vh] pr-4" id="terms-print-content">
          <div className="space-y-4">
            {isLoading ? (
              <div className="flex justify-center items-center h-40">
                <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
              </div>
            ) : (
              sections.map((section: TermsSection, index: number) => (
                <div
                  key={index}
                  className="border rounded-lg overflow-hidden transition-all duration-200"
                >
                  <div
                    className="flex justify-between items-center p-4 bg-slate-50 cursor-pointer"
                    onClick={() => toggleSection(index)}
                  >
                    <h3 className="font-medium">{section.title}</h3>
                    <ChevronDown
                      className={`h-5 w-5 transition-transform ${
                        isExpanded[index] ? 'transform rotate-180' : ''
                      }`}
                    />
                  </div>
                  {isExpanded[index] && (
                    <div className="p-4 bg-white">
                      <p className="whitespace-pre-line">{section.content}</p>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </ScrollArea>

        {showAcceptance && (
          <div className="mt-4 flex items-center space-x-2">
            <Checkbox
              id="terms"
              checked={accepted}
              onCheckedChange={(checked) => setAccepted(checked === true)}
            />
            <Label htmlFor="terms" className="text-sm">
              {translations.acceptLabel}
            </Label>
          </div>
        )}

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            {standalone ? translations.close || 'Fermer' : translations.cancel || 'Annuler'}
          </Button>
          {showAcceptance && (
            <Button onClick={onAccept} disabled={!accepted}>
              {translations.acceptButton}
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}