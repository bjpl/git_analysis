import React, { useState, useEffect } from 'react';
import { AlgorithmPlayground } from './AlgorithmPlayground';
import { DataStructureBuilder } from './DataStructureBuilder';
import { ComplexityCalculator } from './ComplexityCalculator';
import { PatternMatcher } from './PatternMatcher';
import { RealWorldSimulator } from './RealWorldSimulator';
import { CodeConceptBridge } from './CodeConceptBridge';
import { ProgressDashboard } from './ProgressDashboard';
import { CollaborationSpace } from './CollaborationSpace';
import { NavigationSidebar } from './NavigationSidebar';
import { UserProgress, LearningStats } from '../types/learning-types';

interface InteractiveLearningAppProps {
  userId: string;
  userName: string;
}

export const InteractiveLearningApp: React.FC<InteractiveLearningAppProps> = ({
  userId,
  userName
}) => {
  const [activeComponent, setActiveComponent] = useState<string>('playground');
  const [userProgress, setUserProgress] = useState<UserProgress | null>(null);
  const [learningStats, setLearningStats] = useState<LearningStats | null>(null);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  // Load user data on mount
  useEffect(() => {
    loadUserData();
  }, [userId]);

  const loadUserData = async () => {
    try {
      // Load user progress and stats
      const progress = await fetchUserProgress(userId);
      const stats = await fetchLearningStats(userId);
      
      setUserProgress(progress);
      setLearningStats(stats);
    } catch (error) {
      console.error('Failed to load user data:', error);
    }
  };

  const handleComponentChange = (component: string) => {
    setActiveComponent(component);
    
    // Track component usage
    trackComponentUsage(component, userId);
  };

  const handleProgressUpdate = (component: string, progress: any) => {
    // Update user progress based on component activity
    setUserProgress(prev => prev ? {
      ...prev,
      stats: {
        ...prev.stats,
        // Update relevant stats based on component and progress
      }
    } : null);
  };

  const renderActiveComponent = () => {
    const commonProps = {
      userId,
      userName,
      onProgressUpdate: (progress: any) => handleProgressUpdate(activeComponent, progress)
    };

    switch (activeComponent) {
      case 'playground':
        return (
          <AlgorithmPlayground
            algorithm="bubbleSort"
            initialData={[64, 34, 25, 12, 22, 11, 90]}
            onStepComplete={(step) => console.log('Step completed:', step)}
          />
        );

      case 'builder':
        return (
          <DataStructureBuilder
            type="tree"
            onStructureChange={(structure) => console.log('Structure changed:', structure)}
            onValidate={(structure) => {
              // Basic validation logic
              return structure.length > 0;
            }}
          />
        );

      case 'complexity':
        return (
          <ComplexityCalculator
            algorithm="bubbleSort"
            onAnalysisChange={(analysis) => console.log('Analysis updated:', analysis)}
          />
        );

      case 'patterns':
        return (
          <PatternMatcher
            onScoreUpdate={(score) => handleProgressUpdate('patterns', { score })}
            onPatternLearned={(pattern) => handleProgressUpdate('patterns', { pattern })}
          />
        );

      case 'simulator':
        return (
          <RealWorldSimulator
            onSimulationComplete={(result) => handleProgressUpdate('simulator', { result })}
            onAlgorithmApplied={(algorithm, scenario) => 
              handleProgressUpdate('simulator', { algorithm, scenario })
            }
          />
        );

      case 'bridge':
        return (
          <CodeConceptBridge
            initialCode=""
            language="javascript"
            onMappingChange={(mapping) => console.log('Mapping changed:', mapping)}
            onLearningProgress={(progress) => handleProgressUpdate('bridge', { progress })}
          />
        );

      case 'dashboard':
        return (
          <ProgressDashboard
            userId={userId}
            onAchievementUnlock={(achievement) => 
              handleProgressUpdate('dashboard', { achievement })
            }
            onGoalSet={(goal) => handleProgressUpdate('dashboard', { goal })}
          />
        );

      case 'collaboration':
        return (
          <CollaborationSpace
            userId={userId}
            userName={userName}
            onSessionCreate={(session) => handleProgressUpdate('collaboration', { session })}
            onSessionJoin={(sessionId) => handleProgressUpdate('collaboration', { sessionId })}
            onSessionLeave={() => handleProgressUpdate('collaboration', { action: 'leave' })}
          />
        );

      default:
        return <div>Component not found</div>;
    }
  };

  return (
    <div className={`interactive-learning-app ${theme}`}>
      <NavigationSidebar
        activeComponent={activeComponent}
        onComponentChange={handleComponentChange}
        userProgress={userProgress}
        collapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
      />

      <div className={`main-content ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
        <div className="app-header">
          <div className="header-left">
            <h1>Interactive Algorithm Learning</h1>
            <div className="breadcrumb">
              <span>Learning Hub</span>
              <span className="separator">›</span>
              <span className="current">{getComponentTitle(activeComponent)}</span>
            </div>
          </div>
          
          <div className="header-right">
            <button
              className="theme-toggle"
              onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
              title="Toggle theme"
            >
              {theme === 'light' ? '🌙' : '☀️'}
            </button>
            
            <div className="user-info">
              <div className="user-avatar">
                <img src={`/avatars/${userId}.png`} alt={userName} />
              </div>
              <span className="user-name">{userName}</span>
            </div>
          </div>
        </div>

        <div className="component-container">
          {renderActiveComponent()}
        </div>
      </div>

      {/* Global notifications and modals would go here */}
      <div className="notifications-container">
        {/* Notification system */}
      </div>
    </div>
  );
};

// Helper functions
function getComponentTitle(component: string): string {
  const titles: Record<string, string> = {
    playground: 'Algorithm Playground',
    builder: 'Data Structure Builder',
    complexity: 'Complexity Calculator',
    patterns: 'Pattern Matcher',
    simulator: 'Real-World Simulator',
    bridge: 'Code-to-Concept Bridge',
    dashboard: 'Progress Dashboard',
    collaboration: 'Collaboration Space'
  };
  
  return titles[component] || 'Unknown Component';
}

async function fetchUserProgress(userId: string): Promise<UserProgress> {
  // Mock implementation - would fetch from API
  return {
    userId,
    completedModules: [],
    achievements: [],
    stats: {
      algorithmsCompleted: 0,
      patternsRecognized: 0,
      collaborationPoints: 0,
      streakDays: 0
    }
  };
}

async function fetchLearningStats(userId: string): Promise<LearningStats> {
  // Mock implementation
  return {
    totalXP: 0,
    averageQuizScore: 0,
    weeklyProgress: [],
    skillProgress: {}
  };
}

function trackComponentUsage(component: string, userId: string) {
  // Track which components users are using most
  console.log(`User ${userId} accessed ${component}`);
  
  // In a real app, this would send analytics data
  // analytics.track('component_accessed', { component, userId });
}