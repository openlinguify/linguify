"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, useEffect } from "react";
import { Menu, X, Globe } from "lucide-react";
import {
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  navigationMenuTriggerStyle,
} from "@/components/ui/navigation-menu";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

// Define navigation items as a const outside the component for better performance
const NAVIGATION_ITEMS = [
  { name: "Home", href: "/home" },
  { name: "Features", href: "/features" },
  { name: "Pricing", href: "/pricing" },
  { name: "Company", href: "/company" },
  { name: "Contact", href: "/contact" },
] as const;

// Langues disponibles
const LANGUAGES = [
  { code: 'fr', name: 'Français', flag: '🇫🇷' },
  { code: 'en', name: 'English', flag: '🇬🇧' },
  { code: 'es', name: 'Español', flag: '🇪🇸' },
  { code: 'nl', name: 'Nederlands', flag: '🇳🇱' },
];

export const Navbar = () => {
  const pathname = usePathname();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [currentLanguage, setCurrentLanguage] = useState('fr');
  
  // Charger la langue depuis localStorage au démarrage
  useEffect(() => {
    const savedLanguage = localStorage.getItem('language');
    if (savedLanguage) {
      setCurrentLanguage(savedLanguage);
    }
  }, []);
  
  // Fonction pour changer la langue
  const setLanguage = (lang: string) => {
    setCurrentLanguage(lang);
    localStorage.setItem('language', lang);
    // Déclencher un événement pour que d'autres composants puissent réagir
    window.dispatchEvent(new Event('languageChanged'));
  };
  
  // Close mobile menu when screen size changes to desktop
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 640) {
        setIsMenuOpen(false);
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Prevent body scroll when mobile menu is open
  useEffect(() => {
    if (isMenuOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
  }, [isMenuOpen]);

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  // Get current language name and flag
  const currentLangObj = LANGUAGES.find(lang => lang.code === currentLanguage) || LANGUAGES[0];

  return (
    <header className="sticky top-0 z-50 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          {/* Logo */}
          <div className="flex items-center">
            <Link 
              href="/home" 
              className="font-bold text-xl text-gray-900 dark:text-white hover:opacity-80 transition-opacity"
              aria-label="Linguify Home"
            >
              Linguify
            </Link>
            
            {/* Desktop Navigation */}
            <div className="hidden sm:ml-6 sm:flex sm:space-x-2">
              <NavigationMenu>
                <NavigationMenuList>
                  {NAVIGATION_ITEMS.map((item) => (
                    <NavigationMenuItem key={item.href}>
                      <Link href={item.href} legacyBehavior passHref>
                        <NavigationMenuLink
                          className={cn(
                            navigationMenuTriggerStyle(),
                            pathname === item.href 
                              ? "bg-indigo-50 text-indigo-700 dark:bg-indigo-900 dark:text-indigo-200" 
                              : "text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700"
                          )}
                        >
                          {item.name}
                        </NavigationMenuLink>
                      </Link>
                    </NavigationMenuItem>
                  ))}
                </NavigationMenuList>
              </NavigationMenu>
            </div>
          </div>
          
          {/* Desktop Auth Buttons and Language Switcher */}
          <div className="hidden sm:flex sm:items-center">
            {/* Language Switcher - Desktop */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm" className="mr-4">
                  <Globe className="h-4 w-4 mr-2" />
                  <span>{currentLangObj.flag} {currentLangObj.name}</span>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                {LANGUAGES.map((lang) => (
                  <DropdownMenuItem
                    key={lang.code}
                    onClick={() => setLanguage(lang.code)}
                    className={cn(
                      "cursor-pointer",
                      currentLanguage === lang.code ? "bg-indigo-50 dark:bg-indigo-900" : ""
                    )}
                  >
                    <span className="mr-2">{lang.flag}</span>
                    {lang.name}
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>
            
            <Link href="/login" className="mr-4">
              <Button variant="outline">Login</Button>
            </Link>
            <Link href="/register">
              <Button>Register</Button>
            </Link>
          </div>
          
          {/* Mobile Menu Toggle */}
          <div className="flex items-center sm:hidden">
            <Button 
              variant="ghost" 
              size="icon" 
              onClick={toggleMenu}
              aria-label={isMenuOpen ? "Close menu" : "Open menu"}
            >
              {isMenuOpen ? (
                <X className="h-6 w-6" aria-hidden="true" />
              ) : (
                <Menu className="h-6 w-6" aria-hidden="true" />
              )}
            </Button>
          </div>
        </div>
      </nav>

      {/* Mobile menu */}
      {isMenuOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black/50 sm:hidden" 
          onClick={() => setIsMenuOpen(false)}
          aria-hidden="true"
        >
          <div 
            className="absolute top-0 right-0 w-64 h-full bg-white dark:bg-gray-900 shadow-lg"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-4 border-b">
              <Link 
                href="/home" 
                className="font-bold text-xl text-gray-900 dark:text-white"
                onClick={() => setIsMenuOpen(false)}
              >
                Linguify
              </Link>
            </div>
            <nav className="p-4">
              <div className="space-y-2">
                {NAVIGATION_ITEMS.map((item) => (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={cn(
                      "block px-3 py-2 rounded-md text-base font-medium transition-colors",
                      pathname === item.href
                        ? "bg-indigo-50 text-indigo-700 dark:bg-indigo-900 dark:text-indigo-200"
                        : "text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700"
                    )}
                    onClick={() => setIsMenuOpen(false)}
                  >
                    {item.name}
                  </Link>
                ))}
              </div>
              
              {/* Language Switcher - Mobile */}
              <div className="mt-6 border-t pt-4">
                <div className="px-3 py-2 text-sm font-medium text-gray-500 dark:text-gray-400">
                  Language
                </div>
                <div className="mt-2 grid grid-cols-2 gap-2">
                  {LANGUAGES.map((lang) => (
                    <Button
                      key={lang.code}
                      variant={currentLanguage === lang.code ? "default" : "outline"}
                      size="sm"
                      className="justify-start"
                      onClick={() => {
                        setLanguage(lang.code);
                        setIsMenuOpen(false);
                      }}
                    >
                      <span className="mr-2">{lang.flag}</span>
                      {lang.name}
                    </Button>
                  ))}
                </div>
              </div>
              
              <div className="mt-6 space-y-2">
                <Link
                  href="/login"
                  className="block w-full"
                  onClick={() => setIsMenuOpen(false)}
                >
                  <Button variant="outline" className="w-full">Login</Button>
                </Link>
                <Link
                  href="/register"
                  className="block w-full"
                  onClick={() => setIsMenuOpen(false)}
                >
                  <Button className="w-full">Register</Button>
                </Link>
              </div>
            </nav>
          </div>
        </div>
      )}
    </header>
  );
};