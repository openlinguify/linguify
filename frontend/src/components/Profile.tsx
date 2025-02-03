// src/components/Profile.tsx
import useAuth from '../hooks/useAuth';

export default function Profile() {
  const { user, isLoading, getAccessToken } = useAuth();

  const fetchData = async () => {
    const token = await getAccessToken();
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
          <h1>Welcome {user.name}</h1>
          <button onClick={fetchData}>Load Protected Data</button>
        </>
      ) : (
        <a href="/api/auth/login">Login</a>
      )}
    </div>
  );
}