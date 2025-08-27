import React from 'react';
import { UserMenu } from '../components/Auth/UserMenu';
import { Card } from '../components/Shared/Card/Card';
import { Button } from '../components/Shared/Button/Button';
import { useAppSettings } from '../contexts/AppStateContext';
import { useAuth } from '../hooks/useAuth';
import { Settings, User, Moon, Sun, Monitor } from 'lucide-react';

const ProfilePage: React.FC = () => {
  const { settings, theme, language, updateSettings, setTheme, setLanguage } = useAppSettings();
  const { user, isLoading } = useAuth();

  const handleThemeChange = (newTheme: 'light' | 'dark' | 'system') => {
    setTheme(newTheme);
  };

  const handleLanguageChange = (newLanguage: string) => {
    setLanguage(newLanguage);
  };

  const handleSettingsUpdate = (newSettings: Partial<typeof settings>) => {
    updateSettings(newSettings);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-2 border-indigo-600 border-t-transparent"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="container mx-auto px-4 py-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Profile & Settings
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            Manage your account and customize your learning experience.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Profile Info */}
          <Card className="p-6">
            <div className="flex items-center space-x-4 mb-6">
              <div className="w-16 h-16 bg-indigo-100 dark:bg-indigo-900 rounded-full flex items-center justify-center">
                <User className="w-8 h-8 text-indigo-600 dark:text-indigo-400" />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                  {user?.email || 'User'}
                </h2>
                <p className="text-gray-600 dark:text-gray-300">
                  VocabLens Learner
                </p>
              </div>
            </div>
            
            <UserMenu />
          </Card>

          {/* Appearance Settings */}
          <Card className="p-6">
            <div className="flex items-center space-x-2 mb-4">
              <Settings className="w-5 h-5 text-gray-600 dark:text-gray-400" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Appearance
              </h3>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Theme
                </label>
                <div className="grid grid-cols-3 gap-2">
                  <Button
                    variant={theme === 'light' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => handleThemeChange('light')}
                    className="flex items-center justify-center"
                  >
                    <Sun className="w-4 h-4" />
                  </Button>
                  <Button
                    variant={theme === 'dark' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => handleThemeChange('dark')}
                    className="flex items-center justify-center"
                  >
                    <Moon className="w-4 h-4" />
                  </Button>
                  <Button
                    variant={theme === 'system' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => handleThemeChange('system')}
                    className="flex items-center justify-center"
                  >
                    <Monitor className="w-4 h-4" />
                  </Button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Language
                </label>
                <select
                  value={language}
                  onChange={(e) => handleLanguageChange(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                >
                  <option value="en">English</option>
                  <option value="es">Español</option>
                  <option value="fr">Français</option>
                  <option value="de">Deutsch</option>
                  <option value="it">Italiano</option>
                </select>
              </div>
            </div>
          </Card>

          {/* Learning Settings */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Learning Preferences
            </h3>

            <div className="space-y-4">
              <div>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={settings.autoGenerate}
                    onChange={(e) => handleSettingsUpdate({ autoGenerate: e.target.checked })}
                    className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700"
                  />
                  <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                    Auto-generate descriptions when selecting images
                  </span>
                </label>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Default Vocabulary Level
                </label>
                <select
                  value={settings.defaultVocabularyLevel}
                  onChange={(e) => handleSettingsUpdate({ 
                    defaultVocabularyLevel: parseInt(e.target.value) as 1 | 2 | 3 | 4 | 5 
                  })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                >
                  <option value={1}>Beginner (1)</option>
                  <option value={2}>Elementary (2)</option>
                  <option value={3}>Intermediate (3)</option>
                  <option value={4}>Advanced (4)</option>
                  <option value={5}>Expert (5)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Images per search
                </label>
                <select
                  value={settings.maxImagesPerSearch}
                  onChange={(e) => handleSettingsUpdate({ 
                    maxImagesPerSearch: parseInt(e.target.value) 
                  })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                >
                  <option value={10}>10 images</option>
                  <option value={20}>20 images</option>
                  <option value={30}>30 images</option>
                </select>
              </div>
            </div>
          </Card>
        </div>

        {/* Additional Settings Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
          {/* API Configuration */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              API Configuration
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              Configure your API keys for enhanced functionality.
            </p>
            <div className="space-y-3">
              <Button variant="outline" size="sm" className="w-full">
                Configure Unsplash API
              </Button>
              <Button variant="outline" size="sm" className="w-full">
                Configure OpenAI API
              </Button>
            </div>
          </Card>

          {/* Data Management */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Data Management
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              Export your vocabulary data or manage your account.
            </p>
            <div className="space-y-3">
              <Button variant="outline" size="sm" className="w-full">
                Export Vocabulary
              </Button>
              <Button variant="outline" size="sm" className="w-full text-red-600 border-red-300 hover:bg-red-50">
                Delete Account
              </Button>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;