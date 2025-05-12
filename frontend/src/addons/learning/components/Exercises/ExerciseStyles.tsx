'use client';

import React from 'react';
import { cva } from 'class-variance-authority';

/**
 * Styles communs pour les exercices d'apprentissage
 * Ces styles garantissent une apparence cohérente à travers les différents types d'exercices
 */

// Styles pour les conteneurs d'exercice
export const exerciseContainer = cva([
  "w-full",
  "max-w-4xl", 
  "mx-auto",
  "space-y-6",
  "bg-white dark:bg-gray-900",
  "rounded-xl",
  "shadow-sm dark:shadow-none",
  "overflow-hidden",
  "transition-all duration-200"
]);

// Styles pour les cartes d'exercice
export const exerciseCard = cva([
  "rounded-xl",
  "overflow-hidden",
  "shadow-md dark:shadow-none",
  "border border-gray-100 dark:border-gray-800",
  "bg-gradient-to-br from-white to-gray-50 dark:from-gray-900 dark:to-gray-800",
  "transition-all duration-200"
]);

// Styles pour les titres d'exercice
export const exerciseHeading = cva([
  "text-xl md:text-2xl",
  "font-bold",
  "bg-gradient-to-r from-brand-purple to-brand-gold",
  "bg-clip-text",
  "text-transparent",
  "pb-1"
]);

// Styles pour les sections d'exercice
export const exerciseSection = cva([
  "p-6",
  "rounded-lg",
  "transition-all"
]);

// Styles pour les options de réponse
export const exerciseOptions = cva([
  "grid",
  "grid-cols-1 sm:grid-cols-2",
  "gap-3"
]);

// Styles pour les boutons de réponse
export const answerButton = (isSelected: boolean, isCorrect: boolean | null) => {
  const baseClasses = [
    "w-full",
    "p-4",
    "rounded-lg",
    "border-2",
    "font-medium",
    "transition-all duration-200",
    "flex items-center"
  ];

  // État normal (non sélectionné)
  if (!isSelected) {
    return [
      ...baseClasses,
      "border-brand-purple/30 dark:border-brand-purple/20",
      "bg-white dark:bg-gray-800",
      "hover:bg-brand-purple/10 dark:hover:bg-brand-purple/20",
      "shadow-sm"
    ].join(" ");
  }

  // Réponse correcte
  if (isCorrect) {
    return [
      ...baseClasses,
      "border-green-500 dark:border-green-600",
      "bg-green-50 dark:bg-green-900/20",
      "text-green-700 dark:text-green-300",
      "shadow-green-200/50 dark:shadow-green-900/20"
    ].join(" ");
  }

  // Réponse incorrecte
  return [
    ...baseClasses,
    "border-red-500 dark:border-red-600",
    "bg-red-50 dark:bg-red-900/20",
    "text-red-700 dark:text-red-300",
    "shadow-red-200/50 dark:shadow-red-900/20"
  ].join(" ");
};

// Styles pour les boîtes d'exercice (comme les phrases à trous)
export const exerciseContentBox = cva([
  "bg-gradient-to-br",
  "from-brand-purple/5 to-brand-gold/5",
  "p-6",
  "rounded-lg",
  "text-center",
  "border border-brand-purple/10",
  "shadow-sm",
  "transition-all"
]);

// Styles pour les boutons de navigation d'exercice
export const navigationButton = cva([
  "flex items-center gap-2",
  "font-medium",
  "transition-all duration-200"
]);

// Styles pour les messages de feedback
export const feedbackMessage = (isCorrect: boolean) => {
  const baseClasses = [
    "mt-4",
    "p-4",
    "rounded-lg",
    "text-sm",
    "flex items-center",
    "gap-2",
    "shadow-sm",
    "transition-all"
  ];

  return isCorrect 
    ? [...baseClasses, "bg-green-50 dark:bg-green-900/20", "text-green-700 dark:text-green-300", "border border-green-200 dark:border-green-800"].join(" ")
    : [...baseClasses, "bg-red-50 dark:bg-red-900/20", "text-red-700 dark:text-red-300", "border border-red-200 dark:border-red-800"].join(" ");
};

// Wrapper de composant pour appliquer des styles cohérents aux exercices
export function ExerciseWrapper({ children, className = "" }: { children: React.ReactNode, className?: string }) {
  return (
    <div className={exerciseContainer() + " " + className}>
      {children}
    </div>
  );
}

// Wrapper de section d'exercice
export function ExerciseSectionWrapper({ children, className = "" }: { children: React.ReactNode, className?: string }) {
  return (
    <div className={exerciseSection() + " " + className}>
      {children}
    </div>
  );
}

export default {
  exerciseContainer,
  exerciseCard,
  exerciseHeading,
  exerciseSection,
  exerciseOptions,
  answerButton,
  exerciseContentBox,
  navigationButton,
  feedbackMessage,
  ExerciseWrapper,
  ExerciseSectionWrapper
};