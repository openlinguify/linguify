'use client';

import React from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Bell, BellRing, Settings, ToggleLeft, Clock, Save } from 'lucide-react';
import { useTranslation } from '@/core/i18n/useTranslations';
import { triggerLanguageTransition, TransitionType } from "@/core/i18n/LanguageTransition";
import { NotificationSubscriptionManager, PushNotificationManager } from '@/components/notifications';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';

interface NotificationSettingsPanelProps {
  defaultTab?: string;
}

// Helper components for settings UI
interface SettingsToggleProps {
  id: string;
  label: string;
  description?: string;
  checked: boolean;
  onCheckedChange: (checked: boolean) => void;
  disabled?: boolean;
  icon?: React.ReactNode;
}

interface SettingsCardHeaderProps {
  title: string;
  description: string;
  icon?: React.ReactNode;
  variant?: "default" | "destructive";
}

interface SaveButtonProps {
  onClick: () => void;
  isLoading?: boolean;
  className?: string;
}

function SettingsCardHeader({ title, description, icon, variant = "default" }: SettingsCardHeaderProps) {
  const bgClass = variant === "destructive" ? "bg-destructive/5" : "bg-muted/30";
  const titleClass = variant === "destructive" ? "text-destructive" : "";
  
  return (
    <CardHeader className={`pb-3 ${bgClass}`}>
      <CardTitle className={titleClass}>
        {icon ? (
          <div className="flex items-center gap-2">
            {icon}
            {title}
          </div>
        ) : (
          title
        )}
      </CardTitle>
      <CardDescription>
        {description}
      </CardDescription>
    </CardHeader>
  );
}

function SaveButton({ onClick, isLoading = false, className = "" }: SaveButtonProps) {
  const { t, locale } = useTranslation();
  
  const handleClick = () => {
    // Show the context-aware transition message
    triggerLanguageTransition(locale, TransitionType.NOTIFICATION);
    
    // Call the original onClick handler
    if (onClick) {
      onClick();
    }
  };
  
  return (
    <Button 
      onClick={handleClick} 
      className={`gap-2 ${className}`}
      disabled={isLoading}
    >
      <Save className="h-4 w-4" />
      {isLoading ? t('common.saving') : t('common.save')}
    </Button>
  );
}

function SettingsToggle({ 
  id, 
  label, 
  description, 
  checked, 
  onCheckedChange, 
  disabled = false,
  icon
}: SettingsToggleProps) {
  return (
    <div className="flex items-center justify-between">
      <div className="space-y-0.5">
        <Label htmlFor={id} className={`flex items-center gap-2 ${description ? '' : 'text-base'}`}>
          {icon && icon}
          {label}
        </Label>
        {description && (
          <p className="text-sm text-muted-foreground">
            {description}
          </p>
        )}
      </div>
      <Switch
        id={id}
        checked={checked}
        onCheckedChange={onCheckedChange}
        disabled={disabled}
      />
    </div>
  );
}

export default function NotificationSettingsPanel({ defaultTab = 'channels' }: NotificationSettingsPanelProps) {
  const { t } = useTranslation();
  
  return (
    <div className="h-full w-full bg-gray-50 dark:bg-gray-900 overflow-hidden p-0 m-0 space-y-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold tracking-tight mb-1">{t('settings.notifications.title')}</h2>
        <p className="text-muted-foreground">
          {t('settings.notifications.description')}
        </p>
      </div>
      
      <Tabs defaultValue={defaultTab} className="space-y-4">
        <TabsList>
          <TabsTrigger value="channels" className="flex items-center gap-2">
            <Bell className="h-4 w-4" />
            <span>{t('settings.notifications.channels')}</span>
          </TabsTrigger>
          <TabsTrigger value="preferences" className="flex items-center gap-2">
            <ToggleLeft className="h-4 w-4" />
            <span>{t('settings.notifications.preferences')}</span>
          </TabsTrigger>
          <TabsTrigger value="push" className="flex items-center gap-2">
            <BellRing className="h-4 w-4" />
            <span>{t('settings.notifications.push')}</span>
          </TabsTrigger>
          <TabsTrigger value="advanced" className="flex items-center gap-2">
            <Settings className="h-4 w-4" />
            <span>{t('settings.notifications.advanced')}</span>
          </TabsTrigger>
        </TabsList>
        
        {/* Notification Channels Tab */}
        <TabsContent value="channels" className="space-y-4">
          <Card>
            <SettingsCardHeader
              title={t('settings.notifications.channels_title')}
              description={t('settings.notifications.channels_description')}
              icon={<Bell className="h-5 w-5" />}
            />
            <CardContent className="space-y-4">
              {/* Email Notifications */}
              <div className="grid gap-6">
                <SettingsToggle
                  id="email-notifications"
                  label={t('settings.notifications.email')}
                  description={t('settings.notifications.email_description')}
                  checked={true}
                  onCheckedChange={() => {}}
                  icon={<Bell className="h-4 w-4" />}
                />
                
                {/* In-app Notifications */}
                <SettingsToggle
                  id="in-app-notifications"
                  label={t('settings.notifications.in_app')}
                  description={t('settings.notifications.in_app_description')}
                  checked={true}
                  onCheckedChange={() => {}}
                  icon={<BellRing className="h-4 w-4" />}
                />
                
                {/* Push Notifications */}
                <div className="flex items-center justify-between space-x-4">
                  <div className="space-y-0.5">
                    <Label className="flex items-center gap-2">
                      <Settings className="h-4 w-4" />
                      {t('settings.notifications.browser_push')}
                    </Label>
                    <p className="text-sm text-muted-foreground">
                      {t('settings.notifications.browser_push_description')}
                    </p>
                  </div>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => {
                      // Find and click the push tab trigger
                      const pushTab = document.querySelector('[value="push"]') as HTMLElement;
                      if (pushTab) pushTab.click();
                    }}
                  >
                    {t('settings.notifications.configure')}
                  </Button>
                </div>
              </div>
            </CardContent>
            <CardFooter className="flex justify-end border-t pt-4">
              <SaveButton onClick={() => {}} />
            </CardFooter>
          </Card>
        </TabsContent>
        
        {/* Notification Preferences Tab */}
        <TabsContent value="preferences" className="space-y-4">
          <Card>
            <SettingsCardHeader
              title={t('settings.notifications.preferences_title')}
              description={t('settings.notifications.preferences_description')}
              icon={<ToggleLeft className="h-5 w-5" />}
            />
            <CardContent>
              <NotificationSubscriptionManager />
            </CardContent>
            <CardFooter className="flex justify-end border-t pt-4">
              <SaveButton onClick={() => {}} />
            </CardFooter>
          </Card>
          
          <Card>
            <SettingsCardHeader
              title={t('settings.notifications.quiet_hours_title')}
              description={t('settings.notifications.quiet_hours_description')}
              icon={<Clock className="h-5 w-5" />}
            />
            <CardContent>
              <p className="text-sm text-muted-foreground">
                {t('settings.notifications.quiet_hours_coming_soon')}
              </p>
            </CardContent>
            <CardFooter className="flex justify-end border-t pt-4">
              <Button variant="outline" disabled>
                {t('common.coming_soon')}
              </Button>
            </CardFooter>
          </Card>
        </TabsContent>
        
        {/* Push Notifications Tab */}
        <TabsContent value="push" className="space-y-4">
          <Card>
            <SettingsCardHeader
              title={t('settings.notifications.push_title')}
              description={t('settings.notifications.push_description')}
              icon={<BellRing className="h-5 w-5" />}
            />
            <CardContent>
              <PushNotificationManager />
            </CardContent>
            <CardFooter className="flex justify-end border-t pt-4">
              <SaveButton onClick={() => {}} />
            </CardFooter>
          </Card>
          
          <Card>
            <SettingsCardHeader
              title={t('settings.notifications.push_settings_title')}
              description={t('settings.notifications.push_settings_description')}
              icon={<Settings className="h-5 w-5" />}
            />
            <CardContent>
              <p className="text-sm text-muted-foreground">
                {t('settings.notifications.push_settings_coming_soon')}
              </p>
            </CardContent>
            <CardFooter className="flex justify-end border-t pt-4">
              <Button variant="outline" disabled>
                {t('common.coming_soon')}
              </Button>
            </CardFooter>
          </Card>
        </TabsContent>
        
        {/* Advanced Settings Tab */}
        <TabsContent value="advanced" className="space-y-4">
          <Card>
            <SettingsCardHeader
              title={t('settings.notifications.advanced_title')}
              description={t('settings.notifications.advanced_description')}
              icon={<Settings className="h-5 w-5" />}
            />
            <CardContent>
              <div className="grid gap-6">
                <div className="space-y-4">
                  <div className="space-y-1.5">
                    <Label className="flex items-center gap-2 text-base">
                      <Clock className="h-4 w-4" />
                      {t('settings.notifications.data_retention')}
                    </Label>
                    <p className="text-sm text-muted-foreground">
                      {t('settings.notifications.data_retention_description')}
                    </p>
                  </div>
                  <Button variant="outline" size="sm" className="w-auto inline-flex">
                    {t('settings.notifications.clean_notifications')}
                  </Button>
                </div>
                
                <div className="space-y-4">
                  <div className="space-y-1.5">
                    <Label className="flex items-center gap-2 text-base">
                      <Save className="h-4 w-4" />
                      {t('settings.notifications.export')}
                    </Label>
                    <p className="text-sm text-muted-foreground">
                      {t('settings.notifications.export_description')}
                    </p>
                  </div>
                  <Button variant="outline" size="sm" className="w-auto inline-flex">
                    {t('settings.notifications.export_data')}
                  </Button>
                </div>
              </div>
            </CardContent>
            <CardFooter className="flex justify-end border-t pt-4">
              <SaveButton onClick={() => {}} />
            </CardFooter>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}