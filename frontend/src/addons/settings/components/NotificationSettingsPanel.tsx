'use client';

import React from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Bell, BellRing, Settings, ToggleLeft } from 'lucide-react';
import { useTranslation } from '@/core/i18n/useTranslations';
import { NotificationSubscriptionManager, PushNotificationManager } from '@/components/notifications';
import { Button } from '@/components/ui/button';

interface NotificationSettingsPanelProps {
  defaultTab?: string;
}

export default function NotificationSettingsPanel({ defaultTab = 'channels' }: NotificationSettingsPanelProps) {
  const { t } = useTranslation();
  
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">{t('settings.notifications.title')}</h2>
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
            <CardHeader>
              <CardTitle>{t('settings.notifications.channels_title')}</CardTitle>
              <CardDescription>
                {t('settings.notifications.channels_description')}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Email Notifications */}
              <div className="grid gap-6">
                <div className="flex items-center justify-between space-x-4">
                  <div>
                    <h3 className="font-medium">{t('settings.notifications.email')}</h3>
                    <p className="text-sm text-muted-foreground">{t('settings.notifications.email_description')}</p>
                  </div>
                  <Button variant="outline" size="sm">
                    {t('settings.notifications.configure')}
                  </Button>
                </div>
                
                {/* In-app Notifications */}
                <div className="flex items-center justify-between space-x-4">
                  <div>
                    <h3 className="font-medium">{t('settings.notifications.in_app')}</h3>
                    <p className="text-sm text-muted-foreground">{t('settings.notifications.in_app_description')}</p>
                  </div>
                  <Button variant="outline" size="sm">
                    {t('settings.notifications.configure')}
                  </Button>
                </div>
                
                {/* Push Notifications */}
                <div className="flex items-center justify-between space-x-4">
                  <div>
                    <h3 className="font-medium">{t('settings.notifications.browser_push')}</h3>
                    <p className="text-sm text-muted-foreground">{t('settings.notifications.browser_push_description')}</p>
                  </div>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => {
                      document.querySelector('[data-tab="push"]')?.click();
                    }}
                  >
                    {t('settings.notifications.configure')}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        
        {/* Notification Preferences Tab */}
        <TabsContent value="preferences" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>{t('settings.notifications.preferences_title')}</CardTitle>
              <CardDescription>
                {t('settings.notifications.preferences_description')}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <NotificationSubscriptionManager />
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>{t('settings.notifications.quiet_hours_title')}</CardTitle>
              <CardDescription>
                {t('settings.notifications.quiet_hours_description')}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                {t('settings.notifications.quiet_hours_coming_soon')}
              </p>
            </CardContent>
          </Card>
        </TabsContent>
        
        {/* Push Notifications Tab */}
        <TabsContent value="push" className="space-y-4">
          <PushNotificationManager />
          
          <Card>
            <CardHeader>
              <CardTitle>{t('settings.notifications.push_settings_title')}</CardTitle>
              <CardDescription>
                {t('settings.notifications.push_settings_description')}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                {t('settings.notifications.push_settings_coming_soon')}
              </p>
            </CardContent>
          </Card>
        </TabsContent>
        
        {/* Advanced Settings Tab */}
        <TabsContent value="advanced" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>{t('settings.notifications.advanced_title')}</CardTitle>
              <CardDescription>
                {t('settings.notifications.advanced_description')}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4">
                <div>
                  <h3 className="font-medium mb-2">{t('settings.notifications.data_retention')}</h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    {t('settings.notifications.data_retention_description')}
                  </p>
                  <Button variant="outline" size="sm">
                    {t('settings.notifications.clean_notifications')}
                  </Button>
                </div>
                
                <div>
                  <h3 className="font-medium mb-2">{t('settings.notifications.export')}</h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    {t('settings.notifications.export_description')}
                  </p>
                  <Button variant="outline" size="sm">
                    {t('settings.notifications.export_data')}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}