// src/core/auth/fetchInterceptor.ts
// Debug interceptor to catch invalid fetch parameters

let originalFetch: typeof fetch | undefined;

export function setupFetchInterceptor() {
  if (typeof window === 'undefined') return;
  
  // Only intercept once
  if (originalFetch !== undefined) return;
  
  originalFetch = window.fetch;
  
  window.fetch = function interceptedFetch(input: RequestInfo | URL, init?: RequestInit): Promise<Response> {
    try {
      // Only log in development
      if (process.env.NODE_ENV === 'development') {
        console.log('[FetchInterceptor] Fetch call:', {
          input: typeof input === 'string' ? input : input.toString(),
          method: init?.method || 'GET',
          headers: init?.headers,
          hasBody: !!init?.body
        });
      }

      // Validate input
      if (!input) {
        throw new Error('Fetch input is required');
      }
      
      // Handle empty string input
      if (input === '') {
        console.error('[FetchInterceptor] Empty string URL detected');
        throw new Error('URL cannot be empty');
      }

      // Validate URL if it's a string
      if (typeof input === 'string') {
        try {
          // Check if it's a relative URL
          if (input.startsWith('/')) {
            // For relative URLs, prepend the origin
            const baseUrl = typeof window !== 'undefined' ? window.location.origin : '';
            new URL(input, baseUrl);
          } else {
            // For absolute URLs, validate normally
            new URL(input);
          }
        } catch (e) {
          console.error('[FetchInterceptor] Invalid URL:', input);
          throw new Error(`Invalid URL: ${input}`);
        }
      }

      // Validate and clean headers
      if (init?.headers) {
        const headers = init.headers;
        const cleanHeaders: Record<string, string> = {};
        
        if (headers instanceof Headers) {
          headers.forEach((value, key) => {
            if (value !== null && value !== undefined && value !== '') {
              cleanHeaders[key] = String(value);
            }
          });
          init.headers = cleanHeaders;
        } else if (typeof headers === 'object') {
          Object.entries(headers).forEach(([key, value]) => {
            if (value !== null && value !== undefined && value !== '') {
              cleanHeaders[key] = String(value);
            }
          });
          init.headers = cleanHeaders;
        }
      }

      // Validate body
      if (init?.body !== undefined && init.body !== null) {
        if (typeof init.body !== 'string' && 
            !(init.body instanceof FormData) && 
            !(init.body instanceof URLSearchParams) &&
            !(init.body instanceof Blob) &&
            !(init.body instanceof ArrayBuffer) &&
            !(init.body instanceof ReadableStream)) {
          console.error('[FetchInterceptor] Invalid body type:', typeof init.body, init.body);
          throw new Error(`Invalid body type: ${typeof init.body}`);
        }
      }

      // Create a clean init object to avoid passing invalid values
      const cleanInit: RequestInit = {};
      
      if (init) {
        // Only copy valid properties
        if (init.method) cleanInit.method = init.method;
        if (init.headers) cleanInit.headers = init.headers;
        if (init.body !== undefined && init.body !== null) cleanInit.body = init.body;
        if (init.mode) cleanInit.mode = init.mode;
        if (init.credentials) cleanInit.credentials = init.credentials;
        if (init.cache) cleanInit.cache = init.cache;
        if (init.redirect) cleanInit.redirect = init.redirect;
        if (init.referrer) cleanInit.referrer = init.referrer;
        if (init.referrerPolicy) cleanInit.referrerPolicy = init.referrerPolicy;
        if (init.integrity) cleanInit.integrity = init.integrity;
        if (init.keepalive !== undefined) cleanInit.keepalive = init.keepalive;
        if (init.signal) cleanInit.signal = init.signal;
      }
      
      return originalFetch!(input, cleanInit);
    } catch (error) {
      console.error('[FetchInterceptor] Fetch validation failed:', error);
      throw error;
    }
  };
}

export function restoreFetch() {
  if (typeof window === 'undefined') return;
  if (originalFetch) {
    window.fetch = originalFetch;
  }
}