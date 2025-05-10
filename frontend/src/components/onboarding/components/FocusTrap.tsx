'use client';

import React, { useEffect, useRef } from 'react';

interface FocusTrapProps {
  children: React.ReactNode;
  isActive?: boolean;
  returnFocusOnDeactivate?: boolean;
  autoFocus?: boolean;
  onEscape?: () => void;
}

/**
 * FocusTrap - A component that traps focus within its children
 *
 * This ensures keyboard navigation stays within the component and doesn't
 * escape to other elements on the page. It's particularly useful for modals,
 * dialogs, and other overlay components.
 */
const FocusTrap: React.FC<FocusTrapProps> = ({
  children,
  isActive = true,
  returnFocusOnDeactivate = true,
  autoFocus = true,
  onEscape,
}) => {
  const rootRef = useRef<HTMLDivElement>(null);
  const previouslyFocusedElement = useRef<Element | null>(null);

  // List of selectors for focusable elements
  const focusableElements = [
    'a[href]',
    'button:not([disabled])',
    'input:not([disabled])',
    'select:not([disabled])',
    'textarea:not([disabled])',
    '[tabindex]:not([tabindex="-1"])',
  ].join(', ');

  // Store the previously focused element
  useEffect(() => {
    if (isActive) {
      previouslyFocusedElement.current = document.activeElement;
    }
  }, [isActive]);

  // Auto-focus the first focusable element when the trap becomes active
  useEffect(() => {
    if (!isActive || !rootRef.current) return;

    // Small delay to ensure the DOM is fully rendered
    const timeoutId = setTimeout(() => {
      if (autoFocus && rootRef.current) {
        const focusableElementsInside = rootRef.current.querySelectorAll<HTMLElement>(focusableElements);
        
        if (focusableElementsInside.length > 0) {
          focusableElementsInside[0].focus();
        } else {
          // If no focusable elements, focus the container itself
          rootRef.current.setAttribute('tabindex', '-1');
          rootRef.current.focus();
        }
      }
    }, 50);

    return () => clearTimeout(timeoutId);
  }, [isActive, autoFocus, focusableElements]);

  // Return focus to the previously focused element when the trap is deactivated
  useEffect(() => {
    return () => {
      if (returnFocusOnDeactivate && previouslyFocusedElement.current instanceof HTMLElement) {
        previouslyFocusedElement.current.focus();
      }
    };
  }, [returnFocusOnDeactivate]);

  // Handle tab key navigation
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isActive || !rootRef.current) return;

    // Handle escape key
    if (e.key === 'Escape' && onEscape) {
      e.preventDefault();
      onEscape();
      return;
    }

    // Handle tab key for focus trapping
    if (e.key === 'Tab') {
      const focusableElementsInside = Array.from(
        rootRef.current.querySelectorAll<HTMLElement>(focusableElements)
      ).filter(el => el.offsetParent !== null); // Filter out hidden elements
      
      if (focusableElementsInside.length === 0) return;
      
      const firstElement = focusableElementsInside[0];
      const lastElement = focusableElementsInside[focusableElementsInside.length - 1];
      
      // Shift + Tab on first element goes to last element
      if (e.shiftKey && document.activeElement === firstElement) {
        e.preventDefault();
        lastElement.focus();
      }
      // Tab on last element goes to first element
      else if (!e.shiftKey && document.activeElement === lastElement) {
        e.preventDefault();
        firstElement.focus();
      }
    }
  };

  if (!isActive) {
    return <>{children}</>;
  }

  return (
    <div ref={rootRef} onKeyDown={handleKeyDown}>
      {children}
    </div>
  );
};

export default FocusTrap;