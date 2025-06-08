'use client'

export default function DebugEnvPage() {
  // Check environment variables
  const envVars = {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    NEXT_PUBLIC_SUPABASE_URL: process.env.NEXT_PUBLIC_SUPABASE_URL,
    NEXT_PUBLIC_SUPABASE_ANON_KEY: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
  }

  // Check if Supabase variables are set
  const supabaseConfigured = !!(envVars.NEXT_PUBLIC_SUPABASE_URL && envVars.NEXT_PUBLIC_SUPABASE_ANON_KEY)

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Environment Debug</h1>
      
      <div className="space-y-4">
        <div>
          <h2 className="text-xl font-semibold mb-2">API Configuration</h2>
          <p className="font-mono bg-gray-100 p-2 rounded">
            NEXT_PUBLIC_API_URL: {envVars.NEXT_PUBLIC_API_URL || <span className="text-red-500">NOT SET</span>}
          </p>
        </div>

        <div>
          <h2 className="text-xl font-semibold mb-2">Supabase Configuration</h2>
          <div className="space-y-2">
            <p className="font-mono bg-gray-100 p-2 rounded">
              NEXT_PUBLIC_SUPABASE_URL: {envVars.NEXT_PUBLIC_SUPABASE_URL ? 
                <span className="text-green-500">SET ✓</span> : 
                <span className="text-red-500">NOT SET</span>}
            </p>
            <p className="font-mono bg-gray-100 p-2 rounded">
              NEXT_PUBLIC_SUPABASE_ANON_KEY: {envVars.NEXT_PUBLIC_SUPABASE_ANON_KEY ? 
                <span className="text-green-500">SET ✓</span> : 
                <span className="text-red-500">NOT SET</span>}
            </p>
          </div>
        </div>

        <div className={`p-4 rounded ${supabaseConfigured ? 'bg-green-100' : 'bg-red-100'}`}>
          <p className="font-semibold">
            Supabase Status: {supabaseConfigured ? 
              <span className="text-green-700">Configured ✓</span> : 
              <span className="text-red-700">Missing Configuration ✗</span>}
          </p>
          {!supabaseConfigured && (
            <p className="mt-2 text-sm">
              Please set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY in your .env.local file
            </p>
          )}
        </div>
      </div>

      <div className="mt-8">
        <h2 className="text-xl font-semibold mb-2">Quick Actions</h2>
        <button 
          onClick={() => {
            localStorage.clear()
            sessionStorage.clear()
            alert('Local storage and session storage cleared!')
          }}
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        >
          Clear All Storage
        </button>
      </div>
    </div>
  )
}