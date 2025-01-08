"use client";

import AppInterface from "@/app_manager/AppInterface";

export default function AppsPage() {
  return <AppInterface />;
}












// "use client";

// import { useEffect, useState } from "react";
// import { useUser } from "@clerk/nextjs";
// import { useRouter } from "next/navigation";
// import AppInterface from "@/app_manager/AppInterface";

// export default function HomePage() {
//   const { user, isLoaded } = useUser();
//   const router = useRouter();
//   const [hasSelectedModules, setHasSelectedModules] = useState(false);

//   useEffect(() => {
//     if (isLoaded && !user) {
//       router.push('/sign-in');
//       return;
//     }

//     // Vérifier si l'utilisateur a déjà choisi ses modules
//     // On peut stocker cette info dans localStorage pour cet exemple
//     const hasModules = localStorage.getItem('hasSelectedModules');
//     if (hasModules === 'true') {
//       setHasSelectedModules(true);
//     }
//   }, [user, isLoaded, router]);

//   const onModulesSelected = () => {
//     localStorage.setItem('hasSelectedModules', 'true');
//     setHasSelectedModules(true);
//     // Ici vous pouvez rediriger vers le dashboard ou la page principale
//     router.push('/dashboard');
//   };

//   if (!isLoaded || !user) {
//     return <div>Loading...</div>;
//   }

// //   // Si l'utilisateur n'a pas encore choisi ses modules, afficher l'interface de sélection
// //   if (!hasSelectedModules) {
// //     return <AppInterface onModulesSelected={onModulesSelected} />;
// //   }

//   // Si l'utilisateur a déjà choisi ses modules, rediriger vers le dashboard
//   router.push('/dashboard');
//   return null;
// }