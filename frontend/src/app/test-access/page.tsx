'use client';

export default function TestAccessPage() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="max-w-2xl mx-auto p-8 bg-white rounded-lg shadow-lg">
        <div className="text-center">
          <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100">
            <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          
          <h1 className="mt-4 text-3xl font-bold text-gray-900">
            🎉 Accès au SaaS réussi !
          </h1>
          
          <p className="mt-2 text-lg text-gray-600">
            Félicitations ! Vous pouvez maintenant accéder à votre application Linguify.
          </p>
          
          <div className="mt-8 space-y-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <h2 className="text-lg font-semibold text-blue-900">Pages disponibles :</h2>
              <div className="mt-2 grid grid-cols-2 gap-2 text-sm">
                <a href="/" className="text-blue-600 hover:text-blue-800">🏠 Accueil</a>
                <a href="/learning" className="text-blue-600 hover:text-blue-800">📚 Apprentissage</a>
                <a href="/flashcard" className="text-blue-600 hover:text-blue-800">🧠 Flashcards</a>
                <a href="/notebook" className="text-blue-600 hover:text-blue-800">📝 Notes</a>
                <a href="/settings" className="text-blue-600 hover:text-blue-800">⚙️ Paramètres</a>
                <a href="/debug-auth" className="text-blue-600 hover:text-blue-800">🔧 Debug Auth</a>
              </div>
            </div>
            
            <div className="bg-yellow-50 p-4 rounded-lg">
              <h3 className="text-lg font-semibold text-yellow-900">Note :</h3>
              <p className="mt-1 text-sm text-yellow-800">
                Les redirections automatiques ont été temporairement désactivées pour résoudre 
                le problème de boucle infinie. Une fois que l'authentification fonctionne correctement, 
                ces protections seront réactivées.
              </p>
            </div>
          </div>
          
          <div className="mt-8 flex justify-center space-x-4">
            <button
              onClick={() => window.location.href = '/'}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Aller à l'accueil
            </button>
            <button
              onClick={() => window.location.href = '/debug-auth'}
              className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              Vérifier l'auth
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}