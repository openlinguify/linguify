'use client';

import { useAuthContext } from '@/core/auth/AuthAdapter';
import { useSupabaseAuth } from '@/core/auth/SupabaseAuthProvider';
import { supabaseAuthService } from '@/core/auth/supabaseAuthService';
import { useEffect, useState } from 'react';

export default function DebugAuthPage() {
  const authAdapter = useAuthContext();
  const supabaseAuth = useSupabaseAuth();
  const [debugInfo, setDebugInfo] = useState<any>(null);

  useEffect(() => {
    const getDebugInfo = async () => {
      const currentUser = await supabaseAuthService.getCurrentUser();
      const currentSession = await supabaseAuthService.getCurrentSession();
      const accessToken = await supabaseAuthService.getAccessToken();
      
      setDebugInfo({
        currentUser: !!currentUser,
        currentSession: !!currentSession,
        accessToken: !!accessToken,
        userDetails: currentUser,
        sessionDetails: currentSession,
      });
    };

    getDebugInfo();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Debug Authentication</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Auth Adapter State */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Auth Adapter</h2>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span>Is Authenticated:</span>
                <span className={authAdapter.isAuthenticated ? 'text-green-600' : 'text-red-600'}>
                  {authAdapter.isAuthenticated ? 'Yes' : 'No'}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Is Loading:</span>
                <span>{authAdapter.isLoading ? 'Yes' : 'No'}</span>
              </div>
              <div className="flex justify-between">
                <span>Has User:</span>
                <span>{authAdapter.user ? 'Yes' : 'No'}</span>
              </div>
              <div className="flex justify-between">
                <span>Has Token:</span>
                <span>{authAdapter.token ? 'Yes' : 'No'}</span>
              </div>
              {authAdapter.user && (
                <div className="mt-4 p-3 bg-gray-100 rounded">
                  <pre className="text-sm overflow-auto">
                    {JSON.stringify(authAdapter.user, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          </div>

          {/* Supabase Auth State */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Supabase Auth</h2>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span>Has User:</span>
                <span>{supabaseAuth.user ? 'Yes' : 'No'}</span>
              </div>
              <div className="flex justify-between">
                <span>Has Session:</span>
                <span>{supabaseAuth.session ? 'Yes' : 'No'}</span>
              </div>
              <div className="flex justify-between">
                <span>Is Loading:</span>
                <span>{supabaseAuth.loading ? 'Yes' : 'No'}</span>
              </div>
              {supabaseAuth.user && (
                <div className="mt-4 p-3 bg-gray-100 rounded">
                  <pre className="text-sm overflow-auto">
                    {JSON.stringify(supabaseAuth.user, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          </div>

          {/* Debug Info */}
          <div className="bg-white p-6 rounded-lg shadow md:col-span-2">
            <h2 className="text-xl font-semibold mb-4">Service Debug Info</h2>
            {debugInfo ? (
              <div className="space-y-4">
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div className="text-center">
                    <div className="font-medium">Current User</div>
                    <div className={debugInfo.currentUser ? 'text-green-600' : 'text-red-600'}>
                      {debugInfo.currentUser ? 'Found' : 'None'}
                    </div>
                  </div>
                  <div className="text-center">
                    <div className="font-medium">Current Session</div>
                    <div className={debugInfo.currentSession ? 'text-green-600' : 'text-red-600'}>
                      {debugInfo.currentSession ? 'Found' : 'None'}
                    </div>
                  </div>
                  <div className="text-center">
                    <div className="font-medium">Access Token</div>
                    <div className={debugInfo.accessToken ? 'text-green-600' : 'text-red-600'}>
                      {debugInfo.accessToken ? 'Found' : 'None'}
                    </div>
                  </div>
                </div>
                
                {debugInfo.userDetails && (
                  <div>
                    <h3 className="font-medium mb-2">User Details:</h3>
                    <pre className="text-xs bg-gray-100 p-3 rounded overflow-auto">
                      {JSON.stringify(debugInfo.userDetails, null, 2)}
                    </pre>
                  </div>
                )}
                
                {debugInfo.sessionDetails && (
                  <div>
                    <h3 className="font-medium mb-2">Session Details:</h3>
                    <pre className="text-xs bg-gray-100 p-3 rounded overflow-auto">
                      {JSON.stringify(debugInfo.sessionDetails, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            ) : (
              <div>Loading debug info...</div>
            )}
          </div>

          {/* Actions */}
          <div className="bg-white p-6 rounded-lg shadow md:col-span-2">
            <h2 className="text-xl font-semibold mb-4">Actions</h2>
            <div className="flex gap-4">
              <button
                onClick={() => window.location.href = '/'}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Go to Home
              </button>
              <button
                onClick={() => window.location.href = '/login'}
                className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
              >
                Go to Login
              </button>
              <button
                onClick={() => window.location.reload()}
                className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
              >
                Refresh Page
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}