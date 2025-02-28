import React from "react";
import Link from "next/link";
import { Container } from "./Container";
import { Logo } from "./Logo";

interface NavItem {
  name: string;
  href: string;
}

interface SocialItem {
  name: string;
  href: string;
  icon: React.FC<{ size?: number }>;
}

// Social Icons Components
const TwitterIcon: React.FC<{ size?: number }> = ({ size = 24 }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="currentColor"
  >
    <path d="M24 4.37a9.6 9.6 0 0 1-2.83.8 5.04 5.04 0 0 0 2.17-2.8c-.95.58-2 1-3.13 1.22A4.86 4.86 0 0 0 16.61 2a4.99 4.99 0 0 0-4.79 6.2A13.87 13.87 0 0 1 1.67 2.92 5.12 5.12 0 0 0 3.2 9.67a4.82 4.82 0 0 1-2.23-.64v.07c0 2.44 1.7 4.48 3.95 4.95a4.84 4.84 0 0 1-2.22.08c.63 2.01 2.45 3.47 4.6 3.51A9.72 9.72 0 0 1 0 19.74 13.68 13.68 0 0 0 7.55 22c9.06 0 14-7.7 14-14.37v-.65c.96-.71 1.79-1.6 2.45-2.61z" />
  </svg>
);

const InstagramIcon: React.FC<{ size?: number }> = ({ size = 24 }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="currentColor"
  >
    <path d="M16.98 0a6.9 6.9 0 0 1 5.08 1.98A6.94 6.94 0 0 1 24 7.02v9.96c0 2.08-.68 3.87-1.98 5.13A7.14 7.14 0 0 1 16.94 24H7.06a7.06 7.06 0 0 1-5.03-1.89A6.96 6.96 0 0 1 0 16.94V7.02C0 2.8 2.8 0 7.02 0h9.96zm.05 2.23H7.06c-1.45 0-2.7.43-3.53 1.25a4.82 4.82 0 0 0-1.3 3.54v9.92c0 1.5.43 2.7 1.3 3.58a5 5 0 0 0 3.53 1.25h9.88a5 5 0 0 0 3.53-1.25 4.73 4.73 0 0 0 1.4-3.54V7.02a5 5 0 0 0-1.3-3.49 4.82 4.82 0 0 0-3.54-1.3zM12 5.76c3.39 0 6.2 2.8 6.2 6.2a6.2 6.2 0 0 1-12.4 0 6.2 6.2 0 0 1 6.2-6.2zm0 2.22a3.99 3.99 0 0 0-3.97 3.97A3.99 3.99 0 0 0 12 15.92a3.99 3.99 0 0 0 3.97-3.97A3.99 3.99 0 0 0 12 7.98zm6.44-3.77a1.4 1.4 0 1 1 0 2.8 1.4 1.4 0 0 1 0-2.8z" />
  </svg>
);

const LinkedInIcon: React.FC<{ size?: number }> = ({ size = 24 }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="currentColor"
  >
    <path d="M22.23 0H1.77C.8 0 0 .77 0 1.72v20.56C0 23.23.8 24 1.77 24h20.46c.98 0 1.77-.77 1.77-1.72V1.72C24 .77 23.2 0 22.23 0zM7.27 20.1H3.65V9.24h3.62V20.1zM5.47 7.76h-.03c-1.22 0-2-.83-2-1.87 0-1.06.8-1.87 2.05-1.87 1.24 0 2 .8 2.02 1.87 0 1.04-.78 1.87-2.05 1.87zM20.34 20.1h-3.63v-5.8c0-1.45-.52-2.45-1.83-2.45-1 0-1.6.67-1.87 1.32-.1.23-.11.55-.11.88v6.05H9.28s.05-9.82 0-10.84h3.63v1.54a3.6 3.6 0 0 1 3.26-1.8c2.39 0 4.18 1.56 4.18 4.89v6.21z" />
  </svg>
);

// LinkSection composant déplacé après définition des icônes
const LinkSection: React.FC<{ title: string; items: NavItem[] }> = ({ title, items }) => (
  <div className="space-y-4">
    <h3 className="text-sm font-semibold text-gray-900 dark:text-white uppercase tracking-wider">
      {title}
    </h3>
    <nav className="flex flex-col space-y-3">
      {items.map((item) => (
        <Link
          key={item.name}
          href={item.href}
          className="text-base text-gray-600 dark:text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
        >
          {item.name}
        </Link>
      ))}
    </nav>
  </div>
);

export const Footer: React.FC = () => {
  const navigation: NavItem[] = [
    { name: "Accueil", href: "/" },
    { name: "Fonctionnalités", href: "/features" },
    { name: "Tarifs", href: "/pricing" },
    { name: "À propos", href: "/company" },
    { name: "Contact", href: "/contact" }
  ];
  
  const legal: NavItem[] = [
    { name: "Conditions", href: "/terms" },
    { name: "Confidentialité", href: "/privacy" },
    { name: "Mentions légales", href: "/legal" }
  ];

  const social: SocialItem[] = [
    { name: "LinkedIn", href: "https://linkedin.com/company/next-corporation", icon: LinkedInIcon },
    { name: "Twitter", href: "https://twitter.com/next_corporation", icon: TwitterIcon },
    { name: "Instagram", href: "https://instagram.com/next_corporation", icon: InstagramIcon }
  ];

  return (
    <footer className="bg-gradient-to-b from-white to-gray-50 dark:from-gray-900 dark:to-gray-950">
      <Container>
        <div className="mx-auto pt-16 pb-8">
          <div className="grid grid-cols-1 gap-12 lg:grid-cols-5">
            {/* Brand Section */}
            <div className="lg:col-span-2 space-y-8">
              <Logo />
              <p className="text-gray-600 dark:text-gray-400 max-w-md">
                Linguify est une plateforme d&apos;apprentissage des langues créée par Next-Corporation, conçue pour rendre 
                l&apos;apprentissage des langues accessible, engageant et efficace pour tous. Rejoignez-nous pour 
                éliminer les barrières linguistiques dans le monde entier.
              </p>
              <Link
                href="https://next-corporation.com"
                target="_blank"
                rel="noopener"
                className="inline-flex items-center px-4 py-2 rounded-lg bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-200 shadow-sm"
              >
                <span className="font-medium">Un produit Next-Corporation</span>
              </Link>
            </div>

            {/* Navigation Links */}
            <LinkSection title="Navigation" items={navigation} />

            {/* Legal Links */}
            <LinkSection title="Mentions légales" items={legal} />

            {/* Social Links */}
            <div className="space-y-4">
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white uppercase tracking-wider">
                Suivez-nous
              </h3>
              <div className="flex gap-4">
                {social.map((item) => {
                  const Icon = item.icon;
                  return (
                    <a
                      key={item.name}
                      href={item.href}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="p-2 rounded-full bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-50 hover:text-indigo-600 dark:hover:bg-gray-700 dark:hover:text-indigo-400 transition-all duration-200 shadow-sm"
                      aria-label={item.name}
                    >
                      <Icon size={20} />
                    </a>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Footer Bottom */}
          <div className="mt-12 pt-8 border-t border-gray-200 dark:border-gray-800">
            <div className="text-center">
              <p className="text-gray-600 dark:text-gray-400">
                © {new Date().getFullYear()} Next-Corporation. Tous droits réservés.
              </p>
              <p className="mt-2 text-sm text-gray-500 dark:text-gray-500">
                Linguify s&apos;engage à rendre l&apos;éducation accessible dans le monde entier.
              </p>
            </div>
          </div>
        </div>
      </Container>
    </footer>
  );
};