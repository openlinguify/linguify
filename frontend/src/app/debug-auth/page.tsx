'use client'

export default function DebugAuthPage() {
  const debugInfo = {
    supabaseUrl: process.env.NEXT_PUBLIC_SUPABASE_URL,
    hasSupabaseKey: !!process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
    apiUrl: process.env.NEXT_PUBLIC_API_URL,
    nodeEnv: process.env.NODE_ENV,
    isProduction: process.env.NODE_ENV === 'production',
    host: typeof window !== 'undefined' ? window.location.host : 'SSR',
    protocol: typeof window !== 'undefined' ? window.location.protocol : 'SSR',
  }

  // Mask sensitive parts of the URL
  const maskUrl = (url?: string) => {
    if (!url) return 'NOT SET'
    if (url === 'your_supabase_project_url') return 'PLACEHOLDER VALUE'
    try {
      const parsed = new URL(url)
      return `${parsed.protocol}//${parsed.hostname.substring(0, 8)}...`
    } catch {
      return 'INVALID URL'
    }
  }

  return (
    <div className="min-h-screen p-8 bg-gray-50">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-2xl font-bold mb-6">Auth Debug Information</h1>
        
        <div className="bg-white rounded-lg shadow p-6 space-y-4">
          <div>
            <h2 className="font-semibold text-lg mb-2">Environment</h2>
            <dl className="space-y-2">
              <div>
                <dt className="font-medium">Node Environment:</dt>
                <dd className="text-gray-600">{debugInfo.nodeEnv}</dd>
              </div>
              <div>
                <dt className="font-medium">Is Production:</dt>
                <dd className="text-gray-600">{String(debugInfo.isProduction)}</dd>
              </div>
              <div>
                <dt className="font-medium">Host:</dt>
                <dd className="text-gray-600">{debugInfo.host}</dd>
              </div>
            </dl>
          </div>

          <div>
            <h2 className="font-semibold text-lg mb-2">Supabase Configuration</h2>
            <dl className="space-y-2">
              <div>
                <dt className="font-medium">Supabase URL:</dt>
                <dd className={`${!debugInfo.supabaseUrl || debugInfo.supabaseUrl === 'your_supabase_project_url' ? 'text-red-600' : 'text-gray-600'}`}>
                  {maskUrl(debugInfo.supabaseUrl)}
                </dd>
              </div>
              <div>
                <dt className="font-medium">Has Anon Key:</dt>
                <dd className={`${!debugInfo.hasSupabaseKey ? 'text-red-600' : 'text-green-600'}`}>
                  {String(debugInfo.hasSupabaseKey)}
                </dd>
              </div>
            </dl>
          </div>

          <div>
            <h2 className="font-semibold text-lg mb-2">API Configuration</h2>
            <dl className="space-y-2">
              <div>
                <dt className="font-medium">API URL:</dt>
                <dd className="text-gray-600">{debugInfo.apiUrl || 'NOT SET'}</dd>
              </div>
            </dl>
          </div>

          <div className="mt-6 p-4 bg-yellow-50 rounded">
            <p className="text-sm">
              <strong>Note:</strong> Make sure all environment variables are properly set in Vercel:
            </p>
            <ul className="list-disc list-inside mt-2 text-sm space-y-1">
              <li>NEXT_PUBLIC_SUPABASE_URL</li>
              <li>NEXT_PUBLIC_SUPABASE_ANON_KEY</li>
              <li>NEXT_PUBLIC_API_URL (should point to your Render backend)</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}