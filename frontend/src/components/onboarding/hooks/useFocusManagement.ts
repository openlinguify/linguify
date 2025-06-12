'use client';

import { useRef, useEffect, useCallback, RefObject } from 'react';

interface FocusManagementOptions {
  // Whether to trap focus in the container
  trapFocus?: boolean;
  // Whether to focus the first focusable element on mount
  autoFocus?: boolean;
  // If set, this element will receive focus instead of the first focusable element
  initialFocusRef?: RefObject<HTMLElement>;
  // If set, this element will receive focus when the trap is deactivated
  finalFocusRef?: RefObject<HTMLElement>;
  // List of selectors to find focusable elements
  focusableSelectors?: string[];
  // Callback when focus trap is activated
  onActivate?: () => void;
  // Callback when focus trap is deactivated
  onDeactivate?: () => void;
}

// Default selectors for focusable elements
const DEFAULT_FOCUSABLE_ELEMENTS = [
  'a[href]',
  'button:not([disabled])',
  'input:not([disabled])',
  'select:not([disabled])',
  'textarea:not([disabled])',
  '[tabindex]:not([tabindex="-1"])',
];

/**
 * A hook to manage focus within a container, including:
 * - Focus trapping (preventing focus from leaving a modal or dialog)
 * - Auto-focusing the first focusable element or a specified element
 * - Restoring focus when the component is unmounted
 */
export function useFocusManagement(options: FocusManagementOptions = {}) {
  const {
    trapFocus = true,
    autoFocus = true,
    initialFocusRef,
    finalFocusRef,
    focusableSelectors = DEFAULT_FOCUSABLE_ELEMENTS,
    onActivate,
    onDeactivate,
  } = options;

  // Ref for the container element
  const containerRef = useRef<HTMLElement | null>(null);
  
  // Keep track of the element that had focus before the trap was activated
  const previouslyFocusedElement = useRef<Element | null>(null);

  // Selector string for finding all focusable elements
  const focusableElementsSelector = focusableSelectors.join(', ');

  // Get all focusable elements within the container
  const getFocusableElements = useCallback(() => {
    if (!containerRef.current) return [];
    return Array.from(
      containerRef.current.querySelectorAll<HTMLElement>(focusableElementsSelector)
    ).filter(el => el.offsetParent !== null); // Filter out hidden elements
  }, [focusableElementsSelector]);

  // Set focus to the first focusable element or to the specified element
  const setInitialFocus = useCallback(() => {
    if (!containerRef.current) return;

    // If an initial focus ref is provided, use that
    if (initialFocusRef?.current) {
      initialFocusRef.current.focus();
      return;
    }

    // Otherwise, find the first focusable element and focus it
    if (autoFocus) {
      const focusableElements = getFocusableElements();
      if (focusableElements.length > 0) {
        focusableElements[0].focus();
      } else {
        // If no focusable elements, focus the container itself
        if (containerRef.current) {
          containerRef.current.focus();
        }
      }
    }
  }, [autoFocus, getFocusableElements, initialFocusRef]);

  // Handle tab key navigation to trap focus
  const handleTabKey = useCallback((e: KeyboardEvent) => {
    if (!trapFocus || !containerRef.current) return;

    const focusableElements = getFocusableElements();
    
    if (focusableElements.length === 0) return;
    
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];
    
    // If shift + tab and on first element, move to last element
    if (e.shiftKey && document.activeElement === firstElement) {
      e.preventDefault();
      lastElement.focus();
    } 
    // If tab and on last element, move to first element
    else if (!e.shiftKey && document.activeElement === lastElement) {
      e.preventDefault();
      firstElement.focus();
    }
  }, [trapFocus, getFocusableElements]);

  // Handle keyboard events for focus management
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if (e.key === 'Tab') {
      handleTabKey(e);
    } else if (e.key === 'Escape' && trapFocus) {
      // Optional escape key handler could be added here
    }
  }, [handleTabKey, trapFocus]);

  // Set up focus management on mount
  useEffect(() => {
    if (!trapFocus) return;

    // Store the currently focused element
    previouslyFocusedElement.current = document.activeElement;

    // Set initial focus after a small delay to allow rendering
    setTimeout(() => {
      setInitialFocus();
    }, 50);

    // Add keyboard event listeners
    document.addEventListener('keydown', handleKeyDown);

    // Notify that focus trap was activated
    onActivate?.();

    return () => {
      // Clean up event listeners
      document.removeEventListener('keydown', handleKeyDown);

      // Capture the current value of finalFocusRef
      const finalFocusElement = finalFocusRef?.current;
      
      // Return focus to the element that had focus before
      if (finalFocusElement) {
        finalFocusElement.focus();
      } else if (previouslyFocusedElement.current instanceof HTMLElement) {
        previouslyFocusedElement.current.focus();
      }

      // Notify that focus trap was deactivated
      onDeactivate?.();
    };
  }, [trapFocus, handleKeyDown, setInitialFocus, onActivate, onDeactivate, finalFocusRef]);

  // When step changes, we need to set focus again
  const refocusOnUpdate = useCallback(() => {
    setInitialFocus();
  }, [setInitialFocus]);

  return {
    containerRef,
    getFocusableElements,
    refocusOnUpdate,
  };
}