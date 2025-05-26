'use client';

import React, { useState } from 'react';
import { useTranslation } from '@/core/i18n/useTranslations';
import { 
  Bell, 
  Calendar, 
  Clock, 
  MessageCircle, 
  Settings, 
  AlertTriangle,
  Trophy, 
  CheckCircle,
  BookOpen
} from 'lucide-react';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { Input } from '@/components/ui/input';
import { useUserSettings } from '@/core/context/UserSettingsContext';
import { NotificationPermission } from '@/components/notifications';
import { useNotifications } from '@/core/context/NotificationContext';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle 
} from '@/components/ui/card';

// Helper component for toggles
interface SettingsToggleProps {
  id: string;
  label: string;
  description?: string;
  checked: boolean;
  onCheckedChange: (checked: boolean) => void;
  disabled?: boolean;
  icon?: React.ReactNode;
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

export default function NotificationSettings() {
  const { t } = useTranslation();
  const { settings, updateSetting } = useUserSettings();
  const { hasNotificationPermission } = useNotifications();
  
  // Local state for form
  const [localSettings, setLocalSettings] = useState({
    email_notifications: settings.email_notifications,
    push_notifications: settings.push_notifications,
    weekday_reminders: settings.weekday_reminders,
    weekend_reminders: settings.weekend_reminders,
    reminder_time: settings.reminder_time,
    notification_sound: settings.notification_sound || 'default',
    achievement_notifications: true,
    lesson_notifications: true,
    flashcard_notifications: true,
    system_notifications: true,
    notification_retention_days: 30,
  });
  
  // Handle toggle changes
  const handleToggleChange = (setting: string, value: boolean) => {
    setLocalSettings(prev => ({ ...prev, [setting]: value }));
    
    // Update immediately in context
    if (setting in settings) {
      updateSetting(setting as keyof typeof settings, value);
    }
  };
  
  // Handle time change
  const handleTimeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newTime = e.target.value;
    setLocalSettings(prev => ({ ...prev, reminder_time: newTime }));
    updateSetting('reminder_time', newTime);
  };
  
  // Handle sound selection
  const handleSoundChange = (value: string) => {
    setLocalSettings(prev => ({ ...prev, notification_sound: value }));
    
    // Play sound preview
    const sounds: Record<string, string> = {
      'default': '/sounds/notification-default.mp3',
      'chime': '/sounds/notification-chime.mp3',
      'bell': '/sounds/notification-bell.mp3',
      'success': '/sounds/success.mp3',
    };
    
    if (value in sounds) {
      try {
        const audio = new Audio(sounds[value]);
        audio.play();
      } catch (error) {
        console.error('Error playing notification sound:', error);
      }
    }
    
    // Save setting
    updateSetting('notification_sound', value);
  };
  
  // Handle retention days change
  const handleRetentionChange = (value: number[]) => {
    const days = value[0];
    setLocalSettings(prev => ({ ...prev, notification_retention_days: days }));
    updateSetting('notification_retention_days', days);
  };
  
  // Render settings
  return (
    <div className="h-full w-full bg-gray-50 dark:bg-gray-900 overflow-hidden p-0 m-0 space-y-6">
      {/* Permission alert */}
      {!hasNotificationPermission && (
        <NotificationPermission variant="alert" />
      )}
      
      {/* Main notification toggles */}
      <Card>
        <CardHeader className="pb-3 bg-muted/30">
          <CardTitle>
            <div className="flex items-center gap-2">
              <Bell className="h-5 w-5" />
              {t('settings.notifications.main_title')}
            </div>
          </CardTitle>
          <CardDescription>
            {t('settings.notifications.main_description')}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <SettingsToggle
            id="email_notifications"
            label={t('settings.notifications.email')}
            description={t('settings.notifications.email_description')}
            checked={localSettings.email_notifications}
            onCheckedChange={(checked) => handleToggleChange('email_notifications', checked)}
            icon={<MessageCircle className="h-4 w-4" />}
          />
          
          <SettingsToggle
            id="push_notifications"
            label={t('settings.notifications.push')}
            description={t('settings.notifications.push_description')}
            checked={localSettings.push_notifications}
            onCheckedChange={(checked) => handleToggleChange('push_notifications', checked)}
            disabled={!hasNotificationPermission}
            icon={<Bell className="h-4 w-4" />}
          />
        </CardContent>
      </Card>
      
      {/* Notification types */}
      <Card>
        <CardHeader className="pb-3 bg-muted/30">
          <CardTitle>
            <div className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              {t('settings.notifications.types_title')}
            </div>
          </CardTitle>
          <CardDescription>
            {t('settings.notifications.types_description')}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <SettingsToggle
            id="lesson_notifications"
            label={t('settings.notifications.lessons')}
            description={t('settings.notifications.lessons_description')}
            checked={localSettings.lesson_notifications}
            onCheckedChange={(checked) => handleToggleChange('lesson_notifications', checked)}
            icon={<BookOpen className="h-4 w-4" />}
          />
          
          <SettingsToggle
            id="flashcard_notifications"
            label={t('settings.notifications.flashcards')}
            description={t('settings.notifications.flashcards_description')}
            checked={localSettings.flashcard_notifications}
            onCheckedChange={(checked) => handleToggleChange('flashcard_notifications', checked)}
            icon={<CheckCircle className="h-4 w-4" />}
          />
          
          <SettingsToggle
            id="achievement_notifications"
            label={t('settings.notifications.achievements')}
            description={t('settings.notifications.achievements_description')}
            checked={localSettings.achievement_notifications}
            onCheckedChange={(checked) => handleToggleChange('achievement_notifications', checked)}
            icon={<Trophy className="h-4 w-4" />}
          />
          
          <SettingsToggle
            id="system_notifications"
            label={t('settings.notifications.system')}
            description={t('settings.notifications.system_description')}
            checked={localSettings.system_notifications}
            onCheckedChange={(checked) => handleToggleChange('system_notifications', checked)}
            icon={<AlertTriangle className="h-4 w-4" />}
          />
        </CardContent>
      </Card>
      
      {/* Reminder settings */}
      <Card>
        <CardHeader className="pb-3 bg-muted/30">
          <CardTitle>
            <div className="flex items-center gap-2">
              <Clock className="h-5 w-5" />
              {t('settings.notifications.reminders_title')}
            </div>
          </CardTitle>
          <CardDescription>
            {t('settings.notifications.reminders_description')}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <SettingsToggle
            id="weekday_reminders"
            label={t('settings.notifications.weekdays')}
            description={t('settings.notifications.weekdays_description')}
            checked={localSettings.weekday_reminders}
            onCheckedChange={(checked) => handleToggleChange('weekday_reminders', checked)}
            icon={<Calendar className="h-4 w-4" />}
          />
          
          <SettingsToggle
            id="weekend_reminders"
            label={t('settings.notifications.weekends')}
            description={t('settings.notifications.weekends_description')}
            checked={localSettings.weekend_reminders}
            onCheckedChange={(checked) => handleToggleChange('weekend_reminders', checked)}
            icon={<Calendar className="h-4 w-4" />}
          />
          
          <div className="space-y-2">
            <Label htmlFor="reminder_time" className="flex items-center gap-2">
              <Clock className="h-4 w-4" />
              {t('settings.notifications.reminder_time')}
            </Label>
            <Input
              id="reminder_time"
              type="time"
              value={localSettings.reminder_time}
              onChange={handleTimeChange}
              className="w-[200px]"
            />
            <p className="text-sm text-muted-foreground">
              {t('settings.notifications.reminder_time_description')}
            </p>
          </div>
        </CardContent>
      </Card>
      
      {/* Advanced settings */}
      <Card>
        <CardHeader className="pb-3 bg-muted/30">
          <CardTitle>
            <div className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              {t('settings.notifications.advanced_title')}
            </div>
          </CardTitle>
          <CardDescription>
            {t('settings.notifications.advanced_description')}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="notification_sound" className="flex items-center gap-2">
              {t('settings.notifications.sound')}
            </Label>
            <Select
              value={localSettings.notification_sound}
              onValueChange={handleSoundChange}
            >
              <SelectTrigger id="notification_sound" className="w-[240px]">
                <SelectValue placeholder={t('settings.notifications.select_sound')} />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="default">{t('settings.notifications.sound_default')}</SelectItem>
                <SelectItem value="chime">{t('settings.notifications.sound_chime')}</SelectItem>
                <SelectItem value="bell">{t('settings.notifications.sound_bell')}</SelectItem>
                <SelectItem value="success">{t('settings.notifications.sound_success')}</SelectItem>
                <SelectItem value="none">{t('settings.notifications.sound_none')}</SelectItem>
              </SelectContent>
            </Select>
            <p className="text-sm text-muted-foreground">
              {t('settings.notifications.sound_description')}
            </p>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="notification_retention" className="flex items-center gap-2">
              {t('settings.notifications.retention')}
            </Label>
            <div className="flex items-center gap-4">
              <Slider
                id="notification_retention"
                defaultValue={[localSettings.notification_retention_days]}
                max={90}
                min={1}
                step={1}
                onValueChange={handleRetentionChange}
                className="w-[240px]"
              />
              <span className="text-sm">
                {localSettings.notification_retention_days} {t('settings.notifications.days')}
              </span>
            </div>
            <p className="text-sm text-muted-foreground">
              {t('settings.notifications.retention_description')}
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}