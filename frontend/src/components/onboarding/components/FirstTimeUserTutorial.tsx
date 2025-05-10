'use client';

import React, { useState, useEffect } from 'react';
import { useTranslation } from '@/core/i18n/useTranslations';
import { motion, AnimatePresence } from 'framer-motion';
import { Keyboard, Mouse, ArrowRight, Check, Info } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

interface FirstTimeUserTutorialProps {
  autoShow?: boolean;
  onClose: () => void;
}

/**
 * A tutorial component for first-time users of the onboarding flow.
 * Provides tips on keyboard navigation, mouse controls, and accessibility features.
 */
const FirstTimeUserTutorial: React.FC<FirstTimeUserTutorialProps> = ({ 
  autoShow = true,
  onClose 
}) => {
  const { t } = useTranslation();
  const [isVisible, setIsVisible] = useState(false);
  const [activeTab, setActiveTab] = useState('keyboard');

  useEffect(() => {
    if (autoShow) {
      const hasSeenTutorial = localStorage.getItem('hasSeenOnboardingTutorial');
      if (!hasSeenTutorial) {
        // Delay showing the tutorial to ensure the onboarding flow is loaded
        const timer = setTimeout(() => {
          setIsVisible(true);
        }, 1000);
        
        return () => clearTimeout(timer);
      }
    }
  }, [autoShow]);

  const handleClose = () => {
    setIsVisible(false);
    localStorage.setItem('hasSeenOnboardingTutorial', 'true');
    onClose();
  };

  // Tutorial steps
  const keyboardTips = [
    {
      icon: <ArrowRight className="h-5 w-5" />,
      title: t('onboarding.tutorial.keyboard.navigation.title', {}, 'Navigation Keys'),
      description: t('onboarding.tutorial.keyboard.navigation.description', {}, 'Use Tab to move forward and Shift+Tab to move backward through interactive elements.'),
    },
    {
      icon: <Keyboard className="h-5 w-5" />,
      title: t('onboarding.tutorial.keyboard.shortcuts.title', {}, 'Keyboard Shortcuts'),
      description: t('onboarding.tutorial.keyboard.shortcuts.description', {}, 'Press Alt+N for Next, Alt+P for Previous, and Alt+S to Save on the review step.'),
    },
    {
      icon: <ArrowRight className="h-5 w-5" />,
      title: t('onboarding.tutorial.keyboard.arrows.title', {}, 'Arrow Navigation'),
      description: t('onboarding.tutorial.keyboard.arrows.description', {}, 'Use left and right arrow keys to navigate between step pills in the header.'),
    },
  ];

  const accessibilityTips = [
    {
      icon: <Info className="h-5 w-5" />,
      title: t('onboarding.tutorial.accessibility.screenReader.title', {}, 'Screen Reader Support'),
      description: t('onboarding.tutorial.accessibility.screenReader.description', {}, 'This flow is fully accessible to screen readers with ARIA landmarks and proper focus management.'),
    },
    {
      icon: <Keyboard className="h-5 w-5" />,
      title: t('onboarding.tutorial.accessibility.focus.title', {}, 'Focus Indicators'),
      description: t('onboarding.tutorial.accessibility.focus.description', {}, 'Visual focus indicators help you see which element is currently focused when using the keyboard.'),
    },
    {
      icon: <ArrowRight className="h-5 w-5" />,
      title: t('onboarding.tutorial.accessibility.help.title', {}, 'Help Button'),
      description: t('onboarding.tutorial.accessibility.help.description', {}, 'The keyboard shortcut help button in the header provides more detailed instructions.'),
    },
  ];

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[100] flex items-center justify-center p-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={(e) => {
            if (e.target === e.currentTarget) {
              handleClose();
            }
          }}
        >
          <motion.div 
            className="bg-white dark:bg-gray-900 rounded-xl shadow-xl w-full max-w-lg p-6 overflow-hidden"
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            transition={{ duration: 0.3 }}
            role="dialog"
            aria-modal="true"
            aria-labelledby="tutorial-title"
          >
            <h2 
              id="tutorial-title" 
              className="text-xl font-bold text-center mb-4 bg-gradient-to-r from-violet-600 to-indigo-600 text-transparent bg-clip-text"
            >
              {t('onboarding.tutorial.title', {}, 'Welcome to Linguify Onboarding')}
            </h2>
            
            <p className="text-sm text-center text-gray-600 dark:text-gray-400 mb-6">
              {t('onboarding.tutorial.subtitle', {}, 'Here are some tips to help you navigate through the onboarding process')}
            </p>
            
            <Tabs 
              defaultValue="keyboard" 
              value={activeTab} 
              onValueChange={setActiveTab} 
              className="w-full"
            >
              <TabsList className="grid grid-cols-2 mb-4">
                <TabsTrigger value="keyboard" className="flex items-center gap-2">
                  <Keyboard className="h-4 w-4" />
                  {t('onboarding.tutorial.tabs.keyboard', {}, 'Keyboard')}
                </TabsTrigger>
                <TabsTrigger value="accessibility" className="flex items-center gap-2">
                  <Info className="h-4 w-4" />
                  {t('onboarding.tutorial.tabs.accessibility', {}, 'Accessibility')}
                </TabsTrigger>
              </TabsList>
              
              <TabsContent value="keyboard" className="mt-0">
                <div className="space-y-4">
                  {keyboardTips.map((tip, index) => (
                    <motion.div
                      key={index}
                      className="flex items-start gap-4 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg"
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                    >
                      <div className="flex-shrink-0 w-8 h-8 bg-violet-100 dark:bg-violet-900/20 rounded-full flex items-center justify-center text-violet-600 dark:text-violet-400">
                        {tip.icon}
                      </div>
                      <div>
                        <h3 className="text-sm font-medium mb-1">{tip.title}</h3>
                        <p className="text-xs text-gray-600 dark:text-gray-400">{tip.description}</p>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </TabsContent>
              
              <TabsContent value="accessibility" className="mt-0">
                <div className="space-y-4">
                  {accessibilityTips.map((tip, index) => (
                    <motion.div
                      key={index}
                      className="flex items-start gap-4 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg"
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                    >
                      <div className="flex-shrink-0 w-8 h-8 bg-indigo-100 dark:bg-indigo-900/20 rounded-full flex items-center justify-center text-indigo-600 dark:text-indigo-400">
                        {tip.icon}
                      </div>
                      <div>
                        <h3 className="text-sm font-medium mb-1">{tip.title}</h3>
                        <p className="text-xs text-gray-600 dark:text-gray-400">{tip.description}</p>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </TabsContent>
            </Tabs>
            
            <div className="flex justify-end mt-6">
              <Button 
                className="bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700"
                onClick={handleClose}
                autoFocus
              >
                <Check className="h-4 w-4 mr-2" />
                {t('onboarding.tutorial.closeButton', {}, 'Got it, thanks!')}
              </Button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default FirstTimeUserTutorial;