import React, { useState } from 'react';
import {
  BookOpen,
  BarChart3,
  Users,
  Settings,
  Plus,
  Zap,
  Download,
  Star,
  Brain
} from 'lucide-react';
import { VocabularyList } from './VocabularyList';
import { VocabularyStats } from './VocabularyStats';
import { VocabularyAnalyticsDashboard } from './VocabularyAnalytics';
import { VocabularyMarketplaceComponent } from './VocabularyMarketplace';
import { AddVocabulary } from './AddVocabulary';
import { ExportDialog } from './ExportDialog';
import { useVocabulary } from '../../hooks/useVocabulary';
import { Card } from '../Shared/Card/Card';
import { Button } from '../Shared/Button/Button';
import { Modal } from '../Shared/Modal/Modal';

interface VocabularyManagerProps {
  className?: string;
  defaultTab?: 'vocabulary' | 'review' | 'analytics' | 'marketplace';
}

export function VocabularyManager({ 
  className = '',
  defaultTab = 'vocabulary'
}: VocabularyManagerProps) {
  const { stats, getDueForReview, isLoading } = useVocabulary();
  
  // Mock vocabulary review functionality
  const dueItems = getDueForReview();
  const hasReviews = dueItems.length > 0;
  const currentSession = null;
  const startSession = () => console.log('Review session started');
  const resetSession = () => console.log('Review session reset');
  
  const [activeTab, setActiveTab] = useState(defaultTab);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showExportDialog, setShowExportDialog] = useState(false);

  const tabs = [
    {
      id: 'vocabulary',
      label: 'My Vocabulary',
      icon: <BookOpen className="w-5 h-5" />,
      badge: stats?.totalWords
    },
    {
      id: 'review',
      label: 'Review',
      icon: <Zap className="w-5 h-5" />,
      badge: dueItems.length,
      urgent: dueItems.length > 0
    },
    {
      id: 'analytics',
      label: 'Analytics',
      icon: <BarChart3 className="w-5 h-5" />
    },
    {
      id: 'marketplace',
      label: 'Marketplace',
      icon: <Users className="w-5 h-5" />
    }
  ];

  if (isLoading) {
    return (
      <div className={`vocabulary-manager ${className}`}>
        <div className="animate-pulse space-y-6">
          <div className="h-16 bg-gray-200 rounded"></div>
          <div className="h-96 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className={`vocabulary-manager ${className}`}>
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              Vocabulary Manager
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Master your vocabulary with intelligent spaced repetition and analytics
            </p>
          </div>
          
          <div className="flex items-center gap-3">
            {hasReviews && (
              <Button
                variant="primary"
                onClick={startSession}
                className="bg-orange-500 hover:bg-orange-600"
              >
                <Zap className="w-4 h-4 mr-2" />
                Start Review ({dueItems.length})
              </Button>
            )}
            
            <Button
              variant="outline"
              onClick={() => setShowExportDialog(true)}
            >
              <Download className="w-4 h-4 mr-2" />
              Export
            </Button>
            
            <Button
              variant="primary"
              onClick={() => setShowAddModal(true)}
            >
              <Plus className="w-4 h-4 mr-2" />
              Add Word
            </Button>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Words</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {stats?.totalWords || 0}
                </p>
              </div>
              <BookOpen className="w-8 h-8 text-blue-500" />
            </div>
          </Card>
          
          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Due for Review</p>
                <p className="text-2xl font-bold text-orange-500">
                  {dueItems.length}
                </p>
              </div>
              <Zap className="w-8 h-8 text-orange-500" />
            </div>
          </Card>
          
          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Mastered</p>
                <p className="text-2xl font-bold text-green-500">
                  {stats?.masteredWords || 0}
                </p>
              </div>
              <Star className="w-8 h-8 text-green-500" />
            </div>
          </Card>
          
          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Accuracy</p>
                <p className="text-2xl font-bold text-purple-500">
                  {Math.round(stats?.accuracy || 0)}%
                </p>
              </div>
              <Brain className="w-8 h-8 text-purple-500" />
            </div>
          </Card>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 dark:border-gray-700 mb-8">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`group inline-flex items-center py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
              }`}
            >
              {tab.icon}
              <span className="ml-2">{tab.label}</span>
              {tab.badge !== undefined && tab.badge > 0 && (
                <span className={`ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  tab.urgent
                    ? 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300'
                    : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
                }`}>
                  {tab.badge}
                </span>
              )}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {activeTab === 'vocabulary' && (
          <div className="space-y-6">
            <VocabularyStats showDetailedCharts={false} />
            <VocabularyList 
              showAddButton={false}
              className="mt-6"
            />
          </div>
        )}
        
        {activeTab === 'review' && (
          <div className="space-y-6">
            {!hasReviews ? (
              <Card className="p-12 text-center">
                <Zap className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  All Caught Up!
                </h3>
                <p className="text-gray-600 dark:text-gray-400 mb-6">
                  You have no vocabulary words due for review right now.
                </p>
                <div className="flex justify-center gap-4">
                  <Button
                    variant="primary"
                    onClick={() => setShowAddModal(true)}
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Add New Words
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => setActiveTab('marketplace')}
                  >
                    <Users className="w-4 h-4 mr-2" />
                    Browse Marketplace
                  </Button>
                </div>
              </Card>
            ) : (
              <div>
                <Card className="p-6 mb-6">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                        Ready for Review
                      </h3>
                      <p className="text-gray-600 dark:text-gray-400">
                        {dueItems.length} words are waiting for review
                      </p>
                    </div>
                    
                    <Button
                      variant="primary"
                      onClick={startSession}
                      className="bg-orange-500 hover:bg-orange-600"
                    >
                      <Zap className="w-4 h-4 mr-2" />
                      Start Review Session
                    </Button>
                  </div>
                  
                  {/* Preview of due items */}
                  <div className="space-y-2">
                    {dueItems.slice(0, 5).map((item) => (
                      <div key={item.id} className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                        <div>
                          <span className="font-medium text-gray-900 dark:text-white">
                            {item.word}
                          </span>
                          <span className="text-gray-500 dark:text-gray-400 ml-2">
                            → {item.translation}
                          </span>
                        </div>
                        <span className="text-xs text-gray-400">
                          {item.nextReviewAt && new Date(item.nextReviewAt) < new Date() 
                            ? 'Overdue' 
                            : 'Due now'
                          }
                        </span>
                      </div>
                    ))}
                    
                    {dueItems.length > 5 && (
                      <p className="text-sm text-gray-500 dark:text-gray-400 text-center pt-2">
                        ... and {dueItems.length - 5} more
                      </p>
                    )}
                  </div>
                </Card>
              </div>
            )}
          </div>
        )}
        
        {activeTab === 'analytics' && (
          <VocabularyAnalyticsDashboard />
        )}
        
        {activeTab === 'marketplace' && (
          <VocabularyMarketplaceComponent />
        )}
      </div>

      {/* Modals */}
      <Modal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        title="Add New Vocabulary"
        size="lg"
      >
        <AddVocabulary onClose={() => setShowAddModal(false)} />
      </Modal>

      <Modal
        isOpen={showExportDialog}
        onClose={() => setShowExportDialog(false)}
        title="Export Vocabulary"
        size="lg"
      >
        <ExportDialog onClose={() => setShowExportDialog(false)} />
      </Modal>
    </div>
  );
}