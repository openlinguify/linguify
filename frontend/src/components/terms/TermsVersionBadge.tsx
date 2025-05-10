import React from 'react';
import { useTermsAcceptance } from '@/core/hooks/useTermsAcceptance';

interface TermsVersionBadgeProps {
  variant?: 'default' | 'compact' | 'detailed';
  className?: string;
}

/**
 * A component that displays the currently accepted terms version
 * with optional details about when they were accepted.
 */
export default function TermsVersionBadge({
  variant = 'default',
  className = '',
}: TermsVersionBadgeProps) {
  const { termsAccepted, termsVersion, termsAcceptedAt } = useTermsAcceptance();
  
  if (!termsAccepted) {
    return (
      <span className={`inline-flex items-center rounded-full bg-red-100 px-2.5 py-0.5 text-xs font-medium text-red-800 ${className}`}>
        Terms Not Accepted
      </span>
    );
  }

  // Format the acceptance date if available
  const formattedDate = termsAcceptedAt 
    ? new Date(termsAcceptedAt).toLocaleDateString() 
    : 'Unknown date';
  
  // Render different variants
  switch (variant) {
    case 'compact':
      return (
        <span className={`inline-flex items-center rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-800 ${className}`}>
          {termsVersion || 'v1.0'}
        </span>
      );
      
    case 'detailed':
      return (
        <div className={`inline-flex flex-col rounded-md border border-green-200 bg-green-50 px-3 py-1.5 ${className}`}>
          <span className="text-sm font-medium text-green-800">
            Terms Accepted: {termsVersion || 'v1.0'}
          </span>
          <span className="text-xs text-green-600">
            Accepted on {formattedDate}
          </span>
        </div>
      );
      
    default:
      return (
        <span className={`inline-flex items-center rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-800 ${className}`}>
          Terms Accepted: {termsVersion || 'v1.0'}
        </span>
      );
  }
}