'use client';

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
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
  LogOut,
  Menu,
  ChevronDown,
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

const Header = () => {
  const router = useRouter();
  const { toast } = useToast();
  const { theme, setTheme } = useTheme();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isClient, setIsClient] = useState(false);
  
  // Use Translation Hook
  const { t, locale, changeLanguage } = useTranslation();

  // Use Auth Context
  const { user, isAuthenticated, login } = useAuthContext();

  // Only run client-side code after mounting
  useEffect(() => {
    setIsClient(true);
  }, []);

  const handleLanguageChange = (value: string) => {
    console.log("Language changed to:", value);
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

  // Manage mobile menu
  useEffect(() => {
    const handleClickOutside = () => {
      if (isMenuOpen) setIsMenuOpen(false);
    };

    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, [isMenuOpen]);

  // Don't render anything until client-side
  if (!isClient) {
    return <header className="sticky top-0 z-50 w-full h-14 border-b bg-background"></header>;
  }

  return (
    <header className="sticky top-0 z-50 w-full h-14 border-b bg-background dark:bg-gray-900">
      <div className="flex h-14 items-center justify-between px-6">
        {/* Logo Section */}
        <div className="flex items-center gap-2">
          <Link
            href="/"
            className="flex items-center gap-2 hover:opacity-90 transition-all"
          >
            <span className="text-xl font-bold bg-gradient-to-r from-indigo-600 via-purple-500 to-pink-400 bg-clip-text text-transparent">
              Linguify
            </span>
          </Link>      
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
            <SelectTrigger className="w-32">
              <SelectValue placeholder={t('dashboard.header.language')} />
            </SelectTrigger>
            <SelectContent>
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
        <div className="md:hidden border-t dark:border-gray-700">
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