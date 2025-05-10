/**
 * @jest-environment jsdom
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import OnboardingLanguageSelector from '../components/OnboardingLanguageSelector';
import OnboardingHeader from '../components/OnboardingHeader';
import WelcomeStep from '../components/steps/WelcomeStep';
import { useTranslation } from '@/core/i18n/useTranslations';

// Mock the translation hooks
jest.mock('@/core/i18n/useTranslations', () => ({
  useTranslation: jest.fn(),
}));

// Mock the Framer Motion and UI components
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }) => <div {...props}>{children}</div>,
  },
  AnimatePresence: ({ children }) => <>{children}</>,
}));

jest.mock('@/components/ui/dropdown-menu', () => ({
  DropdownMenu: ({ children }) => <div data-testid="dropdown-menu">{children}</div>,
  DropdownMenuTrigger: ({ children }) => <div data-testid="dropdown-trigger">{children}</div>,
  DropdownMenuContent: ({ children }) => <div data-testid="dropdown-content">{children}</div>,
  DropdownMenuItem: ({ children, onClick }) => (
    <button data-testid="dropdown-item" onClick={onClick}>
      {children}
    </button>
  ),
}));

jest.mock('@/components/ui/tooltip', () => ({
  Tooltip: ({ children }) => <div data-testid="tooltip">{children}</div>,
  TooltipTrigger: ({ children }) => <div data-testid="tooltip-trigger">{children}</div>,
  TooltipContent: ({ children }) => <div data-testid="tooltip-content">{children}</div>,
  TooltipProvider: ({ children }) => <div data-testid="tooltip-provider">{children}</div>,
}));

jest.mock('@/components/ui/button', () => ({
  Button: ({ children, onClick, ...props }) => (
    <button onClick={onClick} data-testid="button" {...props}>
      {children}
    </button>
  ),
}));

jest.mock('@/components/ui/progress', () => ({
  Progress: ({ value }) => <div data-testid="progress-bar" data-value={value} />,
}));

jest.mock('@/components/ui/use-toast', () => ({
  useToast: () => ({
    toast: jest.fn(),
  }),
}));

describe('Onboarding Internationalization', () => {
  beforeEach(() => {
    // Set up mocks for each test
    (useTranslation as jest.Mock).mockReturnValue({
      t: (key: string, params?: any, fallback?: string) => {
        // Simple translation function that returns the key and fallback
        if (key === 'onboarding.title') return 'Welcome to Linguify';
        if (key === 'onboarding.steps.welcome.title') return 'Welcome!';
        if (key === 'onboarding.steps.welcome.description') return 'Begin your journey';
        if (key === 'interface.changeLanguage') return 'Change language';
        return fallback || key;
      },
      locale: 'en',
      changeLanguage: jest.fn(),
    });
  });

  test('OnboardingLanguageSelector renders with correct language', () => {
    const handleLanguageChange = jest.fn();
    render(<OnboardingLanguageSelector onLanguageChange={handleLanguageChange} />);
    
    // Check if English is displayed as current language
    expect(screen.getByText('English')).toBeInTheDocument();
  });

  test('WelcomeStep displays translated content', () => {
    render(<WelcomeStep />);
    
    // Check for translated welcome content
    expect(screen.getByText('Welcome!')).toBeInTheDocument();
    expect(screen.getByText('Begin your journey')).toBeInTheDocument();
  });

  test('Language change triggers callback', async () => {
    const mockChangeLanguage = jest.fn();
    const handleLanguageChange = jest.fn();
    
    (useTranslation as jest.Mock).mockReturnValue({
      t: (key: string, params?: any, fallback?: string) => fallback || key,
      locale: 'en',
      changeLanguage: mockChangeLanguage,
    });
    
    render(<OnboardingLanguageSelector onLanguageChange={handleLanguageChange} />);
    
    // Click the language dropdown
    fireEvent.click(screen.getByTestId('dropdown-trigger'));
    
    // Find and click on a language item (simulating a language change)
    const items = screen.getAllByTestId('dropdown-item');
    fireEvent.click(items[1]); // Click the second language option
    
    // Check if change functions were called
    expect(mockChangeLanguage).toHaveBeenCalled();
    expect(handleLanguageChange).toHaveBeenCalled();
  });

  test('Header shows correct translated title', () => {
    const mockSteps = [
      { id: 1, title: 'Welcome', description: 'First step', icon: () => <div>Icon</div> }
    ];
    
    render(
      <OnboardingHeader 
        currentStep={1} 
        totalSteps={1} 
        steps={mockSteps}
        onShowDevTools={jest.fn()}
        onSkipOnboarding={jest.fn()}
        onGoToStep={jest.fn()}
      />
    );
    
    // Check if the header shows the translated title
    expect(screen.getByText('Welcome to Linguify')).toBeInTheDocument();
  });
});