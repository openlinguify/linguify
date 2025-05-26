'use client';

import React, { useState } from 'react';
import { 
  getCookieConsent, 
  getConsentFromBackend,
  revokeConsentOnBackend,
  checkConsentValidityOnBackend,
  type BackendCookieConsent 
} from '@/core/utils/cookieUtils';

export const CookieTestPanel: React.FC = () => {
  const [localConsent, setLocalConsent] = useState<any>(null);
  const [backendConsent, setBackendConsent] = useState<BackendCookieConsent | null>(null);
  const [apiStatus, setApiStatus] = useState<string>('');

  const handleClearLocal = () => {
    localStorage.removeItem('linguify_consent');
    setLocalConsent(null);
    setApiStatus('LocalStorage cleared');
    // Reload page to show banner
    setTimeout(() => window.location.reload(), 1000);
  };

  const handleCheckLocal = () => {
    const consent = getCookieConsent();
    setLocalConsent(consent);
    setApiStatus('Local consent checked');
  };

  const handleCheckBackend = async () => {
    try {
      const consent = await getConsentFromBackend();
      setBackendConsent(consent);
      setApiStatus('Backend consent retrieved');
    } catch (error) {
      setApiStatus(`Backend error: ${error}`);
    }
  };

  const handleRevokeBackend = async () => {
    try {
      const success = await revokeConsentOnBackend('testing');
      setApiStatus(success ? 'Consent revoked on backend' : 'Failed to revoke');
      // Clear local storage too
      localStorage.removeItem('linguify_consent');
      setTimeout(() => window.location.reload(), 1000);
    } catch (error) {
      setApiStatus(`Revoke error: ${error}`);
    }
  };

  const handleTestAnalytics = async () => {
    try {
      const hasConsent = await checkConsentValidityOnBackend('analytics');
      setApiStatus(`Analytics consent: ${hasConsent ? 'YES' : 'NO'}`);
    } catch (error) {
      setApiStatus(`Analytics check error: ${error}`);
    }
  };

  const handleDebugAPI = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/auth/cookie-consent/debug/');
      if (response.ok) {
        const data = await response.json();
        setApiStatus('Debug API works!');
        console.log('Debug data:', data);
      } else {
        setApiStatus(`Debug API error: ${response.status}`);
      }
    } catch (error) {
      setApiStatus(`Debug API failed: ${error}`);
    }
  };

  return (
    <div className="fixed bottom-4 right-4 z-50 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg p-4 max-w-md">
      <h3 className="text-lg font-semibold mb-3 text-gray-900 dark:text-white">
        🍪 Cookie Test Panel
      </h3>
      
      <div className="space-y-2 mb-4">
        <button
          onClick={handleClearLocal}
          className="w-full px-3 py-2 bg-red-500 text-white rounded hover:bg-red-600 text-sm"
        >
          🗑️ Clear Local & Reload
        </button>
        
        <button
          onClick={handleCheckLocal}
          className="w-full px-3 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 text-sm"
        >
          📱 Check Local Storage
        </button>
        
        <button
          onClick={handleCheckBackend}
          className="w-full px-3 py-2 bg-green-500 text-white rounded hover:bg-green-600 text-sm"
        >
          🌐 Check Backend API
        </button>
        
        <button
          onClick={handleRevokeBackend}
          className="w-full px-3 py-2 bg-orange-500 text-white rounded hover:bg-orange-600 text-sm"
        >
          ❌ Revoke Backend & Reload
        </button>
        
        <button
          onClick={handleTestAnalytics}
          className="w-full px-3 py-2 bg-purple-500 text-white rounded hover:bg-purple-600 text-sm"
        >
          📊 Test Analytics API
        </button>
        
        <button
          onClick={handleDebugAPI}
          className="w-full px-3 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 text-sm"
        >
          🔍 Test Debug API
        </button>
      </div>

      {apiStatus && (
        <div className="mb-3 p-2 bg-gray-100 dark:bg-gray-700 rounded text-xs">
          <strong>Status:</strong> {apiStatus}
        </div>
      )}

      {localConsent && (
        <div className="mb-3 p-2 bg-blue-50 dark:bg-blue-900/20 rounded text-xs">
          <strong>Local:</strong>
          <pre className="mt-1 text-xs overflow-x-auto">
            {JSON.stringify(localConsent, null, 2)}
          </pre>
        </div>
      )}

      {backendConsent && (
        <div className="p-2 bg-green-50 dark:bg-green-900/20 rounded text-xs">
          <strong>Backend:</strong>
          <pre className="mt-1 text-xs overflow-x-auto">
            {JSON.stringify(backendConsent, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};