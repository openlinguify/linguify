"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export const Navbar = () => {
  const pathname = usePathname();
  
  const navigation = [
    { name: "Home", href: "/home" },
    { name: "Features", href: "/features" },
    { name: "Pricing", href: "/pricing" },
    { name: "Company", href: "/company" },
    { name: "Blog", href: "/blog" },
  ];

  return (
    <nav className="bg-white border-b border-gray-200">
      <div className="container px-6 py-4 mx-auto md:flex md:justify-between md:items-center">
        <div className="flex items-center justify-between">
          <Link href="/home" className="text-xl font-bold text-gray-800">
            Linguify
          </Link>

          <div className="md:hidden">
            <button type="button" className="block text-gray-800 hover:text-gray-700 focus:text-gray-700 focus:outline-none">
              <svg className="h-6 w-6 fill-current" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>

        <div className="hidden md:flex md:items-center md:justify-between w-full">
          <div className="flex flex-col md:flex-row md:items-center md:space-x-6">
            {navigation.map((item) => (
              <Link 
                key={item.name} 
                href={item.href} 
                className={`text-gray-800 hover:text-blue-600 ${
                  pathname === item.href ? "font-medium text-blue-600" : ""
                }`}
              >
                {item.name}
              </Link>
            ))}
          </div>
          
          {/* Boutons d'authentification */}
          <div className="flex items-center mt-4 md:mt-0">
            <Link 
              href="/login" 
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
            >
              Se connecter
            </Link>
            <Link 
              href="/register" 
              className="ml-4 px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors"
            >
              S'inscrire
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}