'use client';

import React, { useState, useEffect } from 'react';
import { 
  BellRing, 
  BellOff, 
  Loader2, 
  AlertTriangle, 
  CheckCircle, 
  ChevronRight, 
  SmartphoneNfc, 
  Laptop 
} from 'lucide-react';
import { useTranslation } from '@/core/i18n/useTranslations';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Switch } from '@/components/ui/switch';
import { 
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { 
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import { toast } from '@/components/ui/use-toast';
import pushNotificationService from '@/core/api/pushNotificationService';
import { useAuthContext } from '@/core/auth/AuthAdapter';

interface PushNotificationManagerProps {
  className?: string;
}

export function PushNotificationManager({ className }: PushNotificationManagerProps) {
  const { t } = useTranslation();
  const { isAuthenticated } = useAuthContext();
  
  // State
  const [isSupported, setIsSupported] = useState(false);
  const [permission, setPermission] = useState<NotificationPermission | 'unsupported'>('default');
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [devices, setDevices] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  
  // Initialize
  useEffect(() => {
    if (typeof window === 'undefined') return;
    
    const initPushNotifications = async () => {
      setIsLoading(true);
      
      try {
        // Check if push notifications are supported
        const supported = pushNotificationService.isPushSupported();
        setIsSupported(supported);
        
        if (!supported) {
          setPermission('unsupported');
          setIsLoading(false);
          return;
        }
        
        // Get permission status
        const permissionStatus = pushNotificationService.getPermissionStatus();
        setPermission(permissionStatus);
        
        // Initialize service worker if authenticated
        if (isAuthenticated) {
          const initialized = await pushNotificationService.init();
          
          if (initialized) {
            // Check if already subscribed
            const subscribed = await pushNotificationService.isSubscribed();
            setIsSubscribed(subscribed);
            
            // TODO: Load devices from the API
            setDevices(['This device']);
          }
        }
      } catch (error) {
        console.error('Error initializing push notifications:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    initPushNotifications();
  }, [isAuthenticated]);
  
  // Request permission and subscribe
  const handleEnablePush = async () => {
    setIsLoading(true);
    
    try {
      // Request permission first
      const permissionGranted = await pushNotificationService.requestPermission();
      setPermission(Notification.permission);
      
      if (!permissionGranted) {
        toast({
          title: t('notifications.push.permission_denied'),
          description: t('notifications.push.permission_denied_description'),
          variant: 'destructive',
        });
        return;
      }
      
      // Initialize service worker if not already done
      await pushNotificationService.init();
      
      // Subscribe to push notifications
      const subscription = await pushNotificationService.subscribe();
      
      if (subscription) {
        setIsSubscribed(true);
        setDevices(['This device']);
        
        toast({
          title: t('notifications.push.enabled'),
          description: t('notifications.push.enabled_description'),
        });
      } else {
        toast({
          title: t('notifications.push.error'),
          description: t('notifications.push.error_description'),
          variant: 'destructive',
        });
      }
    } catch (error) {
      console.error('Error enabling push notifications:', error);
      toast({
        title: t('notifications.push.error'),
        description: String(error),
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  // Unsubscribe from push notifications
  const handleDisablePush = async () => {
    setIsLoading(true);
    
    try {
      const unsubscribed = await pushNotificationService.unsubscribe();
      
      if (unsubscribed) {
        setIsSubscribed(false);
        setDevices([]);
        
        toast({
          title: t('notifications.push.disabled'),
          description: t('notifications.push.disabled_description'),
        });
      } else {
        toast({
          title: t('notifications.push.error'),
          description: t('notifications.push.error_disable_description'),
          variant: 'destructive',
        });
      }
    } catch (error) {
      console.error('Error disabling push notifications:', error);
      toast({
        title: t('notifications.push.error'),
        description: String(error),
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  // Send a test notification
  const handleSendTestNotification = async () => {
    try {
      await pushNotificationService.sendTestNotification();
      toast({
        title: t('notifications.push.test_sent'),
        description: t('notifications.push.test_sent_description'),
      });
    } catch (error) {
      console.error('Error sending test notification:', error);
      toast({
        title: t('notifications.push.error'),
        description: String(error),
        variant: 'destructive',
      });
    }
  };
  
  // Toggle push notifications
  const handleToggle = (checked: boolean) => {
    if (checked) {
      handleEnablePush();
    } else {
      handleDisablePush();
    }
  };
  
  if (!isAuthenticated) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle>{t('notifications.push.title')}</CardTitle>
          <CardDescription>{t('notifications.push.login_required')}</CardDescription>
        </CardHeader>
        <CardFooter>
          <Button disabled>{t('notifications.push.login_first')}</Button>
        </CardFooter>
      </Card>
    );
  }
  
  return (
    <Card className={className}>
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center gap-2">
          <BellRing className="h-5 w-5" />
          {t('notifications.push.title')}
        </CardTitle>
        <CardDescription>
          {t('notifications.push.description')}
        </CardDescription>
      </CardHeader>
      
      <CardContent className="pb-2">
        {isLoading ? (
          <div className="flex justify-center py-6">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        ) : (
          <>
            {/* Not supported */}
            {!isSupported && (
              <div className="flex items-start gap-3 p-3 border rounded-lg bg-muted/50">
                <AlertTriangle className="h-5 w-5 text-amber-500 mt-0.5" />
                <div>
                  <h4 className="font-medium text-sm">{t('notifications.push.not_supported_title')}</h4>
                  <p className="text-sm text-muted-foreground">{t('notifications.push.not_supported_description')}</p>
                </div>
              </div>
            )}
            
            {/* Permission denied */}
            {permission === 'denied' && (
              <div className="flex items-start gap-3 p-3 border rounded-lg bg-destructive/10">
                <BellOff className="h-5 w-5 text-destructive mt-0.5" />
                <div>
                  <h4 className="font-medium text-sm">{t('notifications.push.permission_denied_title')}</h4>
                  <p className="text-sm text-muted-foreground">{t('notifications.push.permission_denied_description')}</p>
                  <Button 
                    size="sm" 
                    variant="outline" 
                    className="mt-2"
                    onClick={() => setIsDialogOpen(true)}
                  >
                    {t('notifications.push.show_instructions')}
                  </Button>
                </div>
              </div>
            )}
            
            {/* Permission granted and supported */}
            {isSupported && permission === 'granted' && (
              <div className="space-y-4">
                {/* Subscription toggle */}
                <div className="flex items-center justify-between space-x-2">
                  <div className="flex-1 space-y-1">
                    <div className="font-medium text-sm">{t('notifications.push.enable')}</div>
                    <div className="text-xs text-muted-foreground">
                      {isSubscribed 
                        ? t('notifications.push.receiving_notifications')
                        : t('notifications.push.not_receiving_notifications')
                      }
                    </div>
                  </div>
                  <Switch
                    checked={isSubscribed}
                    onCheckedChange={handleToggle}
                    disabled={isLoading}
                    aria-label={t('notifications.push.toggle_label')}
                  />
                </div>
                
                {/* Registered devices */}
                {isSubscribed && devices.length > 0 && (
                  <Accordion type="single" collapsible className="w-full">
                    <AccordionItem value="devices">
                      <AccordionTrigger className="text-sm">
                        {t('notifications.push.registered_devices')} ({devices.length})
                      </AccordionTrigger>
                      <AccordionContent>
                        <ul className="space-y-2">
                          {devices.map((device, index) => (
                            <li key={index} className="flex items-center justify-between py-1 px-2 rounded-md bg-muted/40">
                              <div className="flex items-center gap-2">
                                {device === 'This device' ? (
                                  <Laptop className="h-4 w-4 text-blue-500" />
                                ) : (
                                  <SmartphoneNfc className="h-4 w-4 text-green-500" />
                                )}
                                <span className="text-sm">{device}</span>
                                {device === 'This device' && (
                                  <span className="text-xs bg-blue-500/10 text-blue-600 dark:text-blue-400 px-1.5 py-0.5 rounded-full">
                                    {t('notifications.push.current_device')}
                                  </span>
                                )}
                              </div>
                              {device === 'This device' && (
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  className="h-7 px-2 text-xs"
                                  onClick={handleDisablePush}
                                >
                                  {t('notifications.push.remove')}
                                </Button>
                              )}
                            </li>
                          ))}
                        </ul>
                      </AccordionContent>
                    </AccordionItem>
                  </Accordion>
                )}
                
                {/* Test notification button (only if subscribed) */}
                {isSubscribed && (
                  <div className="flex justify-end">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={handleSendTestNotification}
                      disabled={isLoading}
                    >
                      {t('notifications.push.send_test')}
                    </Button>
                  </div>
                )}
              </div>
            )}
            
            {/* Permission not granted but supported */}
            {isSupported && permission === 'default' && (
              <div className="flex items-start gap-3 p-3 border rounded-lg bg-primary/10">
                <BellRing className="h-5 w-5 text-primary mt-0.5" />
                <div>
                  <h4 className="font-medium text-sm">{t('notifications.push.permission_required_title')}</h4>
                  <p className="text-sm text-muted-foreground">{t('notifications.push.permission_required_description')}</p>
                  <Button 
                    size="sm" 
                    className="mt-2"
                    onClick={handleEnablePush}
                    disabled={isLoading}
                  >
                    {isLoading ? (
                      <>
                        <Loader2 className="h-3 w-3 mr-2 animate-spin" />
                        {t('common.loading')}
                      </>
                    ) : (
                      t('notifications.push.enable_now')
                    )}
                  </Button>
                </div>
              </div>
            )}
          </>
        )}
      </CardContent>
      
      {/* Help dialog for browser settings */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t('notifications.push.browser_settings_title')}</DialogTitle>
            <DialogDescription>
              {t('notifications.push.browser_settings_description')}
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div className="space-y-2">
              <h3 className="font-medium">{t('notifications.push.chrome')}</h3>
              <ol className="list-decimal pl-5 space-y-1 text-sm">
                <li>{t('notifications.push.chrome_step1')}</li>
                <li>{t('notifications.push.chrome_step2')}</li>
                <li>{t('notifications.push.chrome_step3')}</li>
                <li>{t('notifications.push.chrome_step4')}</li>
              </ol>
            </div>
            
            <div className="space-y-2">
              <h3 className="font-medium">{t('notifications.push.firefox')}</h3>
              <ol className="list-decimal pl-5 space-y-1 text-sm">
                <li>{t('notifications.push.firefox_step1')}</li>
                <li>{t('notifications.push.firefox_step2')}</li>
                <li>{t('notifications.push.firefox_step3')}</li>
              </ol>
            </div>
            
            <div className="space-y-2">
              <h3 className="font-medium">{t('notifications.push.safari')}</h3>
              <ol className="list-decimal pl-5 space-y-1 text-sm">
                <li>{t('notifications.push.safari_step1')}</li>
                <li>{t('notifications.push.safari_step2')}</li>
                <li>{t('notifications.push.safari_step3')}</li>
              </ol>
            </div>
          </div>
          
          <DialogFooter>
            <Button onClick={() => setIsDialogOpen(false)}>
              {t('common.close')}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </Card>
  );
}

export default PushNotificationManager;