'use client';

import React, { useEffect, useState } from 'react';

interface A11yAnnouncerProps {
  message: string;
  assertive?: boolean;
  clearDelay?: number;
}

/**
 * Screen reader announcer component that uses ARIA live regions
 * to announce dynamic changes to users of assistive technologies.
 * 
 * This component renders a visually hidden element that announces
 * messages to screen readers.
 */
const A11yAnnouncer: React.FC<A11yAnnouncerProps> = ({
  message,
  assertive = false,
  clearDelay = 5000, // Clear message after 5 seconds
}) => {
  const [announcement, setAnnouncement] = useState<string>(message);

  // Update announcement when message changes
  useEffect(() => {
    if (message) {
      setAnnouncement(message);
      
      // Clear the announcement after a delay for better screen reader behavior
      const timer = setTimeout(() => {
        setAnnouncement('');
      }, clearDelay);
      
      return () => clearTimeout(timer);
    }
  }, [message, clearDelay]);

  return (
    <div
      aria-live={assertive ? 'assertive' : 'polite'}
      aria-atomic="true"
      className="sr-only"
    >
      {announcement}
    </div>
  );
};

export default A11yAnnouncer;