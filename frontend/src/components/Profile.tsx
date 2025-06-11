// src/components/Profile.tsx
import { useAuthContext } from '@/core/auth/AuthAdapter';

export default function Profile() {
  const { user, isLoading, getToken } = useAuthContext();

  const fetchData = async () => {
    const token = await getToken();
    const response = await fetch('http://localhost:8000/api/protected', {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    // ... traitement réponse
  };

  if (isLoading) return <div>Loading...</div>;
  
  return (
    <div>
      {user ? (
        <>
          <h1>Welcome {(user as any)?.name}</h1>
          <button onClick={fetchData}>Load Protected Data</button>
        </>
      ) : (
        <a href="/api/auth/login">Login</a>
      )}
    </div>
  );
}