'use client';

import React, { useState, useEffect } from 'react';
import { useTranslation } from '@/core/i18n/useTranslations';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogDescription } from '@/components/ui/dialog';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Keyboard } from 'lucide-react';

interface KeyboardHelpModalProps {
  autoShowOnFirstVisit?: boolean;
}

const KeyboardHelpModal: React.FC<KeyboardHelpModalProps> = ({
  autoShowOnFirstVisit = true
}) => {
  // State to control dialog visibility
  const [isOpen, setIsOpen] = useState(false);

  // Show help dialog automatically on first visit
  useEffect(() => {
    if (autoShowOnFirstVisit) {
      const hasSeenKeyboardHelp = localStorage.getItem('hasSeenKeyboardHelp');
      if (!hasSeenKeyboardHelp) {
        // Delay opening to ensure the onboarding flow is fully rendered
        const timer = setTimeout(() => {
          setIsOpen(true);
          localStorage.setItem('hasSeenKeyboardHelp', 'true');
        }, 2000);

        return () => clearTimeout(timer);
      }
    }
  }, [autoShowOnFirstVisit]);

  // Pulse animation for the button to draw attention
  const [showPulse, setShowPulse] = useState(false);

  useEffect(() => {
    // Start pulsing after a delay if user hasn't seen the help yet
    const hasSeenKeyboardHelp = localStorage.getItem('hasSeenKeyboardHelp');
    if (!hasSeenKeyboardHelp) {
      const timer = setTimeout(() => setShowPulse(true), 5000);
      return () => clearTimeout(timer);
    }
  }, []);
  const { t } = useTranslation();

  const shortcuts = [
    {
      key: t('onboarding.a11y.shortcuts.tab.key', {}, 'Tab'),
      description: t('onboarding.a11y.shortcuts.tab.description', {}, 'Navigate forward through form fields and buttons'),
    },
    {
      key: t('onboarding.a11y.shortcuts.tabShift.key', {}, 'Shift + Tab'),
      description: t('onboarding.a11y.shortcuts.tabShift.description', {}, 'Navigate backward through form fields and buttons'),
    },
    {
      key: t('onboarding.a11y.shortcuts.arrowLeftRight.key', {}, '← →'),
      description: t('onboarding.a11y.shortcuts.arrowLeftRight.description', {}, 'Navigate between steps in the step pills'),
    },
    {
      key: t('onboarding.a11y.shortcuts.arrowRight.key', {}, '→'),
      description: t('onboarding.a11y.shortcuts.arrowRight.description', {}, 'Advance to next step when focused on Next button'),
    },
    {
      key: t('onboarding.a11y.shortcuts.arrowLeft.key', {}, '←'),
      description: t('onboarding.a11y.shortcuts.arrowLeft.description', {}, 'Go to previous step when focused on Back button'),
    },
    {
      key: t('onboarding.a11y.shortcuts.spacebar.key', {}, 'Space'),
      description: t('onboarding.a11y.shortcuts.spacebar.description', {}, 'Toggle buttons and checkboxes'),
    },
    {
      key: t('onboarding.a11y.shortcuts.enter.key', {}, 'Enter'),
      description: t('onboarding.a11y.shortcuts.enter.description', {}, 'Activate buttons and links'),
    },
    {
      key: t('onboarding.a11y.shortcuts.escape.key', {}, 'Esc'),
      description: t('onboarding.a11y.shortcuts.escape.description', {}, 'Skip onboarding (if allowed)'),
    },
  ];

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <motion.div
          animate={showPulse ? {
            scale: [1, 1.1, 1],
            opacity: [0.7, 1, 0.7],
          } : {}}
          transition={{
            repeat: showPulse ? Infinity : 0,
            repeatType: "reverse",
            duration: 2,
          }}
        >
          <Button
            variant="ghost"
            size="icon"
            className="text-white/70 hover:text-white hover:bg-white/20 relative"
            aria-label={t('onboarding.a11y.shortcuts.buttonLabel', {}, 'Keyboard shortcuts')}
            onFocus={() => setShowPulse(false)}
            onClick={() => setShowPulse(false)}
          >
            <Keyboard className="h-4 w-4" />
            {showPulse && (
              <span className="absolute -top-1 -right-1 flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-purple-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-purple-500"></span>
              </span>
            )}
          </Button>
        </motion.div>
      </DialogTrigger>
      <DialogContent className="max-w-md" onOpenAutoFocus={(e) => e.preventDefault()}>
        <DialogHeader>
          <DialogTitle className="text-center text-xl font-bold mb-2">
            {t('onboarding.a11y.shortcuts.title', {}, 'Keyboard Shortcuts')}
          </DialogTitle>
          <DialogDescription className="text-center text-sm">
            {t('onboarding.a11y.shortcuts.description', {}, 'Use these keyboard shortcuts for faster navigation through the onboarding process.')}
          </DialogDescription>
        </DialogHeader>

        <div className="my-4 p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-100 dark:border-purple-900/30">
          <h3 className="text-sm font-medium text-purple-800 dark:text-purple-300 mb-2">
            {t('onboarding.a11y.shortcuts.tip', {}, 'Pro Tip:')}
          </h3>
          <p className="text-xs text-purple-700 dark:text-purple-300">
            {t('onboarding.a11y.shortcuts.tipDescription', {}, 'For screen reader users: All controls are properly labeled and you can navigate the onboarding flow using standard screen reader commands.')}
          </p>
        </div>

        <div className="space-y-2">
          <h3 className="text-sm font-medium mb-2">
            {t('onboarding.a11y.shortcuts.navigation', {}, 'Navigation')}
          </h3>
          {shortcuts.slice(0, 5).map((shortcut, index) => (
            <motion.div
              key={index}
              className="flex gap-4 py-2 border-b border-gray-100 dark:border-gray-800 last:border-0"
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <code className="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded min-w-[80px] text-center font-mono text-sm shadow-sm">
                {shortcut.key}
              </code>
              <span className="text-sm">{shortcut.description}</span>
            </motion.div>
          ))}

          <h3 className="text-sm font-medium mt-4 mb-2">
            {t('onboarding.a11y.shortcuts.forms', {}, 'Forms & Controls')}
          </h3>
          {shortcuts.slice(5).map((shortcut, index) => (
            <motion.div
              key={index + 5}
              className="flex gap-4 py-2 border-b border-gray-100 dark:border-gray-800 last:border-0"
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: (index + 5) * 0.1 }}
            >
              <code className="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded min-w-[80px] text-center font-mono text-sm shadow-sm">
                {shortcut.key}
              </code>
              <span className="text-sm">{shortcut.description}</span>
            </motion.div>
          ))}
        </div>

        <div className="flex justify-end mt-4">
          <Button
            size="sm"
            variant="ghost"
            onClick={() => setIsOpen(false)}
            className="text-xs"
            autoFocus
          >
            {t('onboarding.a11y.shortcuts.closeButton', {}, 'Got it! Close')}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default KeyboardHelpModal;