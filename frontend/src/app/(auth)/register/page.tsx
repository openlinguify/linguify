"use client";

import { useAuth } from "@/providers/AuthProvider";
import { useRouter } from "next/navigation";
import React from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { LoaderCircle } from "lucide-react";

// Mapping des langues basé sur le modèle backend
const LANGUAGE_OPTIONS = [
  { value: 'EN', label: 'English' },
  { value: 'FR', label: 'French' },
  { value: 'NL', label: 'Dutch' },
  { value: 'DE', label: 'German' },
  { value: 'ES', label: 'Spanish' },
  { value: 'IT', label: 'Italian' },
  { value: 'PT', label: 'Portuguese' },
];

const LEVEL_OPTIONS = [
  { value: 'A1', label: 'A1 - Débutant' },
  { value: 'A2', label: 'A2 - Élémentaire' },
  { value: 'B1', label: 'B1 - Intermédiaire' },
  { value: 'B2', label: 'B2 - Intermédiaire supérieur' },
  { value: 'C1', label: 'C1 - Avancé' },
  { value: 'C2', label: 'C2 - Maîtrise' },
];

const OBJECTIVES_OPTIONS = [
  { value: 'Travel', label: 'Voyage' },
  { value: 'Business', label: 'Affaires' },
  { value: 'Live Abroad', label: 'Vivre à l\'étranger' },
  { value: 'Exam', label: 'Préparation d\'examen' },
  { value: 'For Fun', label: 'Pour le plaisir' },
  { value: 'Work', label: 'Travail' },
  { value: 'School', label: 'École' },
  { value: 'Study', label: 'Études' },
  { value: 'Personal', label: 'Développement personnel' },
];

export default function RegisterPage() {
  const { login, isAuthenticated } = useAuth();
  const router = useRouter();
  const [error, setError] = React.useState<string | null>(null);
  const [isLoading, setIsLoading] = React.useState(false);
  const [activeTab, setActiveTab] = React.useState<string>("form");
  
  // États pour le formulaire d'inscription
  const [formData, setFormData] = React.useState({
    firstName: "",
    lastName: "",
    username: "",
    email: "",
    nativeLanguage: "",
    targetLanguage: "",
    languageLevel: "",
    objectives: "",
    bio: ""
  });
  
  const [formErrors, setFormErrors] = React.useState<Record<string, string>>({});

  React.useEffect(() => {
    if (isAuthenticated) {
      router.push("/");
    }
  }, [isAuthenticated, router]);

  const handleFormChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Effacer l'erreur sur ce champ si l'utilisateur modifie sa valeur
    if (formErrors[field]) {
      setFormErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const validateForm = () => {
    const errors: Record<string, string> = {};
    
    if (!formData.firstName.trim()) {
      errors.firstName = "Le prénom est requis";
    }
    
    if (!formData.lastName.trim()) {
      errors.lastName = "Le nom est requis";
    }
    
    if (!formData.username.trim()) {
      errors.username = "Le nom d'utilisateur est requis";
    }
    
    if (!formData.email.trim()) {
      errors.email = "L'email est requis";
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      errors.email = "Format d'email invalide";
    }
    
    if (!formData.nativeLanguage) {
      errors.nativeLanguage = "La langue maternelle est requise";
    }
    
    if (!formData.targetLanguage) {
      errors.targetLanguage = "La langue cible est requise";
    } else if (formData.nativeLanguage === formData.targetLanguage) {
      errors.targetLanguage = "La langue cible doit être différente de la langue maternelle";
    }
    
    if (!formData.languageLevel) {
      errors.languageLevel = "Le niveau de langue est requis";
    }
    
    if (!formData.objectives) {
      errors.objectives = "L'objectif d'apprentissage est requis";
    }
    
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    // On stocke les données du formulaire dans localStorage pour les récupérer après l'authentification
    localStorage.setItem("userRegistrationData", JSON.stringify(formData));
    
    // On passe à l'onglet d'authentification
    setActiveTab("auth");
  };

  const handleAuth0Signup = async () => {
    try {
      setError(null);
      setIsLoading(true);
      // Appel à la fonction login avec un paramètre string
      await login("auth0");  // ou autre valeur acceptée par ta fonction login
    } catch (err) {
      setError("Une erreur est survenue lors de l'inscription. Veuillez réessayer.");
      console.error("Erreur d'inscription:", err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex justify-center items-center p-4 md:p-8">
      <Card className="w-full max-w-lg shadow-lg">
        <CardHeader>
          <CardTitle className="text-2xl text-center">Créer un compte</CardTitle>
          <CardDescription className="text-center">
            Rejoignez Linguify et commencez votre voyage d'apprentissage linguistique
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-2 mb-6">
              <TabsTrigger value="form">Vos informations</TabsTrigger>
              <TabsTrigger value="auth">Finaliser l'inscription</TabsTrigger>
            </TabsList>
            
            <TabsContent value="form">
              <form onSubmit={handleFormSubmit} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="firstName">Prénom</Label>
                    <Input 
                      id="firstName" 
                      placeholder="Prénom"
                      value={formData.firstName}
                      onChange={(e) => handleFormChange("firstName", e.target.value)}
                      className={formErrors.firstName ? "border-red-500" : ""}
                    />
                    {formErrors.firstName && <p className="text-sm text-red-500">{formErrors.firstName}</p>}
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="lastName">Nom</Label>
                    <Input 
                      id="lastName" 
                      placeholder="Nom"
                      value={formData.lastName}
                      onChange={(e) => handleFormChange("lastName", e.target.value)}
                      className={formErrors.lastName ? "border-red-500" : ""}
                    />
                    {formErrors.lastName && <p className="text-sm text-red-500">{formErrors.lastName}</p>}
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="username">Nom d'utilisateur</Label>
                  <Input 
                    id="username" 
                    placeholder="Nom d'utilisateur"
                    value={formData.username}
                    onChange={(e) => handleFormChange("username", e.target.value)}
                    className={formErrors.username ? "border-red-500" : ""}
                  />
                  {formErrors.username && <p className="text-sm text-red-500">{formErrors.username}</p>}
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="email">Adresse email</Label>
                  <Input 
                    id="email" 
                    type="email" 
                    placeholder="vous@exemple.com"
                    value={formData.email}
                    onChange={(e) => handleFormChange("email", e.target.value)}
                    className={formErrors.email ? "border-red-500" : ""}
                  />
                  {formErrors.email && <p className="text-sm text-red-500">{formErrors.email}</p>}
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="nativeLanguage">Langue maternelle</Label>
                    <Select 
                      value={formData.nativeLanguage} 
                      onValueChange={(value) => handleFormChange("nativeLanguage", value)}
                    >
                      <SelectTrigger className={formErrors.nativeLanguage ? "border-red-500" : ""}>
                        <SelectValue placeholder="Sélectionnez" />
                      </SelectTrigger>
                      <SelectContent>
                        {LANGUAGE_OPTIONS.map((lang) => (
                          <SelectItem key={lang.value} value={lang.value}>{lang.label}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    {formErrors.nativeLanguage && <p className="text-sm text-red-500">{formErrors.nativeLanguage}</p>}
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="targetLanguage">Langue à apprendre</Label>
                    <Select 
                      value={formData.targetLanguage} 
                      onValueChange={(value) => handleFormChange("targetLanguage", value)}
                    >
                      <SelectTrigger className={formErrors.targetLanguage ? "border-red-500" : ""}>
                        <SelectValue placeholder="Sélectionnez" />
                      </SelectTrigger>
                      <SelectContent>
                        {LANGUAGE_OPTIONS.map((lang) => (
                          <SelectItem key={lang.value} value={lang.value}>{lang.label}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    {formErrors.targetLanguage && <p className="text-sm text-red-500">{formErrors.targetLanguage}</p>}
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="languageLevel">Niveau actuel</Label>
                    <Select 
                      value={formData.languageLevel} 
                      onValueChange={(value) => handleFormChange("languageLevel", value)}
                    >
                      <SelectTrigger className={formErrors.languageLevel ? "border-red-500" : ""}>
                        <SelectValue placeholder="Sélectionnez" />
                      </SelectTrigger>
                      <SelectContent>
                        {LEVEL_OPTIONS.map((level) => (
                          <SelectItem key={level.value} value={level.value}>{level.label}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    {formErrors.languageLevel && <p className="text-sm text-red-500">{formErrors.languageLevel}</p>}
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="objectives">Objectif</Label>
                    <Select 
                      value={formData.objectives} 
                      onValueChange={(value) => handleFormChange("objectives", value)}
                    >
                      <SelectTrigger className={formErrors.objectives ? "border-red-500" : ""}>
                        <SelectValue placeholder="Sélectionnez" />
                      </SelectTrigger>
                      <SelectContent>
                        {OBJECTIVES_OPTIONS.map((objective) => (
                          <SelectItem key={objective.value} value={objective.value}>{objective.label}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    {formErrors.objectives && <p className="text-sm text-red-500">{formErrors.objectives}</p>}
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="bio">Bio (optionnel)</Label>
                  <Input 
                    id="bio" 
                    placeholder="Parlez-nous un peu de vous..."
                    value={formData.bio}
                    onChange={(e) => handleFormChange("bio", e.target.value)}
                  />
                </div>
                
                <Button type="submit" className="w-full">Continuer</Button>
              </form>
            </TabsContent>
            
            <TabsContent value="auth">
              <div className="space-y-4">
                <p className="text-center mb-4">
                  Vos informations ont été enregistrées temporairement. Finalisez votre inscription en vous connectant avec Auth0.
                </p>
                
                {error && (
                  <div className="p-3 bg-red-100 text-red-700 rounded-md text-sm mb-4">
                    {error}
                  </div>
                )}
                
                <Button 
                  className="w-full flex items-center justify-center gap-2"
                  onClick={handleAuth0Signup}
                  disabled={isLoading}
                >
                  {isLoading ? <LoaderCircle className="h-4 w-4 animate-spin" /> : null}
                  Finaliser l'inscription avec Auth0
                </Button>
                
                <div className="text-center mt-4">
                  <Button 
                    variant="link" 
                    className="text-sm"
                    onClick={() => setActiveTab("form")}
                  >
                    Retour aux informations
                  </Button>
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
        <CardFooter className="flex flex-col space-y-2">
          <div className="text-center text-sm">
            En créant un compte, vous acceptez nos{" "}
            <a href="/terms" className="underline hover:text-primary">
              Conditions d'utilisation
            </a>{" "}
            et notre{" "}
            <a href="/privacy" className="underline hover:text-primary">
              Politique de confidentialité
            </a>
          </div>
          <div className="text-center text-sm">
            Vous avez déjà un compte?{" "}
            <a href="/login" className="text-primary hover:underline">
              Connectez-vous
            </a>
          </div>
        </CardFooter>
      </Card>
    </div>
  );
}