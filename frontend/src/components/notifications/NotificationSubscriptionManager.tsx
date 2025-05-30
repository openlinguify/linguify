'use client';

import React, { useState, useEffect } from 'react';
import { 
  Bell, 
  BookOpen, 
  Trophy, 
  AlertCircle, 
  Info, 
  Check, 
  Calendar,
  MessageSquare,
  Star
} from "lucide-react";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { useNotifications } from '@/core/context/NotificationContext';
import { NotificationType } from '@/core/types/notification.types';
import { useTranslation } from "@/core/i18n/useTranslations";
import { toast } from '@/components/ui/use-toast';
import { useAuthContext } from '@/core/auth/AuthAdapter';
import notificationWebsocket from '@/core/api/notificationWebsocket';

interface SubscriptionSetting {
  type: NotificationType;
  label: string;
  description: string;
  icon: React.ReactNode;
  subscribed: boolean;
}

export function NotificationSubscriptionManager() {
  const { t } = useTranslation();
  const { user } = useAuthContext();
  const { hasNotificationPermission, requestNotificationPermission } = useNotifications();
  
  // Track WebSocket connection state
  const [connected, setConnected] = useState(false);
  
  // State for subscription settings
  const [settings, setSettings] = useState<SubscriptionSetting[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [saveInProgress, setSaveInProgress] = useState(false);
  
  // Track changes for save button
  const [hasChanges, setHasChanges] = useState(false);
  
  // Dialog state
  const [isOpen, setIsOpen] = useState(false);
  
  // Initialize WebSocket connection listener
  useEffect(() => {
    if (!user?.token) return;
    
    const handleConnectionChange = (isConnected: boolean) => {
      setConnected(isConnected);
      
      // If we just connected, load subscriptions
      if (isConnected && isLoading) {
        loadCurrentSubscriptions();
      }
    };
    
    // Add connection listener
    notificationWebsocket.addConnectionListener(handleConnectionChange);
    
    // Check if already connected
    if (notificationWebsocket.isConnected()) {
      setConnected(true);
      loadCurrentSubscriptions();
    }
    
    return () => {
      notificationWebsocket.removeConnectionListener(handleConnectionChange);
    };
  }, [user, isLoading]);
  
  // Setup message listener for subscription updates
  useEffect(() => {
    if (!connected) return;
    
    // Custom event handler for WebSocket messages
    const handleWebSocketMessage = (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data);
        
        // Handle initial connection data
        if (data.type === 'connection_established' && data.subscriptions) {
          handleSubscriptionsUpdate(data.subscriptions);
        }
        
        // Handle subscription update confirmations
        if (data.type === 'subscription_update' && data.success) {
          toast({
            title: t('notifications.subscription_updated'),
            description: t('notifications.subscription_success'),
            duration: 3000,
          });
        }
      } catch (error) {
        console.error('Error handling WebSocket message:', error);
      }
    };
    
    // Add event listener if WebSocket is available
    if (typeof window !== 'undefined' && notificationWebsocket.isConnected()) {
      // @ts-ignore - We need to access the private socket property
      const socket = (notificationWebsocket as any).socket;
      if (socket) {
        socket.addEventListener('message', handleWebSocketMessage);
      }
    }
    
    return () => {
      // Clean up event listener
      if (typeof window !== 'undefined' && notificationWebsocket.isConnected()) {
        // @ts-ignore - We need to access the private socket property
        const socket = (notificationWebsocket as any).socket;
        if (socket) {
          socket.removeEventListener('message', handleWebSocketMessage);
        }
      }
    };
  }, [connected, t]);
  
  // Load current subscriptions from WebSocket or settings
  const loadCurrentSubscriptions = () => {
    // Create default settings
    const defaultSettings: SubscriptionSetting[] = [
      {
        type: NotificationType.LESSON_REMINDER,
        label: t('notifications.types.lesson_reminder'),
        description: t('notifications.descriptions.lesson_reminder'),
        icon: <BookOpen className="h-5 w-5 text-blue-500" />,
        subscribed: true
      },
      {
        type: NotificationType.FLASHCARD,
        label: t('notifications.types.flashcard'),
        description: t('notifications.descriptions.flashcard'),
        icon: <MessageSquare className="h-5 w-5 text-green-500" />,
        subscribed: true
      },
      {
        type: NotificationType.ACHIEVEMENT,
        label: t('notifications.types.achievement'),
        description: t('notifications.descriptions.achievement'),
        icon: <Trophy className="h-5 w-5 text-yellow-500" />,
        subscribed: true
      },
      {
        type: NotificationType.STREAK,
        label: t('notifications.types.streak'),
        description: t('notifications.descriptions.streak'),
        icon: <Calendar className="h-5 w-5 text-orange-500" />,
        subscribed: true
      },
      {
        type: NotificationType.SYSTEM,
        label: t('notifications.types.system'),
        description: t('notifications.descriptions.system'),
        icon: <AlertCircle className="h-5 w-5 text-purple-500" />,
        subscribed: true
      },
      {
        type: NotificationType.INFO,
        label: t('notifications.types.info'),
        description: t('notifications.descriptions.info'),
        icon: <Info className="h-5 w-5 text-sky-500" />,
        subscribed: true
      },
      {
        type: NotificationType.PROGRESS,
        label: t('notifications.types.progress'),
        description: t('notifications.descriptions.progress'),
        icon: <Star className="h-5 w-5 text-pink-500" />,
        subscribed: true
      }
    ];
    
    setSettings(defaultSettings);
    setIsLoading(false);
    setHasChanges(false);
  };
  
  // Update settings based on subscriptions array from server
  const handleSubscriptionsUpdate = (subscriptions: string[]) => {
    setSettings(prev => prev.map(setting => ({
      ...setting,
      subscribed: subscriptions.includes(setting.type)
    })));
    
    setIsLoading(false);
    setHasChanges(false);
  };
  
  // Toggle a subscription setting
  const toggleSubscription = (type: NotificationType) => {
    if (saveInProgress) return;
    
    setSettings(prev => prev.map(setting => 
      setting.type === type 
        ? { ...setting, subscribed: !setting.subscribed } 
        : setting
    ));
    
    setHasChanges(true);
  };
  
  // Save changes to subscriptions
  const saveChanges = () => {
    if (!connected || !hasChanges) return;
    
    setSaveInProgress(true);
    
    // Process each change
    const promises = settings.map(setting => {
      // Determine action based on subscription state
      const action = setting.subscribed ? 'subscribe' : 'unsubscribe';
      
      // Send subscription message
      return new Promise<void>((resolve, reject) => {
        try {
          // Only update if connected
          if (notificationWebsocket.isConnected()) {
            // @ts-ignore - We need to access the private socket property
            const socket = (notificationWebsocket as any).socket;
            
            if (socket) {
              socket.send(JSON.stringify({
                type: 'subscription',
                action: action,
                notification_type: setting.type
              }));
              resolve();
            } else {
              reject(new Error('WebSocket not available'));
            }
          } else {
            reject(new Error('WebSocket not connected'));
          }
        } catch (error) {
          reject(error);
        }
      });
    });
    
    // Process all subscription changes
    Promise.all(promises)
      .then(() => {
        toast({
          title: t('notifications.settings_saved'),
          description: t('notifications.settings_saved_description'),
          duration: 3000,
        });
        setHasChanges(false);
      })
      .catch(error => {
        console.error('Error saving notification settings:', error);
        toast({
          title: t('notifications.settings_error'),
          description: t('notifications.settings_error_description'),
          variant: 'destructive',
          duration: 5000,
        });
      })
      .finally(() => {
        setSaveInProgress(false);
      });
  };
  
  // Request browser notification permission
  const handleRequestPermission = async () => {
    const granted = await requestNotificationPermission();
    
    if (granted) {
      toast({
        title: t('notifications.permission_granted'),
        description: t('notifications.permission_granted_description'),
        duration: 3000,
      });
    } else {
      toast({
        title: t('notifications.permission_denied'),
        description: t('notifications.permission_denied_description'),
        variant: 'destructive',
        duration: 5000,
      });
    }
  };
  
  return (
    <>
      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogTrigger asChild>
          <Button variant="outline" className="flex items-center gap-2">
            <Bell className="h-4 w-4" />
            {t('notifications.manage_subscriptions')}
          </Button>
        </DialogTrigger>
        
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>{t('notifications.subscription_settings')}</DialogTitle>
            <DialogDescription>
              {t('notifications.subscription_description')}
            </DialogDescription>
          </DialogHeader>
          
          {/* Connection status */}
          {!connected && (
            <div className="bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800 rounded-md p-3 mb-4">
              <div className="flex items-center gap-2">
                <AlertCircle className="h-5 w-5 text-amber-500" />
                <p className="text-sm text-amber-800 dark:text-amber-300">
                  {t('notifications.connection_required')}
                </p>
              </div>
            </div>
          )}
          
          {/* Browser notification permission */}
          {!hasNotificationPermission && (
            <Card className="mb-4 border-dashed">
              <CardHeader className="pb-2">
                <CardTitle className="text-base">{t('notifications.browser_notifications')}</CardTitle>
                <CardDescription>{t('notifications.browser_notifications_description')}</CardDescription>
              </CardHeader>
              <CardFooter>
                <Button size="sm" onClick={handleRequestPermission}>
                  {t('notifications.enable_browser_notifications')}
                </Button>
              </CardFooter>
            </Card>
          )}
          
          {/* Notification type settings */}
          <div className="space-y-4 max-h-[400px] overflow-y-auto pr-1">
            {settings.map((setting) => (
              <div 
                key={setting.type} 
                className="flex items-start space-x-4 p-3 border rounded-lg hover:bg-muted/50 transition-colors"
              >
                <div className="flex-shrink-0 mt-0.5">
                  {setting.icon}
                </div>
                
                <div className="flex-1 space-y-1">
                  <h4 className="font-medium text-sm leading-none">{setting.label}</h4>
                  <p className="text-xs text-muted-foreground">{setting.description}</p>
                </div>
                
                <Switch
                  id={`notification-${setting.type}`}
                  checked={setting.subscribed}
                  onCheckedChange={() => toggleSubscription(setting.type)}
                  aria-label={`Toggle ${setting.label} notifications`}
                  disabled={saveInProgress || !connected}
                />
              </div>
            ))}
          </div>
          
          <DialogFooter>
            <Button 
              variant="outline" 
              onClick={() => setIsOpen(false)}
              disabled={saveInProgress}
            >
              {t('common.cancel')}
            </Button>
            <Button 
              onClick={saveChanges} 
              disabled={!hasChanges || !connected || saveInProgress}
            >
              {saveInProgress ? (
                <span className="flex items-center gap-2">
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                  {t('common.saving')}
                </span>
              ) : (
                <span className="flex items-center gap-2">
                  <Check className="h-4 w-4" />
                  {t('common.save_changes')}
                </span>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}

export default NotificationSubscriptionManager;