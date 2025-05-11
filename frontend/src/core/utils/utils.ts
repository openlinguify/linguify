import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Convert a base64 URL-safe string to a Uint8Array
 * Used for converting VAPID public keys for push notifications
 *
 * @param base64String The base64 URL-safe string to convert
 * @returns Uint8Array representation of the input
 */
export function base64UrlToUint8Array(base64String: string): Uint8Array {
  // Replace URL-safe characters to standard base64 characters
  const base64 = base64String
    .replace(/-/g, '+')
    .replace(/_/g, '/');

  // Add padding if needed
  const padLength = 4 - (base64.length % 4);
  const padded = padLength < 4 ? base64 + '='.repeat(padLength) : base64;

  // Convert to binary string
  const raw = atob(padded);

  // Convert to Uint8Array
  const output = new Uint8Array(raw.length);
  for (let i = 0; i < raw.length; i++) {
    output[i] = raw.charCodeAt(i);
  }

  return output;
}

/**
 * Format a date string or timestamp into a human-readable format
 *
 * @param dateInput The date string, timestamp, or Date object
 * @param format The desired format ('relative', 'short', or 'full')
 * @returns Formatted date string
 */
export function formatDate(
  dateInput: string | number | Date,
  format: 'relative' | 'short' | 'full' = 'short'
): string {
  const date = new Date(dateInput);

  if (isNaN(date.getTime())) {
    return 'Invalid date';
  }

  // For relative time format (e.g., "2 hours ago")
  if (format === 'relative') {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffSec = Math.floor(diffMs / 1000);
    const diffMin = Math.floor(diffSec / 60);
    const diffHour = Math.floor(diffMin / 60);
    const diffDay = Math.floor(diffHour / 24);

    if (diffSec < 60) {
      return 'just now';
    } else if (diffMin < 60) {
      return `${diffMin} ${diffMin === 1 ? 'minute' : 'minutes'} ago`;
    } else if (diffHour < 24) {
      return `${diffHour} ${diffHour === 1 ? 'hour' : 'hours'} ago`;
    } else if (diffDay < 7) {
      return `${diffDay} ${diffDay === 1 ? 'day' : 'days'} ago`;
    }
  }

  // For short format (e.g., "Jan 1, 2023")
  if (format === 'short') {
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    }).format(date);
  }

  // For full format (e.g., "January 1, 2023, 12:00 PM")
  return new Intl.DateTimeFormat('en-US', {
    month: 'long',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: 'numeric',
    hour12: true
  }).format(date);
}
