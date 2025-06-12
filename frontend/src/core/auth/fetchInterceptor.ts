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
      // Log the fetch call for debugging
      console.log('[FetchInterceptor] Fetch call:', {
        input: typeof input === 'string' ? input : input.toString(),
        method: init?.method || 'GET',
        headers: init?.headers,
        hasBody: !!init?.body
      });

      // Validate input
      if (!input) {
        throw new Error('Fetch input is required');
      }

      // Validate URL if it's a string
      if (typeof input === 'string') {
        try {
          new URL(input);
        } catch (e) {
          console.error('[FetchInterceptor] Invalid URL:', input);
          throw new Error(`Invalid URL: ${input}`);
        }
      }

      // Validate headers
      if (init?.headers) {
        const headers = init.headers;
        if (headers instanceof Headers) {
          headers.forEach((value, key) => {
            if (value === null || value === undefined) {
              console.error('[FetchInterceptor] Invalid header value:', { key, value });
              throw new Error(`Invalid header value for ${key}: ${value}`);
            }
          });
        } else if (typeof headers === 'object') {
          Object.entries(headers).forEach(([key, value]) => {
            if (value === null || value === undefined) {
              console.error('[FetchInterceptor] Invalid header value:', { key, value });
              throw new Error(`Invalid header value for ${key}: ${value}`);
            }
          });
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

      return originalFetch!(input, init);
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