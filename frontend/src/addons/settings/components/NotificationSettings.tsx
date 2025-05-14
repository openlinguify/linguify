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
      'success': '/sounds/notification-success.mp3',
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
    <div className="space-y-6">
      {/* Permission alert */}
      {!hasNotificationPermission && (
        <NotificationPermission variant="alert" />
      )}
      
      {/* Main notification toggles */}
      <Card>
        <CardHeader>
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
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="email_notifications" className="flex items-center gap-2">
                <MessageCircle className="h-4 w-4" />
                {t('settings.notifications.email')}
              </Label>
              <p className="text-sm text-muted-foreground">
                {t('settings.notifications.email_description')}
              </p>
            </div>
            <Switch
              id="email_notifications"
              checked={localSettings.email_notifications}
              onCheckedChange={(checked) => handleToggleChange('email_notifications', checked)}
            />
          </div>
          
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="push_notifications" className="flex items-center gap-2">
                <Bell className="h-4 w-4" />
                {t('settings.notifications.push')}
              </Label>
              <p className="text-sm text-muted-foreground">
                {t('settings.notifications.push_description')}
              </p>
            </div>
            <Switch
              id="push_notifications"
              checked={localSettings.push_notifications}
              onCheckedChange={(checked) => handleToggleChange('push_notifications', checked)}
              disabled={!hasNotificationPermission}
            />
          </div>
        </CardContent>
      </Card>
      
      {/* Notification types */}
      <Card>
        <CardHeader>
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
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="lesson_notifications" className="flex items-center gap-2">
                <BookOpen className="h-4 w-4" />
                {t('settings.notifications.lessons')}
              </Label>
              <p className="text-sm text-muted-foreground">
                {t('settings.notifications.lessons_description')}
              </p>
            </div>
            <Switch
              id="lesson_notifications"
              checked={localSettings.lesson_notifications}
              onCheckedChange={(checked) => handleToggleChange('lesson_notifications', checked)}
            />
          </div>
          
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="flashcard_notifications" className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4" />
                {t('settings.notifications.flashcards')}
              </Label>
              <p className="text-sm text-muted-foreground">
                {t('settings.notifications.flashcards_description')}
              </p>
            </div>
            <Switch
              id="flashcard_notifications"
              checked={localSettings.flashcard_notifications}
              onCheckedChange={(checked) => handleToggleChange('flashcard_notifications', checked)}
            />
          </div>
          
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="achievement_notifications" className="flex items-center gap-2">
                <Trophy className="h-4 w-4" />
                {t('settings.notifications.achievements')}
              </Label>
              <p className="text-sm text-muted-foreground">
                {t('settings.notifications.achievements_description')}
              </p>
            </div>
            <Switch
              id="achievement_notifications"
              checked={localSettings.achievement_notifications}
              onCheckedChange={(checked) => handleToggleChange('achievement_notifications', checked)}
            />
          </div>
          
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="system_notifications" className="flex items-center gap-2">
                <AlertTriangle className="h-4 w-4" />
                {t('settings.notifications.system')}
              </Label>
              <p className="text-sm text-muted-foreground">
                {t('settings.notifications.system_description')}
              </p>
            </div>
            <Switch
              id="system_notifications"
              checked={localSettings.system_notifications}
              onCheckedChange={(checked) => handleToggleChange('system_notifications', checked)}
            />
          </div>
        </CardContent>
      </Card>
      
      {/* Reminder settings */}
      <Card>
        <CardHeader>
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
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="weekday_reminders" className="flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                {t('settings.notifications.weekdays')}
              </Label>
              <p className="text-sm text-muted-foreground">
                {t('settings.notifications.weekdays_description')}
              </p>
            </div>
            <Switch
              id="weekday_reminders"
              checked={localSettings.weekday_reminders}
              onCheckedChange={(checked) => handleToggleChange('weekday_reminders', checked)}
            />
          </div>
          
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="weekend_reminders" className="flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                {t('settings.notifications.weekends')}
              </Label>
              <p className="text-sm text-muted-foreground">
                {t('settings.notifications.weekends_description')}
              </p>
            </div>
            <Switch
              id="weekend_reminders"
              checked={localSettings.weekend_reminders}
              onCheckedChange={(checked) => handleToggleChange('weekend_reminders', checked)}
            />
          </div>
          
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
        <CardHeader>
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