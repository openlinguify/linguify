/**
 * @jest-environment jsdom
 */

import React from 'react';
import { render, screen, fireEvent, act } from '@testing-library/react';
import OnboardingFlow from '../OnboardingFlow';
import { useTranslation } from '@/core/i18n/useTranslations';
import { useOnboardingForm } from '../hooks/useOnboardingForm';
import { useOnboardingValidation } from '../hooks/useOnboardingValidation';

// Mocks
jest.mock('@/core/i18n/useTranslations', () => ({
  useTranslation: jest.fn(),
}));

jest.mock('../hooks/useOnboardingForm', () => ({
  useOnboardingForm: jest.fn(),
}));

jest.mock('../hooks/useOnboardingValidation', () => ({
  useOnboardingValidation: jest.fn(),
}));

jest.mock('@/core/auth/AuthAdapter', () => ({
  useAuthContext: jest.fn().mockReturnValue({ user: { id: '123' } }),
}));

// Mock framer-motion
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }) => <div data-testid="motion-div" {...props}>{children}</div>,
  },
  AnimatePresence: ({ children }) => <>{children}</>,
}));

// Mock UI components
jest.mock('@/components/ui/button', () => ({
  Button: ({ children, onClick, ...props }) => (
    <button onClick={onClick} data-testid="button" {...props}>
      {children}
    </button>
  ),
}));

// Mock the step components
jest.mock('../components/steps/WelcomeStep', () => ({
  __esModule: true,
  default: () => <div data-testid="welcome-step">Welcome Step</div>,
}));

jest.mock('../components/steps/PersonalInfoStep', () => ({
  __esModule: true,
  default: ({ onChange }) => (
    <div data-testid="personal-info-step">
      <button onClick={() => onChange('first_name', 'John')}>Set Name</button>
    </div>
  ),
}));

jest.mock('../components/OnboardingHeader', () => {
  return {
    __esModule: true,
    default: ({ onLanguageChange }) => (
      <div data-testid="onboarding-header">
        <button 
          data-testid="language-change-button" 
          onClick={() => onLanguageChange && onLanguageChange('fr')}
        >
          Change Language
        </button>
      </div>
    ),
  };
});

describe('OnboardingFlow', () => {
  beforeEach(() => {
    // Set up the mocks for translation
    (useTranslation as jest.Mock).mockReturnValue({
      t: (key: string, params?: any, fallback?: string) => fallback || key,
      locale: 'en',
      changeLanguage: jest.fn(),
    });

    // Mock form data and handlers
    const mockFormData = {
      first_name: '',
      last_name: '',
      username: '',
      bio: '',
      native_language: '',
      target_language: '',
      language_level: 'A1',
      objectives: 'Travel',
      interface_language: 'en',
      termsAccepted: false,
    };

    const mockHandleInputChange = jest.fn((field, value) => {
      mockFormData[field as keyof typeof mockFormData] = value as any;
    });

    (useOnboardingForm as jest.Mock).mockReturnValue({
      formData: mockFormData,
      initialData: { ...mockFormData },
      validationErrors: {},
      isSubmitting: false,
      lastServerResponse: null,
      apiRequests: [],
      changedFieldsCount: 0,
      fetchCurrentProfile: jest.fn(),
      handleInputChange: mockHandleInputChange,
      handleSubmit: jest.fn().mockResolvedValue(true),
      clearApiRequests: jest.fn(),
    });

    // Mock validation
    (useOnboardingValidation as jest.Mock).mockReturnValue({
      validateStep: jest.fn().mockReturnValue({ isValid: true, errors: {} }),
      validationErrors: {},
    });
  });

  test('should render the welcome step initially', () => {
    render(<OnboardingFlow onComplete={jest.fn()} />);
    expect(screen.getByTestId('welcome-step')).toBeInTheDocument();
  });

  test('should update interface language when language is changed', () => {
    const mockHandleInputChange = jest.fn();
    
    (useOnboardingForm as jest.Mock).mockReturnValue({
      formData: { interface_language: 'en' },
      initialData: { interface_language: 'en' },
      validationErrors: {},
      isSubmitting: false,
      lastServerResponse: null,
      apiRequests: [],
      changedFieldsCount: 0,
      fetchCurrentProfile: jest.fn(),
      handleInputChange: mockHandleInputChange,
      handleSubmit: jest.fn().mockResolvedValue(true),
      clearApiRequests: jest.fn(),
    });

    render(<OnboardingFlow onComplete={jest.fn()} />);
    
    // Find and click the language change button in the header
    const languageButton = screen.getByTestId('language-change-button');
    fireEvent.click(languageButton);
    
    // Check if handleInputChange was called with the correct parameters
    expect(mockHandleInputChange).toHaveBeenCalledWith('interface_language', 'fr');
  });
});