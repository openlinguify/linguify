// src/app/(dashboard)/_components/header.tsx
'use client';

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  User,
  BookOpen,
  Trophy,
  Settings,
  Bell,
  NotebookPen,
  LogOut,
  Brain,
  BarChart,
  HandHelping,

  Menu,
  ChevronDown,
  ArrowLeft,
} from "lucide-react";
import {
  Select,
  SelectTrigger,
  SelectContent,
  SelectItem,
  SelectValue,
} from "@/components/ui/select";
import { useToast } from "@/components/ui/use-toast";
import { useTheme } from "next-themes";
import { Sun, Moon } from "lucide-react";
import { useAuthContext } from "@/core/auth/AuthProvider";
import { useTranslation } from "@/core/i18n/useTranslations";

// Define types for page configuration
interface PageConfig {
  title: string;
  icon: React.ElementType | null;
}

interface PagesConfig {
  [path: string]: PageConfig;
}

const Header = () => {
  const router = useRouter();
  const pathname = usePathname();
  const { toast } = useToast();
  const { theme, setTheme } = useTheme();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  // Initialize with false to ensure title is visible on first render
  const [isHoveringLogo, setIsHoveringLogo] = useState(false);
  // Track if we're on client-side immediately
  const [isClient, setIsClient] = useState(false);
    // Use Translation Hook
  const { t, locale, changeLanguage } = useTranslation();
  const PAGE_CONFIG: PagesConfig = {
    '/': { title: 'Linguify', icon: null },
    '/home': { title: 'Linguify', icon: null },
    '/learning': { title: t('dashboard.layoutpathname.learning'), icon: BookOpen },
    '/flashcard': { title: t('dashboard.layoutpathname.flashcard'), icon: Brain },
    '/progress': { title: t('dashboard.layoutpathname.progress'), icon: BarChart },
    '/notebook': { title: t('dashboard.layoutpathname.notebook'), icon: NotebookPen },
    '/help': { title: t('dashboard.helpCard.title'), icon: HandHelping },
    '/settings': { title: t('dashboard.layoutpathname.settings'), icon: Settings },
  };
  // Get current page config with fallback
  const currentPage = PAGE_CONFIG[pathname] || { title: 'Linguify', icon: null };
  const isHomePage = pathname === '/' || pathname === '/home';
  


  // Use Auth Context
  const { user, isAuthenticated, login } = useAuthContext();

  // Define page configuration outside component to ensure it's immediately available

  // Set client-side state as early as possible
  useEffect(() => {
    setIsClient(true);
  }, []);

  const handleLanguageChange = (value: string) => {
    changeLanguage(value as any);
    toast({
      title: t('dashboard.header.languageChanged'),
      description: t('dashboard.header.languageSetTo', { language: value.toUpperCase() }),
    });
  };

  const handleLogout = () => {
    // Local logout
    localStorage.clear();

    // Clear cookies
    document.cookie.split(";").forEach(function (c) {
      document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/");
    });

    // Redirect to home
    window.location.href = '/home';

    toast({
      title: t('auth.logoutSuccess'),
      description: t('auth.comeBackSoon'),
    });
  };

  const handleLogin = () => {
    login();
  };

  const handleNotificationClick = () => {
    toast({
      title: t('dashboard.header.noNewNotifications'),
      description: t('dashboard.header.checkBackLater'),
    });
  };
  
  const handleBackToHome = () => {
    router.push('/');
  };

  // Manage mobile menu
  useEffect(() => {
    const handleClickOutside = () => {
      if (isMenuOpen) setIsMenuOpen(false);
    };

    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, [isMenuOpen]);
  
  // Set default title and icon based on the current route
  const pageTitle = currentPage.title;
  
  // Render a skeleton header with the correct title even before hydration
  if (!isClient) {
    return (
      <header className="sticky top-0 z-50 w-full h-14 bg-background">
        <div className="flex h-14 items-center px-6">
          <div className="flex items-center">
            <span className="text-xl font-bold bg-gradient-to-r from-indigo-600 via-purple-500 to-pink-400 bg-clip-text text-transparent font-montserrat">
              {pageTitle}
            </span>
          </div>
        </div>
      </header>
    );
  }

  return (
    <header className="sticky top-0 z-50 w-full h-14 dark:border-gray-800/20 bg-background/70 dark:bg-transparent backdrop-blur-xl">
      <div className="flex h-14 items-center justify-between px-6">
        {/* Logo Section - Always visible */}
        <div className="flex items-center gap-2 h-full">
          {isHomePage ? (
            // Home page logo - simple and static
            <div className="flex items-center">
              <span className="text-xl font-bold bg-gradient-to-r from-indigo-600 via-purple-500 to-pink-400 bg-clip-text text-transparent font-montserrat">
                {pageTitle}
              </span>
            </div>
          ) : (
            // Inner page layout with back button functionality
            <div
              className="flex items-center group cursor-pointer h-full"
              onMouseEnter={() => setIsHoveringLogo(true)}
              onMouseLeave={() => setIsHoveringLogo(false)}
              onClick={handleBackToHome}
            >
              {/* The page title is always visible first */}
              <div className="flex items-center relative h-full">
                {/* Back button that appears on hover */}
                <div 
                  className={`absolute left-0 top-1/2 -translate-y-1/2 transition-opacity duration-300 ${
                    isHoveringLogo ? 'opacity-100' : 'opacity-0'
                  }`}
                >
                  <ArrowLeft className="h-5 w-5 text-gray-600 dark:text-gray-300" />
                </div>
                
                {/* Page title/icon that shifts right on hover */}
                <div 
                  className={`flex items-center transition-all duration-300 ${
                    isHoveringLogo ? 'translate-x-7' : 'translate-x-0'
                  }`}
                >
                  {currentPage.icon && (
                    <currentPage.icon className="h-4 w-4 mr-2" />
                  )}
                  <span className="text-xl font-bold bg-gradient-to-r from-indigo-600 via-purple-500 to-pink-400 bg-clip-text text-transparent font-montserrat">
                    {pageTitle}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Right Side Actions */}
        <div className="flex items-center gap-4">
          {/* Theme Toggle */}
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
            className="text-gray-600 dark:text-gray-300 hover:text-sky-600 dark:hover:text-sky-400"
          >
            {theme === 'light' ? (
              <Moon className="h-5 w-5" />
            ) : (
              <Sun className="h-5 w-5" />
            )}
          </Button>

          {/* Language Selector */}
          <Select onValueChange={handleLanguageChange} defaultValue={locale}>
            <SelectTrigger 
            className="w-32 dark:bg-transparent dark:border-none dark:text-gray-200">
              <SelectValue placeholder={t('dashboard.header.language')} />
            </SelectTrigger>
            <SelectContent
              className="w-32 bg-background dark:bg-gray-900/70 backdrop-blur-xl shadow-lg border dark:border-gray-700/20"
            >
              <SelectItem value="en">{t('dashboard.header.english')}</SelectItem>
              <SelectItem value="fr">{t('dashboard.header.french')}</SelectItem>
              <SelectItem value="es">{t('dashboard.header.spanish')}</SelectItem>
              <SelectItem value="nl">{t('dashboard.header.dutch')}</SelectItem>
            </SelectContent>
          </Select>

          {/* Auth-dependent UI */}
          {isAuthenticated && user ? (
            <div className="flex items-center gap-4">
              {/* Notifications */}
              <Button
                variant="ghost"
                size="icon"
                onClick={handleNotificationClick}
                className="relative"
              >
                <Bell className="h-5 w-5" />
                <span className="absolute top-0 right-0 h-2 w-2 bg-red-500 rounded-full" />
              </Button>

              {/* User Menu */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="flex items-center gap-2">
                    {user?.picture ? (
                      <img
                        src={user.picture}
                        alt={t('dashboard.header.profile')}
                        className="h-6 w-6 rounded-full object-cover"
                      />
                    ) : (
                      <User className="h-4 w-4" />
                    )}
                    <span className="max-w-[100px] truncate">{user?.name || t('dashboard.header.profile')}</span>
                    <ChevronDown className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-48">
                  <DropdownMenuLabel>
                    <div className="flex items-center gap-2">
                      {user?.picture && (
                        <img
                          src={user.picture}
                          alt={t('dashboard.header.profile')}
                          className="h-8 w-8 rounded-full object-cover"
                        />
                      )}
                      <div>
                        <p className="font-medium text-sm">{user?.name}</p>
                        <p className="text-xs text-muted-foreground">{user?.email}</p>
                      </div>
                    </div>
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={() => router.push('/learning')}>
                    <BookOpen className="h-4 w-4 mr-2" />
                    {t('sidebar.learning')}
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => router.push('/settings')}>
                    <Settings className="h-4 w-4 mr-2" />
                    {t('sidebar.settings')}
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={handleLogout} className="text-red-600">
                    <LogOut className="h-4 w-4 mr-2" />
                    {t('auth.logout')}
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                onClick={handleLogin}
              >
                {t('auth.login')}
              </Button>
              <Button
                className="bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-600 hover:to-blue-700 text-white"
                onClick={() => router.push('/register')}
              >
                {t('auth.register')}
              </Button>
            </div>
          )}

          {/* Mobile Menu Button */}
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden"
            onClick={(e) => {
              e.stopPropagation();
              setIsMenuOpen(!isMenuOpen);
            }}
          >
            <Menu className="h-5 w-5" />
          </Button>
        </div>
      </div>

      {/* Mobile menu */}
      {isMenuOpen && (
        <div className="md:hidden border-t dark:border-gray-700/20 absolute w-full bg-background/80 dark:bg-gray-900/70 backdrop-blur-xl shadow-lg">
          <div className="p-4 space-y-3">
            <NavItemMobile href="/learning" icon={BookOpen} label={t('sidebar.learning')} onClick={() => setIsMenuOpen(false)} />
            <NavItemMobile href="/progress" icon={Trophy} label={t('sidebar.progress')} onClick={() => setIsMenuOpen(false)} />

            {isAuthenticated ? (
              <>
                <NavItemMobile href="/profile" icon={User} label={t('dashboard.header.profile')} onClick={() => setIsMenuOpen(false)} />
                <NavItemMobile href="/settings" icon={Settings} label={t('sidebar.settings')} onClick={() => setIsMenuOpen(false)} />
                <div className="pt-2">
                  <Button
                    variant="destructive"
                    className="w-full justify-start"
                    onClick={() => {
                      localStorage.clear();
                      document.cookie.split(";").forEach(function (c) {
                        document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/");
                      });
                      window.location.href = '/home';
                      setIsMenuOpen(false);
                    }}
                  >
                    <LogOut className="h-4 w-4 mr-2" />
                    {t('auth.logout')}
                  </Button>
                </div>
              </>
            ) : (
              <div className="flex flex-col gap-2 pt-2">
                <Button
                  onClick={() => {
                    handleLogin();
                    setIsMenuOpen(false);
                  }}
                >
                  {t('auth.login')}
                </Button>
                <Button
                  className="bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-600 hover:to-blue-700 text-white"
                  onClick={() => {
                    router.push('/register');
                    setIsMenuOpen(false);
                  }}
                >
                  {t('auth.register')}
                </Button>
              </div>
            )}
          </div>
        </div>
      )}
    </header>
  );
};

const NavItemMobile = ({
  href,
  icon: Icon,
  label,
  onClick,
}: {
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  onClick?: () => void;
}) => (
  <Link
    href={href}
    className="flex items-center p-2 rounded-md text-sm font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
    onClick={onClick}
  >
    <Icon className="h-4 w-4 mr-3" />
    {label}
  </Link>
);

export default Header;