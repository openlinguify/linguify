'use client';

import React, { useState } from 'react';
import { useTranslation } from '@/core/i18n/useTranslations';
import { Printer, FileDown, ExternalLink, ArrowDown, ArrowUp, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogClose,
} from '@/components/ui/dialog';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';

interface TermsAndConditionsProps {
  isAccepted: boolean;
  onAcceptChange: (isAccepted: boolean) => void;
  locale?: string;
}

const TermsAndConditions: React.FC<TermsAndConditionsProps> = ({
  isAccepted,
  onAcceptChange,
  locale = 'en',
}) => {
  const { t } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const [expandedSections, setExpandedSections] = useState<string[]>([]);

  const today = new Date().toLocaleDateString(locale, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  // Mock sections and key points for development/testing when API is unavailable
  const mockSections = [
    {
      id: 'usage',
      title: 'Terms of Usage',
      content: 'By using Linguify, you agree to use the service responsibly and in accordance with all applicable laws. This is a development/testing version of the terms.'
    },
    {
      id: 'privacy',
      title: 'Privacy Policy',
      content: 'We respect your privacy and protect your personal information according to our privacy policy.'
    },
    {
      id: 'intellectual',
      title: 'Intellectual Property',
      content: 'All content provided on Linguify is protected by copyright and intellectual property laws.'
    },
    {
      id: 'cancellation',
      title: 'Cancellation Policy',
      content: 'You may cancel your account at any time, subject to our cancellation policy.'
    },
    {
      id: 'liability',
      title: 'Limitation of Liability',
      content: 'Linguify is not liable for any damages arising from the use of our service.'
    }
  ];

  const defaultKeyPoints = [
    {
      title: 'Personal Data',
      description: 'We collect and process your data to provide language learning services.'
    },
    {
      title: 'Learning Content',
      description: 'All learning content is provided "as is" without warranties.'
    },
    {
      title: 'User Accounts',
      description: 'You are responsible for maintaining the security of your account.'
    },
    {
      title: 'Subscriptions',
      description: 'Subscription fees are subject to change with notice to users.'
    },
    {
      title: 'Termination',
      description: 'We reserve the right to terminate accounts that violate our terms.'
    }
  ];

  // Determine if we should show development mode message
  const isDevelopmentMode = typeof window !== 'undefined' && window.location.hostname === 'localhost';

  // Get terms sections from translations or use defaults
  const sections = t('terms.sections', { fallback: mockSections });
  const keyPoints = t('terms.keyPoints', { fallback: defaultKeyPoints });

  // In development mode, always use mock data
  const termsData = isDevelopmentMode
    ? { sections: mockSections, keyPoints: defaultKeyPoints }
    : { sections, keyPoints };

  // Helper functions
  const toggleSection = (id: string) => {
    setExpandedSections(prev =>
      prev.includes(id) ? prev.filter(item => item !== id) : [...prev, id]
    );
  };

  const expandAll = () => {
    setExpandedSections(sections.map((section: any) => section.id));
  };

  const collapseAll = () => {
    setExpandedSections([]);
  };

  const printTerms = () => {
    window.print();
  };

  const downloadPdf = () => {
    alert(t('terms.pdfAlert', {}, "This feature would download the terms and conditions in PDF format in a real implementation."));
  };

  return (
    <div className="w-full">
      <div className="flex items-center space-x-2 mb-4">
        <Checkbox
          id="terms"
          checked={isAccepted}
          onCheckedChange={(checked) => {
            // Ensure we're passing a boolean value
            console.log("Terms checkbox changed:", checked);
            onAcceptChange(checked === true);
          }}
          aria-describedby="terms-description"
        />
        <div className="grid gap-1.5 leading-none">
          <Label 
            htmlFor="terms" 
            className="font-medium cursor-pointer text-sm"
            onClick={() => setIsOpen(true)}
          >
            {t('terms.acceptLabel', {}, "I have read and accept the terms and conditions")}
          </Label>
          <p 
            id="terms-description" 
            className="text-xs text-muted-foreground underline cursor-pointer"
            onClick={() => setIsOpen(true)}
          >
            {t('terms.readFullTerms', {}, "Read full terms")}
          </p>
        </div>
      </div>

      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogContent className="max-w-3xl max-h-[90vh] flex flex-col">
          <DialogHeader>
            <DialogTitle className="text-xl flex items-center justify-between">
              {t('terms.title', {}, "Terms and Conditions")}
              <Badge variant="outline" className="ml-2">
                {t('terms.lastUpdate', {}, "Last updated")}: {today}
              </Badge>
            </DialogTitle>
            <DialogDescription>
              {t('terms.disclaimer', {}, "Linguify is a language learning platform created by GPI Software.")}
            </DialogDescription>
          </DialogHeader>

          <div className="flex justify-end space-x-2 my-2">
            <Button variant="outline" size="sm" onClick={printTerms}>
              <Printer className="h-4 w-4 mr-1" />
              {t('terms.print', {}, "Print")}
            </Button>
            <Button variant="outline" size="sm" onClick={downloadPdf}>
              <FileDown className="h-4 w-4 mr-1" />
              {t('terms.download', {}, "PDF")}
            </Button>
            <Button variant="outline" size="sm" onClick={window.open ? () => window.open('/terms', '_blank') : undefined}>
              <ExternalLink className="h-4 w-4 mr-1" />
              {t('terms.openNew', {}, "Open in new window")}
            </Button>
          </div>

          <Alert className="mb-4">
            <h3 className="font-medium">{t('terms.summary', {}, "Summary of key points")}</h3>
            <AlertDescription>
              {t('terms.summaryDisclaimer', {}, "This summary is provided for your convenience. For a complete understanding, please read the full terms.")}
            </AlertDescription>
          </Alert>

          {isDevelopmentMode && (
            <div className="mb-4 p-2 bg-yellow-50 border border-yellow-200 rounded-md text-xs text-yellow-700">
              <p><strong>Development Mode:</strong> Using mock terms and conditions data. In production, these would be loaded from the backend API.</p>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
            {termsData.keyPoints.map((point: any, idx: number) => (
              <div key={idx} className="p-3 border rounded-md">
                <h4 className="font-medium">{point.title}</h4>
                <p className="text-sm text-muted-foreground">{point.description}</p>
              </div>
            ))}
          </div>

          <Separator className="my-2" />

          <div className="flex justify-between items-center mb-2">
            <h3 className="font-semibold">{t('terms.title', {}, "Terms and Conditions")}</h3>
            <div className="flex gap-2">
              <Button variant="ghost" size="sm" onClick={expandAll}>
                <ArrowDown className="h-4 w-4 mr-1" />
                {t('common.expandAll', {}, "Expand All")}
              </Button>
              <Button variant="ghost" size="sm" onClick={collapseAll}>
                <ArrowUp className="h-4 w-4 mr-1" />
                {t('common.collapseAll', {}, "Collapse All")}
              </Button>
            </div>
          </div>

          <ScrollArea className="flex-1 pr-4">
            <Accordion
              type="multiple"
              value={expandedSections}
              onValueChange={setExpandedSections}
              className="w-full"
            >
              {termsData.sections.map((section: any) => (
                <AccordionItem key={section.id} value={section.id}>
                  <AccordionTrigger>{section.title}</AccordionTrigger>
                  <AccordionContent>
                    <div className="whitespace-pre-line text-sm">
                      {section.content}
                    </div>
                  </AccordionContent>
                </AccordionItem>
              ))}
            </Accordion>
          </ScrollArea>

          <DialogFooter className="pt-4">
            <div className="flex items-center justify-between w-full">
              <Button variant="outline" onClick={() => setIsOpen(false)}>
                {t('terms.close', {}, "Close")}
              </Button>
              <Button
                onClick={() => {
                  console.log("Accept button clicked in dialog");
                  onAcceptChange(true);
                  setIsOpen(false);
                }}
                className="bg-gradient-to-r from-indigo-600 to-purple-600"
              >
                {t('terms.acceptButton', {}, "Accept and continue")}
              </Button>
            </div>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default TermsAndConditions;