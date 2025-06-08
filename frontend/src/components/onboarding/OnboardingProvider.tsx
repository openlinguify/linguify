// src/components/onboarding/OnboardingProvider.tsx
'use client';
import React, { createContext, useContext, useState, useEffect } from "react";
import OnboardingFlow from "./OnboardingFlow";
import { useAuthContext } from "@/core/auth/AuthAdapter";

// Create context
interface OnboardingContextType {
  isOnboardingComplete: boolean;
  setOnboardingComplete: (complete: boolean) => void;
  resetOnboarding: () => void;
}

const OnboardingContext = createContext<OnboardingContextType | undefined>(undefined);

// Provider component
export const OnboardingProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, isAuthenticated, isLoading } = useAuthContext();
  
  // Initialize from localStorage to avoid unnecessary checks
  const [isOnboardingComplete, setIsOnboardingComplete] = useState(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem("onboardingCompleted") === "true";
    }
    return false;
  });
  
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [hasChecked, setHasChecked] = useState(false);

  // Reset onboarding (for testing or manual reset)
  const resetOnboarding = () => {
    localStorage.removeItem("onboardingCompleted");
    setIsOnboardingComplete(false);
    setShowOnboarding(true);
  };

  // Set onboarding as complete
  const setOnboardingComplete = (complete: boolean) => {
    localStorage.setItem("onboardingCompleted", complete ? "true" : "false");
    setIsOnboardingComplete(complete);
    setShowOnboarding(!complete);
  };

  // Check if user needs onboarding
  useEffect(() => {
    // Skip if already checked or still loading
    if (hasChecked || isLoading || !isAuthenticated || !user) {
      return;
    }

    // Mark as checked to prevent repeated checks
    setHasChecked(true);

    // SIMPLIFIED: Always mark onboarding as complete
    // This avoids unnecessary checks and logging
    setIsOnboardingComplete(true);
    setShowOnboarding(false);
  }, [isAuthenticated, isLoading, user, hasChecked]);

  // Handler for when onboarding is completed
  const handleOnboardingComplete = () => {
    setOnboardingComplete(true);
  };

  return (
    <OnboardingContext.Provider
      value={{
        isOnboardingComplete,
        setOnboardingComplete,
        resetOnboarding
      }}
    >
      {children}
      {showOnboarding && <OnboardingFlow onComplete={handleOnboardingComplete} />}
    </OnboardingContext.Provider>
  );
};

// Custom hook
export const useOnboarding = () => {
  const context = useContext(OnboardingContext);
  if (context === undefined) {
    throw new Error("useOnboarding must be used within an OnboardingProvider");
  }
  return context;
};

export default OnboardingProvider;