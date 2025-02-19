// src/app/(dashboard)/_components/header.tsx
"use client";

import React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/providers/AuthProvider";
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
  GlobeIcon,
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

const Header: React.FC = () => {
  const { isAuthenticated, user, logout } = useAuth();
  const router = useRouter();
  const { toast } = useToast();
  const { theme, setTheme } = useTheme();

  const handleLanguageChange = (value: string) => {
    toast({
      title: "Language Changed",
      description: `Language set to ${value.toUpperCase()}`,
    });
  };

  const handleLogout = async () => {
    try {
      await logout();
      router.push("/");
      toast({
        title: "Logged out successfully",
        description: "Come back soon!",
      });
    } catch (error) {
      console.error("Logout error:", error);
      toast({
        variant: "destructive",
        title: "Error logging out",
        description: "Please try again",
      });
    }
  };

  const handleNotificationClick = () => {
    toast({
      title: "No new notifications",
      description: "Check back later for updates",
    });
  };

  return (
    <header className="sticky top-0 z-50 w-full h-14 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 dark:bg-gray-900/95">
      <div className="flex h-14 items-center justify-between px-6">
        {/* Logo Section */}
        <div className="flex items-center gap-2">
          <Link
            href="/"
            className="flex items-center gap-2 hover:opacity-90 transition-all"
          >
            <GlobeIcon className="h-6 w-6 text-brand-purple" />
            <span className="text-xl font-bold bg-gradient-to-r from-brand-purple to-brand-gold bg-clip-text text-transparent">
              Linguify
            </span>
          </Link>

          {/* Navigation */}
          <nav className="hidden md:flex gap-6 ml-10">
            <NavItem href="/learning" icon={BookOpen} label="Learn" />
            <NavItem href="/progress" icon={Trophy} label="Progress" />
          </nav>
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
          <Select onValueChange={handleLanguageChange} defaultValue="en">
            <SelectTrigger className="w-32">
              <SelectValue placeholder="Language" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="en">English</SelectItem>
              <SelectItem value="fr">French</SelectItem>
              <SelectItem value="es">Spanish</SelectItem>
              <SelectItem value="nl">Dutch</SelectItem>
            </SelectContent>
          </Select>

          {isAuthenticated ? (
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
                        alt="Profile" 
                        className="h-6 w-6 rounded-full object-cover"
                      />
                    ) : (
                      <User className="h-4 w-4" />
                    )}
                    <span className="max-w-[100px] truncate">{user?.name || 'Profile'}</span>
                    <ChevronDown className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-48">
                  <DropdownMenuLabel>
                    <div className="flex items-center gap-2">
                      {user?.picture && (
                        <img 
                          src={user.picture} 
                          alt="Profile" 
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
                  <DropdownMenuItem onClick={() => router.push('/profile')}>
                    <User className="h-4 w-4 mr-2" />
                    Profile
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => router.push('/learning')}>
                    <BookOpen className="h-4 w-4 mr-2" />
                    My Learning
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => router.push('/settings')}>
                    <Settings className="h-4 w-4 mr-2" />
                    Settings
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={handleLogout} className="text-red-600">
                    <LogOut className="h-4 w-4 mr-2" />
                    Logout
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Button 
                variant="ghost"
                onClick={() => router.push('/login')}
              >
                Sign In
              </Button>
              <Button
                className="bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-600 hover:to-blue-700 text-white"
                onClick={() => router.push('/register')}
              >
                Get Started 
              </Button>
            </div>
          )}

          {/* Mobile Menu Button */}
          <Button variant="ghost" size="icon" className="md:hidden">
            <Menu className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </header>
  );
};

const NavItem = ({
  href,
  icon: Icon,
  label,
}: {
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  label: string;
}) => (
  <Link
    href={href}
    className="flex items-center gap-2 text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-sky-600 dark:hover:text-sky-400 transition-colors"
  >
    <Icon className="h-4 w-4" />
    {label}
  </Link>
);

export default Header;