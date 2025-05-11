'use client';

import React, { useState, useEffect } from 'react';
import { Bell, BellOff, Info, Settings, AlertTriangle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { useNotifications } from '@/core/context/NotificationContext';
import { useTranslation } from '@/core/i18n/useTranslations';

interface NotificationPermissionProps {
  children?: React.ReactNode;
  variant?: 'card' | 'alert' | 'inline' | 'banner';
  onRequestPermission?: () => Promise<boolean>;
}

export default function NotificationPermission({
  children,
  variant = 'alert',
  onRequestPermission
}: NotificationPermissionProps) {
  const { t } = useTranslation();
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [permissionState, setPermissionState] = useState<NotificationPermission | 'unsupported'>('default');
  
  const { 
    hasNotificationPermission, 
    requestNotificationPermission 
  } = useNotifications();
  
  // Check notification permission status
  useEffect(() => {
    checkPermission();
  }, [hasNotificationPermission]);
  
  // Check current permission status
  const checkPermission = () => {
    if (!('Notification' in window)) {
      setPermissionState('unsupported');
      return;
    }
    
    setPermissionState(Notification.permission);
  };
  
  // Request permission
  const handleRequestPermission = async () => {
    if (!('Notification' in window)) {
      return;
    }

    try {
      // Use the prop if provided, otherwise use the context
      const permission = onRequestPermission
        ? await onRequestPermission()
        : await requestNotificationPermission();

      if (permission) {
        checkPermission();
      }
    } catch (error) {
      console.error('Error requesting notification permission:', error);
    }
  };
  
  // Show browser settings instructions for denied permission
  const handleShowSettings = () => {
    setIsDialogOpen(true);
  };
  
  // Don't render anything if already granted
  if (permissionState === 'granted' && !children) {
    return null;
  }
  
  // If custom children are provided, render them with the request permission function
  if (children) {
    return (
      <div onClick={handleRequestPermission}>
        {children}
      </div>
    );
  }
  
  // Render permission request UI based on variant
  if (variant === 'card') {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell className="h-5 w-5" />
            {t('notifications.permission.title')}
          </CardTitle>
          <CardDescription>
            {t('notifications.permission.description')}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {permissionState === 'default' && (
            <p className="text-sm text-muted-foreground">
              {t('notifications.permission.default_message')}
            </p>
          )}
          
          {permissionState === 'denied' && (
            <Alert variant="destructive" className="mb-4">
              <BellOff className="h-4 w-4" />
              <AlertTitle>{t('notifications.permission.denied_title')}</AlertTitle>
              <AlertDescription>
                {t('notifications.permission.denied_message')}
              </AlertDescription>
            </Alert>
          )}
          
          {permissionState === 'unsupported' && (
            <Alert className="mb-4">
              <Info className="h-4 w-4" />
              <AlertTitle>{t('notifications.permission.unsupported_title')}</AlertTitle>
              <AlertDescription>
                {t('notifications.permission.unsupported_message')}
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
        <CardFooter className="flex justify-end gap-3">
          {permissionState === 'default' && (
            <Button 
              onClick={handleRequestPermission}
              className="gap-2"
            >
              <Bell className="h-4 w-4" />
              {t('notifications.permission.enable')}
            </Button>
          )}
          
          {permissionState === 'denied' && (
            <Button
              variant="outline"
              onClick={handleShowSettings}
              className="gap-2"
            >
              <Settings className="h-4 w-4" />
              {t('notifications.permission.browser_settings')}
            </Button>
          )}
        </CardFooter>
      </Card>
    );
  }
  
  if (variant === 'alert') {
    if (permissionState === 'default') {
      return (
        <Alert className="mb-4">
          <Bell className="h-4 w-4" />
          <AlertTitle>{t('notifications.permission.alert_title')}</AlertTitle>
          <AlertDescription className="flex flex-col gap-2">
            <p>{t('notifications.permission.alert_description')}</p>
            <div>
              <Button 
                size="sm" 
                onClick={handleRequestPermission}
                className="gap-2"
              >
                <Bell className="h-3 w-3" />
                {t('notifications.permission.enable')}
              </Button>
            </div>
          </AlertDescription>
        </Alert>
      );
    }
    
    if (permissionState === 'denied') {
      return (
        <Alert variant="destructive" className="mb-4">
          <BellOff className="h-4 w-4" />
          <AlertTitle>{t('notifications.permission.denied_title')}</AlertTitle>
          <AlertDescription className="flex flex-col gap-2">
            <p>{t('notifications.permission.denied_message')}</p>
            <div>
              <Button 
                size="sm"
                variant="outline" 
                onClick={handleShowSettings}
                className="gap-2"
              >
                <Settings className="h-3 w-3" />
                {t('notifications.permission.browser_settings')}
              </Button>
              
              <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>{t('notifications.permission.settings_dialog_title')}</DialogTitle>
                    <DialogDescription>
                      {t('notifications.permission.settings_dialog_description')}
                    </DialogDescription>
                  </DialogHeader>
                  
                  <div className="space-y-4 py-4">
                    <h3 className="font-medium">{t('notifications.permission.browser_instructions')}</h3>
                    
                    <div className="ml-6 space-y-2">
                      <h4 className="font-medium">Chrome</h4>
                      <ol className="list-decimal pl-5 space-y-1 text-sm">
                        <li>{t('notifications.permission.chrome_step1')}</li>
                        <li>{t('notifications.permission.chrome_step2')}</li>
                        <li>{t('notifications.permission.chrome_step3')}</li>
                        <li>{t('notifications.permission.chrome_step4')}</li>
                      </ol>
                    </div>
                    
                    <div className="ml-6 space-y-2">
                      <h4 className="font-medium">Firefox</h4>
                      <ol className="list-decimal pl-5 space-y-1 text-sm">
                        <li>{t('notifications.permission.firefox_step1')}</li>
                        <li>{t('notifications.permission.firefox_step2')}</li>
                        <li>{t('notifications.permission.firefox_step3')}</li>
                      </ol>
                    </div>
                    
                    <div className="ml-6 space-y-2">
                      <h4 className="font-medium">Safari</h4>
                      <ol className="list-decimal pl-5 space-y-1 text-sm">
                        <li>{t('notifications.permission.safari_step1')}</li>
                        <li>{t('notifications.permission.safari_step2')}</li>
                        <li>{t('notifications.permission.safari_step3')}</li>
                      </ol>
                    </div>
                  </div>
                  
                  <DialogFooter>
                    <Button onClick={() => setIsDialogOpen(false)}>
                      {t('notifications.permission.close')}
                    </Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            </div>
          </AlertDescription>
        </Alert>
      );
    }
  }
  
  // Banner variant (for notification dropdown)
  if (variant === 'banner') {
    return (
      <div className="p-3 bg-amber-50 dark:bg-amber-950/20 border-t border-amber-100 dark:border-amber-800">
        <div className="flex gap-2">
          <AlertTriangle className="h-5 w-5 text-amber-500 flex-shrink-0" />
          <div className="flex-1">
            <p className="text-sm font-medium">{t('notifications.permission.enable_title')}</p>
            <p className="text-xs text-muted-foreground mt-1">{t('notifications.permission.banner_description')}</p>
            <div className="mt-2 flex gap-2">
              <Button
                size="sm"
                className="h-8"
                onClick={handleRequestPermission}
              >
                {t('notifications.permission.enable')}
              </Button>
              <Button
                size="sm"
                variant="outline"
                className="h-8"
                onClick={() => setIsDialogOpen(true)}
              >
                {t('common.learn_more')}
              </Button>

              <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>{t('notifications.permission.settings_dialog_title')}</DialogTitle>
                    <DialogDescription>
                      {t('notifications.permission.settings_dialog_description')}
                    </DialogDescription>
                  </DialogHeader>

                  <div className="space-y-4 py-4">
                    <h3 className="font-medium">{t('notifications.permission.why_enable')}</h3>
                    <ul className="ml-6 list-disc space-y-1 text-sm">
                      <li>{t('notifications.permission.benefit1')}</li>
                      <li>{t('notifications.permission.benefit2')}</li>
                      <li>{t('notifications.permission.benefit3')}</li>
                    </ul>
                  </div>

                  <DialogFooter>
                    <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
                      {t('common.cancel')}
                    </Button>
                    <Button onClick={handleRequestPermission}>
                      {t('notifications.permission.enable')}
                    </Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Inline variant
  return (
    <div className="flex items-center gap-2">
      {permissionState === 'default' && (
        <Button
          size="sm"
          onClick={handleRequestPermission}
          className="gap-2"
        >
          <Bell className="h-3 w-3" />
          {t('notifications.permission.enable')}
        </Button>
      )}

      {permissionState === 'denied' && (
        <>
          <Button
            size="sm"
            variant="outline"
            onClick={handleShowSettings}
            className="gap-2"
          >
            <Settings className="h-3 w-3" />
            {t('notifications.permission.browser_settings')}
          </Button>

          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>{t('notifications.permission.settings_dialog_title')}</DialogTitle>
                <DialogDescription>
                  {t('notifications.permission.settings_dialog_description')}
                </DialogDescription>
              </DialogHeader>

              <div className="space-y-4 py-4">
                <h3 className="font-medium">{t('notifications.permission.browser_instructions')}</h3>

                <div className="ml-6 space-y-2">
                  <h4 className="font-medium">Chrome</h4>
                  <ol className="list-decimal pl-5 space-y-1 text-sm">
                    <li>{t('notifications.permission.chrome_step1')}</li>
                    <li>{t('notifications.permission.chrome_step2')}</li>
                    <li>{t('notifications.permission.chrome_step3')}</li>
                    <li>{t('notifications.permission.chrome_step4')}</li>
                  </ol>
                </div>

                <div className="ml-6 space-y-2">
                  <h4 className="font-medium">Firefox</h4>
                  <ol className="list-decimal pl-5 space-y-1 text-sm">
                    <li>{t('notifications.permission.firefox_step1')}</li>
                    <li>{t('notifications.permission.firefox_step2')}</li>
                    <li>{t('notifications.permission.firefox_step3')}</li>
                  </ol>
                </div>

                <div className="ml-6 space-y-2">
                  <h4 className="font-medium">Safari</h4>
                  <ol className="list-decimal pl-5 space-y-1 text-sm">
                    <li>{t('notifications.permission.safari_step1')}</li>
                    <li>{t('notifications.permission.safari_step2')}</li>
                    <li>{t('notifications.permission.safari_step3')}</li>
                  </ol>
                </div>
              </div>

              <DialogFooter>
                <Button onClick={() => setIsDialogOpen(false)}>
                  {t('notifications.permission.close')}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </>
      )}
    </div>
  );
}