/**
 * Settings Page Component
 * Main settings page with different configuration sections
 */

import React, { useState, useEffect } from 'react';
import { 
  Settings, 
  Key, 
  Palette, 
  Bell, 
  Shield, 
  Download,
  Trash2,
  AlertTriangle
} from 'lucide-react';
import { ApiSettings } from '../components/Settings/ApiSettings';
import { apiConfigService } from '../services/apiConfigService';

interface SettingTab {
  id: string;
  label: string;
  icon: React.ComponentType<any>;
  component: React.ComponentType;
}

const GeneralSettings: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
          General Preferences
        </h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Language
              </label>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Choose your preferred language for the interface
              </p>
            </div>
            <select className="mt-1 block w-32 pl-3 pr-10 py-2 text-base border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md dark:bg-gray-700 dark:text-gray-300">
              <option>English</option>
              <option>Spanish</option>
              <option>French</option>
              <option>German</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  );
};

const AppearanceSettings: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
          Appearance
        </h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Theme
              </label>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Choose your preferred theme
              </p>
            </div>
            <select className="mt-1 block w-32 pl-3 pr-10 py-2 text-base border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md dark:bg-gray-700 dark:text-gray-300">
              <option>Light</option>
              <option>Dark</option>
              <option>Auto</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  );
};

const NotificationSettings: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
          Notifications
        </h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Learning Reminders
              </label>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Get notified to review your vocabulary
              </p>
            </div>
            <input
              type="checkbox"
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 dark:border-gray-600 rounded dark:bg-gray-700"
              defaultChecked
            />
          </div>
        </div>
      </div>
    </div>
  );
};

const DataSettings: React.FC = () => {
  const [isClearing, setIsClearing] = useState(false);

  const handleClearData = async () => {
    if (!confirm('Are you sure you want to clear all API configuration data? This action cannot be undone.')) {
      return;
    }

    setIsClearing(true);
    try {
      await apiConfigService.clearConfiguration();
      alert('API configuration cleared successfully.');
    } catch (error) {
      alert('Failed to clear API configuration.');
    } finally {
      setIsClearing(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
          Data Management
        </h3>
        <div className="space-y-4">
          <div className="border border-red-200 dark:border-red-800 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <AlertTriangle className="h-5 w-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <h4 className="text-sm font-medium text-red-800 dark:text-red-200">
                  Clear API Configuration
                </h4>
                <p className="text-sm text-red-600 dark:text-red-400 mt-1">
                  This will remove all stored API keys and configuration data from your browser.
                </p>
                <button
                  onClick={handleClearData}
                  disabled={isClearing}
                  className="mt-3 inline-flex items-center px-3 py-2 text-sm bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  {isClearing ? 'Clearing...' : 'Clear All Data'}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export const SettingsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState('api');
  const [needsSetup, setNeedsSetup] = useState(false);

  useEffect(() => {
    checkSetupStatus();
  }, []);

  const checkSetupStatus = async () => {
    try {
      const setupNeeded = await apiConfigService.isSetupNeeded();
      setNeedsSetup(setupNeeded);
    } catch (error) {
      console.error('Failed to check setup status:', error);
    }
  };

  const tabs: SettingTab[] = [
    {
      id: 'api',
      label: 'API Keys',
      icon: Key,
      component: ApiSettings
    },
    {
      id: 'general',
      label: 'General',
      icon: Settings,
      component: GeneralSettings
    },
    {
      id: 'appearance',
      label: 'Appearance',
      icon: Palette,
      component: AppearanceSettings
    },
    {
      id: 'notifications',
      label: 'Notifications',
      icon: Bell,
      component: NotificationSettings
    },
    {
      id: 'data',
      label: 'Data',
      icon: Shield,
      component: DataSettings
    }
  ];

  const ActiveComponent = tabs.find(tab => tab.id === activeTab)?.component || ApiSettings;

  return (
    <div className="max-w-6xl mx-auto px-4 py-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
          Settings
        </h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Manage your VocabLens preferences and configuration
        </p>
      </div>

      {/* Setup Warning */}
      {needsSetup && (
        <div className="mb-6 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="h-5 w-5 text-yellow-600 dark:text-yellow-400" />
            <div>
              <h3 className="text-sm font-medium text-yellow-800 dark:text-yellow-200">
                Setup Required
              </h3>
              <p className="text-sm text-yellow-700 dark:text-yellow-300 mt-1">
                You need to configure your API keys to use VocabLens. Click on "API Keys" to get started.
              </p>
            </div>
          </div>
        </div>
      )}

      <div className="lg:grid lg:grid-cols-12 lg:gap-x-8">
        {/* Sidebar */}
        <aside className="py-6 px-2 sm:px-6 lg:py-0 lg:px-0 lg:col-span-3">
          <nav className="space-y-1">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`group rounded-md px-3 py-2 flex items-center text-sm font-medium w-full text-left transition-colors ${
                    isActive
                      ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300'
                      : 'text-gray-900 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-800'
                  }`}
                  aria-current={isActive ? 'page' : undefined}
                >
                  <Icon
                    className={`flex-shrink-0 -ml-1 mr-3 h-5 w-5 ${
                      isActive
                        ? 'text-blue-600 dark:text-blue-400'
                        : 'text-gray-400 dark:text-gray-500 group-hover:text-gray-500 dark:group-hover:text-gray-400'
                    }`}
                    aria-hidden="true"
                  />
                  <span className="truncate">{tab.label}</span>
                  {tab.id === 'api' && needsSetup && (
                    <span className="ml-auto flex-shrink-0">
                      <div className="h-2 w-2 bg-red-400 rounded-full"></div>
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </aside>

        {/* Main content */}
        <main className="space-y-6 sm:px-6 lg:px-0 lg:col-span-9">
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
            <div className="px-4 py-6 sm:p-6">
              <ActiveComponent />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default SettingsPage;