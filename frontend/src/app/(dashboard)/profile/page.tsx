'use client';
import { useRouter } from 'next/navigation';
import { useAuthContext } from "@/services/AuthProvider";
import { useEffect, useState, useRef } from 'react';
import { Camera, Save, X, Loader2 } from 'lucide-react';
import { userApiService } from '@/services/userAPI';
import { Alert, AlertDescription } from "@/components/ui/alert";

export default function MyProfile() {
  const { user, isAuthenticated, updateUser } = useAuthContext();
  const router = useRouter();
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState({
    show: false,
    isError: false,
    message: "",
  });
  
  // États pour le formulaire
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    bio: '',
    gender: '',
    birthday: '',
    native_language: '',
    target_language: '',
    language_level: '',
    objectives: ''
  });

  // Redirect if not authenticated
  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, router]);

  // Charger les données utilisateur
  useEffect(() => {
    if (user) {
      // Initialiser avec les données de base du user
      setFormData({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        email: user.email || '',
        bio: user.bio || '',
        gender: user.gender || '',
        birthday: user.birthday ? new Date(user.birthday).toISOString().split('T')[0] : '',
        native_language: user.native_language || '',
        target_language: user.target_language || '',
        language_level: user.language_level || '',
        objectives: user.objectives || ''
      });
      
      // Essayer de charger des données supplémentaires si nécessaire
      loadUserData();
    }
  }, [user]);

  // Charger les données complètes depuis le service
  const loadUserData = async () => {
    try {
      // Utiliser le nouveau service API
      const userData = await userApiService.getCurrentUser();
      
      // Mettre à jour le formulaire avec les données complètes
      setFormData({
        first_name: userData.first_name || '',
        last_name: userData.last_name || '',
        email: userData.email || '',
        bio: userData.bio || '',
        gender: userData.gender || '',
        birthday: userData.birthday ? new Date(userData.birthday).toISOString().split('T')[0] : '',
        native_language: userData.native_language || '',
        target_language: userData.target_language || '',
        language_level: userData.language_level || '',
        objectives: userData.objectives || ''
      });
    } catch (error) {
      console.error("Erreur lors du chargement des données utilisateur:", error);
    }
  };

  // Show loading state while checking authentication
  if (!isAuthenticated || !user) {
    return <div className="max-w-2xl mx-auto p-6 bg-white shadow rounded-lg mt-10">Chargement...</div>;
  }

  // Format le nom complet
  const fullName = `${user.first_name || ''} ${user.last_name || ''}`.trim() || user.username;
  
  // Fonction pour ouvrir le sélecteur de fichier
  const handleProfilePictureClick = () => {
    fileInputRef.current?.click();
  };

  // Fonction pour gérer l'upload de la photo
  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    try {
      setUploading(true);
      
      // Utiliser le nouveau service pour l'upload de photo
      const result = await userApiService.uploadProfilePicture(file);
      
      // Mettre à jour l'utilisateur dans le contexte
      if (updateUser && result.profile_picture) {
        updateUser({
          ...user,
          profile_picture: result.profile_picture
        });
      } else {
        window.location.reload();
      }
      
      setSaveStatus({
        show: true,
        isError: false,
        message: "Photo de profil mise à jour avec succès",
      });
      
      // Masquer le message après quelques secondes
      setTimeout(() => {
        setSaveStatus(prev => ({ ...prev, show: false }));
      }, 3000);
      
    } catch (error) {
      console.error('Erreur:', error);
      setSaveStatus({
        show: true,
        isError: true,
        message: "Une erreur est survenue lors de l'upload de votre photo",
      });
    } finally {
      setUploading(false);
    }
  };

  // Gérer les changements dans le formulaire
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

const handleSaveChanges = async () => {
  try {
    setIsSaving(true);
    setSaveStatus({ show: false, isError: false, message: "" });
    
    // Utiliser directement la bonne URL
    const response = await fetch('http://localhost:8000/api/auth/me/', {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: JSON.stringify({
        first_name: formData.first_name,
        last_name: formData.last_name,
        bio: formData.bio,
        gender: formData.gender,
        birthday: formData.birthday,
        native_language: formData.native_language,
        target_language: formData.target_language,
        language_level: formData.language_level,
        objectives: formData.objectives
      }),
      credentials: 'include'
    });
    
    if (!response.ok) {
      throw new Error(`Erreur HTTP: ${response.status}`);
    }
    
    const updatedUser = await response.json();
    
    // Mettre à jour l'utilisateur dans le contexte
    if (updateUser) {
      updateUser({
        ...user,
        ...updatedUser
      });
    }
    
    setSaveStatus({
      show: true,
      isError: false,
      message: "Profil mis à jour avec succès",
    });
    
    setIsEditing(false);
  } catch (error) {
    console.error('Erreur complète:', error);
    setSaveStatus({
      show: true, 
      isError: true,
      message: `Erreur: ${error.message || "Une erreur est survenue"}`,
    });
  } finally {
    setIsSaving(false);
    setTimeout(() => {
      setSaveStatus(prev => ({ ...prev, show: false }));
    }, 3000);
  }
};

  // Options pour les sélecteurs
  const languageOptions = [
    { value: "EN", label: "English" },
    { value: "FR", label: "French" },
    { value: "NL", label: "Dutch" },
    { value: "DE", label: "German" },
    { value: "ES", label: "Spanish" },
    { value: "IT", label: "Italian" },
    { value: "PT", label: "Portuguese" },
  ];

  const levelOptions = [
    { value: "A1", label: "A1 - Débutant" },
    { value: "A2", label: "A2 - Élémentaire" },
    { value: "B1", label: "B1 - Intermédiaire" },
    { value: "B2", label: "B2 - Intermédiaire avancé" },
    { value: "C1", label: "C1 - Avancé" },
    { value: "C2", label: "C2 - Maîtrise" },
  ];

  const genderOptions = [
    { value: "M", label: "Homme" },
    { value: "F", label: "Femme" },
  ];

  const objectivesOptions = [
    { value: "Travel", label: "Voyage" },
    { value: "Business", label: "Business" },
    { value: "Live Abroad", label: "Vivre à l'étranger" },
    { value: "Exam", label: "Examen" },
    { value: "For Fun", label: "Pour le plaisir" },
    { value: "Work", label: "Travail" },
    { value: "School", label: "École" },
    { value: "Study", label: "Études" },
    { value: "Personal", label: "Personnel" },
  ];

  return (
    <div className="max-w-3xl mx-auto p-6 bg-white shadow rounded-lg mt-10">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Profil</h1>
        {!isEditing ? (
          <button 
            className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded"
            onClick={() => setIsEditing(true)}
          >
            Modifier
          </button>
        ) : (
          <div className="flex gap-2">
            <button 
              className="bg-gray-200 hover:bg-gray-300 text-gray-800 px-4 py-2 rounded flex items-center"
              onClick={() => setIsEditing(false)}
            >
              <X className="w-4 h-4 mr-1" /> Annuler
            </button>
            <button 
              className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded flex items-center"
              onClick={handleSaveChanges}
              disabled={isSaving}
            >
              {isSaving ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Save className="w-4 h-4 mr-1" />
              )}
              Enregistrer
            </button>
          </div>
        )}
      </div>

      {saveStatus.show && (
        <Alert
          className={`mb-6 ${saveStatus.isError ? 'bg-red-100 border-red-400' : 'bg-green-100 border-green-400'}`}
        >
          <AlertDescription>{saveStatus.message}</AlertDescription>
        </Alert>
      )}

      <div className="flex items-center mb-6">
        {/* Photo de profil avec upload */}
        <div 
          className="relative w-24 h-24 rounded-full overflow-hidden border-2 border-gray-200 mr-4 cursor-pointer"
          onClick={handleProfilePictureClick}
        >
          {user.profile_picture ? (
            <img 
              src={user.profile_picture} 
              alt="Photo de profil"
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full bg-gray-300 flex items-center justify-center">
              <span className="text-2xl text-gray-500">
                {fullName.charAt(0).toUpperCase()}
              </span>
            </div>
          )}
          
          <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-40 opacity-0 hover:opacity-100 transition-opacity">
            <Camera className="w-6 h-6 text-white" />
          </div>
          
          {uploading && (
            <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-60">
              <div className="w-6 h-6 border-2 border-t-blue-500 border-r-transparent border-b-transparent border-l-transparent rounded-full animate-spin"></div>
            </div>
          )}
        </div>
        
        {/* Input file caché */}
        <input 
          type="file" 
          ref={fileInputRef} 
          onChange={handleFileChange} 
          className="hidden" 
          accept="image/*"
        />
        
        <div>
          <h2 className="text-xl font-medium">{fullName}</h2>
          <p className="text-gray-600">{user.email}</p>
        </div>
      </div>
      
      {!isEditing ? (
        // Mode affichage
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <InfoItem label="Nom d'utilisateur" value={user.username} />
          <InfoItem label="Prénom" value={user.first_name || 'Non spécifié'} />
          <InfoItem label="Nom" value={user.last_name || 'Non spécifié'} />
          <InfoItem label="Email" value={user.email} />
          <InfoItem label="Genre" value={
            genderOptions.find(opt => opt.value === user.gender)?.label || 'Non spécifié'
          } />
          <InfoItem label="Date de naissance" value={user.birthday ? new Date(user.birthday).toLocaleDateString() : 'Non spécifiée'} />
          <InfoItem label="Langue maternelle" value={
            languageOptions.find(opt => opt.value === user.native_language)?.label || 'Non spécifiée'
          } />
          <InfoItem label="Langue cible" value={
            languageOptions.find(opt => opt.value === user.target_language)?.label || 'Non spécifiée'
          } />
          <InfoItem label="Niveau" value={
            levelOptions.find(opt => opt.value === user.language_level)?.label || 'Non spécifié'
          } />
          <InfoItem label="Objectif" value={
            objectivesOptions.find(opt => opt.value === user.objectives)?.label || 'Non spécifié'
          } />
          <InfoItem label="Membre depuis" value={new Date(user.created_at).toLocaleDateString()} />
          
          <div className="col-span-2">
            <h3 className="text-lg font-semibold mb-2">Biographie</h3>
            <p className="text-gray-700">{user.bio || 'Aucune biographie disponible'}</p>
          </div>
        </div>
      ) : (
        // Mode édition
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="first_name">
              Prénom
            </label>
            <input
              type="text"
              id="first_name"
              name="first_name"
              value={formData.first_name}
              onChange={handleInputChange}
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            />
          </div>
          
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="last_name">
              Nom
            </label>
            <input
              type="text"
              id="last_name"
              name="last_name"
              value={formData.last_name}
              onChange={handleInputChange}
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            />
          </div>
          
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="email">
              Email
            </label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              disabled
              className="shadow appearance-none border rounded w-full py-2 px-3 bg-gray-50 text-gray-700 leading-tight"
            />
          </div>
          
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="gender">
              Genre
            </label>
            <select
              id="gender"
              name="gender"
              value={formData.gender}
              onChange={handleInputChange}
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            >
              <option value="">Sélectionnez...</option>
              {genderOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
          
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="birthday">
              Date de naissance
            </label>
            <input
              type="date"
              id="birthday"
              name="birthday"
              value={formData.birthday}
              onChange={handleInputChange}
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            />
          </div>
          
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="native_language">
              Langue maternelle
            </label>
            <select
              id="native_language"
              name="native_language"
              value={formData.native_language}
              onChange={handleInputChange}
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            >
              <option value="">Sélectionnez...</option>
              {languageOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
          
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="target_language">
              Langue cible
            </label>
            <select
              id="target_language"
              name="target_language"
              value={formData.target_language}
              onChange={handleInputChange}
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            >
              <option value="">Sélectionnez...</option>
              {languageOptions.map(option => (
                <option 
                  key={option.value} 
                  value={option.value}
                  disabled={option.value === formData.native_language}
                >
                  {option.label}
                </option>
              ))}
            </select>
          </div>
          
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="language_level">
              Niveau
            </label>
            <select
              id="language_level"
              name="language_level"
              value={formData.language_level}
              onChange={handleInputChange}
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            >
              <option value="">Sélectionnez...</option>
              {levelOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
          
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="objectives">
              Objectif d'apprentissage
            </label>
            <select
              id="objectives"
              name="objectives"
              value={formData.objectives}
              onChange={handleInputChange}
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            >
              <option value="">Sélectionnez...</option>
              {objectivesOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
          
          <div className="col-span-2 mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="bio">
              Biographie
            </label>
            <textarea
              id="bio"
              name="bio"
              value={formData.bio}
              onChange={handleInputChange}
              rows={3}
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            ></textarea>
          </div>
        </div>
      )}
    </div>
  );
}

// Composant pour afficher une ligne d'information
function InfoItem({ label, value }: { label: string, value: string }) {
  return (
    <div className="mb-4">
      <p className="text-sm font-medium text-gray-500">{label}</p>
      <p className="text-gray-800">{value}</p>
    </div>
  );
}