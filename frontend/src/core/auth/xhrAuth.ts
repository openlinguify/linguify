// Authentication using XMLHttpRequest to completely avoid fetch issues
export async function xhrSignIn(email: string, password: string): Promise<any> {
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
  let supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
  
  // Clean the API key - remove any whitespace/newlines that might have been added
  if (supabaseAnonKey) {
    supabaseAnonKey = supabaseAnonKey.replace(/\s+/g, '').trim();
  }
  
  if (!supabaseUrl || !supabaseAnonKey) {
    console.error('[XHRAuth] Missing environment variables');
    return { 
      error: { 
        message: 'Authentication service not configured',
        status: 500 
      } 
    };
  }
  
  return new Promise((resolve) => {
    try {
      console.log('[XHRAuth] Using XMLHttpRequest for authentication...');
      
      const xhr = new XMLHttpRequest();
      const url = `${supabaseUrl}/auth/v1/token?grant_type=password`;
      
      xhr.open('POST', url, true);
      xhr.setRequestHeader('Content-Type', 'application/json');
      xhr.setRequestHeader('apikey', supabaseAnonKey);
      xhr.setRequestHeader('Authorization', `Bearer ${supabaseAnonKey}`);
      
      xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
          console.log('[XHRAuth] Response received:', xhr.status);
          
          try {
            const data = JSON.parse(xhr.responseText);
            
            if (xhr.status >= 200 && xhr.status < 300) {
              resolve({
                user: data.user,
                session: {
                  access_token: data.access_token,
                  refresh_token: data.refresh_token,
                  expires_at: data.expires_at,
                  expires_in: data.expires_in,
                  token_type: data.token_type,
                  user: data.user
                }
              });
            } else {
              resolve({
                error: {
                  message: data.error_description || data.message || `HTTP ${xhr.status}`,
                  status: xhr.status
                }
              });
            }
          } catch (parseError) {
            resolve({
              error: {
                message: 'Failed to parse response',
                status: xhr.status
              }
            });
          }
        }
      };
      
      xhr.onerror = function() {
        console.error('[XHRAuth] Network error');
        resolve({
          error: {
            message: 'Network error',
            status: 0
          }
        });
      };
      
      const body = JSON.stringify({ email, password });
      xhr.send(body);
      
    } catch (error) {
      console.error('[XHRAuth] Error:', error);
      resolve({
        error: {
          message: error instanceof Error ? error.message : 'Authentication failed',
          status: 500
        }
      });
    }
  });
}