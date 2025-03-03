// src/app/test-auth/page.tsx
"use client";
import { useEffect, useState } from 'react';

export default function TestAuthPage() {
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<number | null>(null);

  useEffect(() => {
    // Test direct de l'endpoint /api/auth/me
    const testAuth = async () => {
      try {
        console.log('🧪 Testing auth/me endpoint...');
        const res = await fetch('/api/auth/me');
        setStatus(res.status);
        console.log('📊 Status:', res.status);
        
        if (res.ok) {
          const data = await res.json();
          setResult(data);
          console.log('✅ Auth successful!', data);
        } else {
          const errorText = await res.text();
          setError(errorText);
          console.error('❌ Auth failed!', errorText);
        }
      } catch (err) {
        console.error('💥 Fetch error:', err);
        setError(String(err));
      }
    };

    testAuth();
  }, []);

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Testing Authentication</h1>
      <div className="mb-4">
        <div className="font-semibold">Status:</div>
        <div className={`p-2 ${
          status === 200 ? 'bg-green-100' : 
          status ? 'bg-red-100' : 'bg-gray-100'
        }`}>
          {status !== null ? status : 'Loading...'}
        </div>
      </div>
      
      {result && (
        <div className="mb-4">
          <div className="font-semibold">Success Result:</div>
          <pre className="bg-green-100 p-2 rounded overflow-auto max-h-80">
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}
      
      {error && (
        <div className="mb-4">
          <div className="font-semibold">Error:</div>
          <pre className="bg-red-100 p-2 rounded overflow-auto max-h-80">
            {error}
          </pre>
        </div>
      )}

      <div className="mt-8">
        <h2 className="text-xl font-bold mb-2">Debugging Tools</h2>
        <button 
          onClick={() => {
            const authData = localStorage.getItem('auth_state');
            console.log('Auth State:', authData ? JSON.parse(authData) : null);
            alert('Check console for auth state data');
          }}
          className="bg-blue-500 text-white px-4 py-2 rounded mr-2"
        >
          Check localStorage
        </button>
        <button 
          onClick={() => {
            console.log('Cookies:', document.cookie);
            alert('Check console for cookies');
          }}
          className="bg-purple-500 text-white px-4 py-2 rounded"
        >
          Check Cookies
        </button>
      </div>
    </div>
  );
}