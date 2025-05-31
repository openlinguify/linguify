'use client';

// Ultra-simple client component
export default function SimplePage() {
  const handleNavigation = (url: string) => {
    window.location.href = url;
  };

  return (
    <div style={{
      fontFamily: 'Arial, sans-serif',
      margin: 0,
      padding: '40px',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      color: 'white',
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    }}>
      <div style={{
        textAlign: 'center',
        background: 'rgba(255, 255, 255, 0.1)',
        padding: '40px',
        borderRadius: '20px',
        backdropFilter: 'blur(10px)',
        boxShadow: '0 20px 40px rgba(0,0,0,0.2)',
        maxWidth: '600px'
      }}>
        <div style={{ fontSize: '4rem', marginBottom: '20px' }}>🎉</div>
        <h1 style={{ 
          fontSize: '3rem', 
          marginBottom: '20px',
          textShadow: '2px 2px 4px rgba(0,0,0,0.3)' 
        }}>
          SUCCÈS !
        </h1>
        
        <div style={{
          background: 'rgba(0, 255, 0, 0.1)',
          border: '2px solid #4ade80',
          padding: '20px',
          borderRadius: '10px',
          margin: '20px 0'
        }}>
          <h2>✅ Accès au SaaS Linguify réussi !</h2>
          <p>Cette page se charge sans aucune redirection ni erreur.</p>
        </div>
        
        <p style={{ fontSize: '1.2rem', marginBottom: '30px', opacity: 0.9 }}>
          Votre application fonctionne maintenant. Le middleware a été désactivé 
          et les boucles de redirection ont été éliminées.
        </p>
        
        <div style={{
          display: 'flex',
          gap: '20px',
          justifyContent: 'center',
          flexWrap: 'wrap'
        }}>
          <button 
            style={{
              padding: '15px 30px',
              fontSize: '1.1rem',
              border: 'none',
              borderRadius: '10px',
              cursor: 'pointer',
              fontWeight: 'bold',
              background: '#3b82f6',
              color: 'white'
            }}
            onClick={() => handleNavigation('/')}
          >
            🏠 Aller à l'accueil
          </button>
          
          <button 
            style={{
              padding: '15px 30px',
              fontSize: '1.1rem',
              border: '2px solid rgba(255, 255, 255, 0.3)',
              borderRadius: '10px',
              cursor: 'pointer',
              fontWeight: 'bold',
              background: 'rgba(255, 255, 255, 0.2)',
              color: 'white'
            }}
            onClick={() => handleNavigation('/login')}
          >
            🔑 Page de connexion
          </button>
          
          <button 
            style={{
              padding: '15px 30px',
              fontSize: '1.1rem',
              border: '2px solid rgba(255, 255, 255, 0.3)',
              borderRadius: '10px',
              cursor: 'pointer',
              fontWeight: 'bold',
              background: 'rgba(255, 255, 255, 0.2)',
              color: 'white'
            }}
            onClick={() => handleNavigation('/debug-auth')}
          >
            🔧 Debug authentification
          </button>
        </div>
        
        <div style={{
          marginTop: '40px', 
          fontSize: '0.9rem', 
          opacity: 0.7
        }}>
          <p>
            💡 <strong>Prochaines étapes :</strong><br/>
            1. Testez la connexion avec vos identifiants<br/>
            2. Naviguez dans l'application<br/>
            3. Une fois tout vérifié, nous réactiverons les protections
          </p>
        </div>
      </div>
    </div>
  );
}