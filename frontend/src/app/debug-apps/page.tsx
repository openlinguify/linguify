'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/core/api/apiClient';

interface DebugAppData {
  id: number;
  code: string;
  display_name: string;
  is_enabled: boolean;
  user_has_enabled: boolean;
}

interface DebugResponse {
  total_apps: number;
  enabled_by_user: number;
  apps: DebugAppData[];
  enabled_app_codes: string[];
  user_created: boolean;
}

export default function DebugAppsPage() {
  const [debugData, setDebugData] = useState<DebugResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDebugData = async () => {
      try {
        const response = await apiClient.get<DebugResponse>('/api/v1/app-manager/debug/');
        setDebugData(response.data);
      } catch (err) {
        setError('Failed to load debug data');
        console.error('Debug data error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchDebugData();
  }, []);

  if (loading) return <div className="p-8">Loading debug data...</div>;
  if (error) return <div className="p-8 text-red-500">Error: {error}</div>;
  if (!debugData) return <div className="p-8">No data</div>;

  const { apps, total_apps, enabled_by_user, enabled_app_codes, user_created } = debugData;

  // Group by display name to show duplicates
  const groupedByName = apps.reduce((acc, app) => {
    if (!acc[app.display_name]) {
      acc[app.display_name] = [];
    }
    acc[app.display_name].push(app);
    return acc;
  }, {} as Record<string, DebugAppData[]>);

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">🔍 Debug Apps Data</h1>
      
      <div className="grid grid-cols-4 gap-4 mb-8">
        <div className="bg-blue-100 p-4 rounded">
          <h3 className="font-semibold">Total Apps</h3>
          <p className="text-2xl">{total_apps}</p>
        </div>
        <div className="bg-green-100 p-4 rounded">
          <h3 className="font-semibold">Enabled by User</h3>
          <p className="text-2xl">{enabled_by_user}</p>
        </div>
        <div className="bg-yellow-100 p-4 rounded">
          <h3 className="font-semibold">User Created</h3>
          <p className="text-2xl">{user_created ? '✅' : '❌'}</p>
        </div>
        <div className="bg-purple-100 p-4 rounded">
          <h3 className="font-semibold">Enabled Codes</h3>
          <p className="text-sm">{enabled_app_codes.join(', ')}</p>
        </div>
      </div>

      <h2 className="text-2xl font-bold mb-4">🏷️ Apps Grouped by Name (Duplicates)</h2>
      <div className="space-y-6">
        {Object.entries(groupedByName).map(([name, apps]) => (
          <div key={name} className="border rounded-lg p-4">
            <h3 className="text-xl font-semibold mb-3">
              {name} {apps.length > 1 && <span className="text-red-500">({apps.length} duplicates!)</span>}
            </h3>
            <div className="grid grid-cols-1 gap-2">
              {apps.map(app => (
                <div 
                  key={app.id} 
                  className={`p-3 rounded border-l-4 ${
                    app.user_has_enabled 
                      ? 'border-green-500 bg-green-50' 
                      : 'border-gray-300 bg-gray-50'
                  }`}
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <span className="font-mono bg-gray-200 px-2 py-1 rounded text-sm">
                        {app.code}
                      </span>
                      <span className="ml-2 text-sm text-gray-600">ID: {app.id}</span>
                    </div>
                    <div className="flex gap-2">
                      {app.is_enabled ? (
                        <span className="bg-blue-500 text-white px-2 py-1 rounded text-xs">
                          Available
                        </span>
                      ) : (
                        <span className="bg-gray-500 text-white px-2 py-1 rounded text-xs">
                          Disabled
                        </span>
                      )}
                      {app.user_has_enabled ? (
                        <span className="bg-green-500 text-white px-2 py-1 rounded text-xs">
                          User Enabled
                        </span>
                      ) : (
                        <span className="bg-red-500 text-white px-2 py-1 rounded text-xs">
                          User Disabled
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      <h2 className="text-2xl font-bold mb-4 mt-8">📋 All Apps (Raw Data)</h2>
      <div className="overflow-x-auto">
        <table className="min-w-full bg-white border border-gray-300">
          <thead className="bg-gray-100">
            <tr>
              <th className="px-4 py-2 border">ID</th>
              <th className="px-4 py-2 border">Code</th>
              <th className="px-4 py-2 border">Display Name</th>
              <th className="px-4 py-2 border">Available</th>
              <th className="px-4 py-2 border">User Enabled</th>
            </tr>
          </thead>
          <tbody>
            {apps.map(app => (
              <tr key={app.id} className={app.user_has_enabled ? 'bg-green-50' : 'bg-gray-50'}>
                <td className="px-4 py-2 border text-center">{app.id}</td>
                <td className="px-4 py-2 border font-mono">{app.code}</td>
                <td className="px-4 py-2 border">{app.display_name}</td>
                <td className="px-4 py-2 border text-center">
                  {app.is_enabled ? '✅' : '❌'}
                </td>
                <td className="px-4 py-2 border text-center">
                  {app.user_has_enabled ? '✅' : '❌'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}