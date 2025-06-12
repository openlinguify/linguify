import { ConnectionTester } from '@/components/debug/ConnectionTester'

export default function DebugConnectionPage() {
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto">
        <h1 className="text-3xl font-bold text-center mb-8">Connection Debug</h1>
        <ConnectionTester />
      </div>
    </div>
  )
}