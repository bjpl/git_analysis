import React, { useState, useEffect, useMemo } from 'react';
import { Achievement, UserProgress, LearningStats } from '../types/learning-types';
import { AchievementCard } from './AchievementCard';
import { ProgressChart } from './ProgressChart';
import { SkillRadar } from './SkillRadar';
import { ActivityFeed } from './ActivityFeed';
import { LeaderboardPanel } from './LeaderboardPanel';

interface ProgressDashboardProps {
  userId: string;
  onAchievementUnlock?: (achievement: Achievement) => void;
  onGoalSet?: (goal: LearningGoal) => void;
}

export const ProgressDashboard: React.FC<ProgressDashboardProps> = ({
  userId,
  onAchievementUnlock,
  onGoalSet
}) => {
  const [userProgress, setUserProgress] = useState<UserProgress | null>(null);
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [learningStats, setLearningStats] = useState<LearningStats | null>(null);
  const [selectedTimeRange, setSelectedTimeRange] = useState<'week' | 'month' | 'year'>('month');
  const [activeTab, setActiveTab] = useState<'overview' | 'achievements' | 'skills' | 'activity' | 'social'>('overview');
  const [goals, setGoals] = useState<LearningGoal[]>([]);
  const [streak, setStreak] = useState(0);

  // Load user progress data
  useEffect(() => {
    loadUserProgress(userId).then(progress => {
      setUserProgress(progress);
      setAchievements(progress.achievements);
      setStreak(progress.stats.streakDays);
    });
    
    loadLearningStats(userId, selectedTimeRange).then(setLearningStats);
    loadUserGoals(userId).then(setGoals);
  }, [userId, selectedTimeRange]);

  // Calculate derived metrics
  const progressMetrics = useMemo(() => {
    if (!userProgress || !learningStats) return null;

    return {
      totalXP: learningStats.totalXP,
      level: calculateLevel(learningStats.totalXP),
      completionRate: (userProgress.completedModules.length / 50) * 100, // Assume 50 total modules
      averageScore: learningStats.averageQuizScore,
      weeklyProgress: learningStats.weeklyProgress,
      skillDistribution: calculateSkillDistribution(userProgress),
      nextLevelXP: calculateNextLevelXP(learningStats.totalXP)
    };
  }, [userProgress, learningStats]);

  // Handle achievement unlock
  const handleAchievementUnlock = (achievement: Achievement) => {
    setAchievements(prev => prev.map(a => 
      a.id === achievement.id ? { ...a, unlocked: true, unlockedAt: new Date() } : a
    ));
    onAchievementUnlock?.(achievement);
  };

  // Handle goal creation
  const handleGoalCreate = (goal: LearningGoal) => {
    setGoals(prev => [...prev, goal]);
    onGoalSet?.(goal);
  };

  const handleTimeRangeChange = (range: 'week' | 'month' | 'year') => {
    setSelectedTimeRange(range);
  };

  if (!userProgress || !learningStats || !progressMetrics) {
    return <div className="loading">Loading your progress...</div>;
  }

  return (
    <div className="progress-dashboard">
      <div className="dashboard-header">
        <div className="user-overview">
          <div className="user-avatar">
            <img src={`/avatars/${userId}.png`} alt="User Avatar" />
          </div>
          <div className="user-info">
            <h2>Welcome back!</h2>
            <div className="level-info">
              <span className="level">Level {progressMetrics.level}</span>
              <div className="xp-progress">
                <div className="xp-bar">
                  <div 
                    className="xp-fill" 
                    style={{ width: `${(progressMetrics.totalXP % 1000) / 10}%` }}
                  />
                </div>
                <span className="xp-text">
                  {progressMetrics.totalXP} / {progressMetrics.nextLevelXP} XP
                </span>
              </div>
            </div>
          </div>
          <div className="streak-counter">
            <div className="streak-flame">🔥</div>
            <div className="streak-info">
              <span className="streak-number">{streak}</span>
              <span className="streak-label">Day Streak</span>
            </div>
          </div>
        </div>

        <div className="quick-stats">
          <div className="stat-card">
            <div className="stat-value">{progressMetrics.completionRate.toFixed(1)}%</div>
            <div className="stat-label">Completion</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{progressMetrics.averageScore}%</div>
            <div className="stat-label">Average Score</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{userProgress.stats.patternsRecognized}</div>
            <div className="stat-label">Patterns Learned</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{userProgress.stats.collaborationPoints}</div>
            <div className="stat-label">Collab Points</div>
          </div>
        </div>
      </div>

      <div className="dashboard-controls">
        <div className="tab-navigation">
          {(['overview', 'achievements', 'skills', 'activity', 'social'] as const).map(tab => (
            <button
              key={tab}
              className={activeTab === tab ? 'active' : ''}
              onClick={() => setActiveTab(tab)}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        <div className="time-range-selector">
          {(['week', 'month', 'year'] as const).map(range => (
            <button
              key={range}
              className={selectedTimeRange === range ? 'active' : ''}
              onClick={() => handleTimeRangeChange(range)}
            >
              {range.charAt(0).toUpperCase() + range.slice(1)}
            </button>
          ))}
        </div>
      </div>

      <div className="dashboard-content">
        {activeTab === 'overview' && (
          <div className="overview-tab">
            <div className="main-chart-section">
              <ProgressChart
                data={progressMetrics.weeklyProgress}
                timeRange={selectedTimeRange}
                metrics={['xp', 'completion', 'accuracy']}
              />
            </div>

            <div className="goals-section">
              <div className="section-header">
                <h3>Learning Goals</h3>
                <button onClick={() => handleGoalCreate(createDefaultGoal())}>
                  + Add Goal
                </button>
              </div>
              <div className="goals-grid">
                {goals.map(goal => (
                  <GoalCard key={goal.id} goal={goal} />
                ))}
              </div>
            </div>

            <div className="recent-achievements">
              <h3>Recent Achievements</h3>
              <div className="achievement-list">
                {achievements
                  .filter(a => a.unlocked)
                  .sort((a, b) => (b.unlockedAt?.getTime() || 0) - (a.unlockedAt?.getTime() || 0))
                  .slice(0, 3)
                  .map(achievement => (
                    <AchievementCard key={achievement.id} achievement={achievement} compact />
                  ))
                }
              </div>
            </div>

            <div className="skill-overview">
              <h3>Skill Distribution</h3>
              <SkillRadar
                data={progressMetrics.skillDistribution}
                skills={['Sorting', 'Searching', 'Graph', 'Dynamic Programming', 'Greedy', 'Data Structures']}
              />
            </div>
          </div>
        )}

        {activeTab === 'achievements' && (
          <div className="achievements-tab">
            <div className="achievement-stats">
              <div className="stat">
                <span className="value">{achievements.filter(a => a.unlocked).length}</span>
                <span className="label">Unlocked</span>
              </div>
              <div className="stat">
                <span className="value">{achievements.length}</span>
                <span className="label">Total</span>
              </div>
              <div className="stat">
                <span className="value">
                  {((achievements.filter(a => a.unlocked).length / achievements.length) * 100).toFixed(1)}%
                </span>
                <span className="label">Completion</span>
              </div>
            </div>

            <div className="achievement-categories">
              {groupAchievementsByCategory(achievements).map(category => (
                <div key={category.name} className="achievement-category">
                  <h3>{category.name}</h3>
                  <div className="achievements-grid">
                    {category.achievements.map(achievement => (
                      <AchievementCard 
                        key={achievement.id} 
                        achievement={achievement}
                        onUnlock={handleAchievementUnlock}
                      />
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'skills' && (
          <div className="skills-tab">
            <div className="skill-breakdown">
              <SkillRadar
                data={progressMetrics.skillDistribution}
                skills={['Sorting', 'Searching', 'Graph', 'Dynamic Programming', 'Greedy', 'Data Structures']}
                detailed
              />
            </div>

            <div className="skill-progress-list">
              {Object.entries(progressMetrics.skillDistribution).map(([skill, progress]) => (
                <div key={skill} className="skill-item">
                  <div className="skill-header">
                    <span className="skill-name">{skill}</span>
                    <span className="skill-level">{Math.floor(progress / 10)} / 10</span>
                  </div>
                  <div className="skill-bar">
                    <div 
                      className="skill-fill" 
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                  <div className="skill-recommendations">
                    {getSkillRecommendations(skill, progress).map((rec, index) => (
                      <span key={index} className="recommendation">{rec}</span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'activity' && (
          <div className="activity-tab">
            <ActivityFeed
              userId={userId}
              timeRange={selectedTimeRange}
              showFilters
            />
          </div>
        )}

        {activeTab === 'social' && (
          <div className="social-tab">
            <div className="social-stats">
              <div className="stat">
                <span className="value">{userProgress.stats.collaborationPoints}</span>
                <span className="label">Collaboration Points</span>
              </div>
              <div className="stat">
                <span className="value">#42</span>
                <span className="label">Global Rank</span>
              </div>
            </div>

            <LeaderboardPanel
              userId={userId}
              timeRange={selectedTimeRange}
              category="overall"
            />

            <div className="friend-activity">
              <h3>Friend Activity</h3>
              <FriendActivityFeed userId={userId} />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Supporting Components
interface GoalCardProps {
  goal: LearningGoal;
}

const GoalCard: React.FC<GoalCardProps> = ({ goal }) => {
  const progressPercentage = (goal.currentProgress / goal.targetValue) * 100;

  return (
    <div className="goal-card">
      <div className="goal-header">
        <h4>{goal.title}</h4>
        <span className="goal-deadline">
          {goal.deadline ? new Date(goal.deadline).toLocaleDateString() : 'No deadline'}
        </span>
      </div>
      
      <div className="goal-progress">
        <div className="progress-bar">
          <div 
            className="progress-fill" 
            style={{ width: `${Math.min(progressPercentage, 100)}%` }}
          />
        </div>
        <div className="progress-text">
          {goal.currentProgress} / {goal.targetValue} {goal.unit}
        </div>
      </div>

      <div className="goal-status">
        <span className={`status-badge ${goal.status}`}>
          {goal.status}
        </span>
      </div>
    </div>
  );
};

interface FriendActivityFeedProps {
  userId: string;
}

const FriendActivityFeed: React.FC<FriendActivityFeedProps> = ({ userId }) => {
  const [activities, setActivities] = useState([]);

  useEffect(() => {
    // Load friend activities
    loadFriendActivities(userId).then(setActivities);
  }, [userId]);

  return (
    <div className="friend-activity-feed">
      {activities.map((activity: any, index) => (
        <div key={index} className="activity-item">
          <div className="friend-avatar">
            <img src={`/avatars/${activity.friendId}.png`} alt="Friend" />
          </div>
          <div className="activity-content">
            <span className="friend-name">{activity.friendName}</span>
            <span className="activity-text">{activity.description}</span>
            <span className="activity-time">{activity.timestamp}</span>
          </div>
        </div>
      ))}
    </div>
  );
};

// Helper functions and types
interface LearningGoal {
  id: string;
  title: string;
  description: string;
  targetValue: number;
  currentProgress: number;
  unit: string;
  deadline?: Date;
  status: 'active' | 'completed' | 'paused';
  category: string;
}

interface LearningStats {
  totalXP: number;
  averageQuizScore: number;
  weeklyProgress: Array<{ date: string; xp: number; completion: number; accuracy: number }>;
  skillProgress: Record<string, number>;
}

async function loadUserProgress(userId: string): Promise<UserProgress> {
  // Mock implementation - would fetch from API
  return {
    userId,
    completedModules: Array.from({length: 23}, (_, i) => `module-${i}`),
    achievements: generateMockAchievements(),
    stats: {
      algorithmsCompleted: 47,
      patternsRecognized: 23,
      collaborationPoints: 1250,
      streakDays: 12
    }
  };
}

async function loadLearningStats(userId: string, timeRange: string): Promise<LearningStats> {
  return {
    totalXP: 8750,
    averageQuizScore: 87,
    weeklyProgress: generateMockProgressData(timeRange),
    skillProgress: {
      sorting: 85,
      searching: 72,
      graph: 63,
      dynamic: 45,
      greedy: 58,
      dataStructures: 79
    }
  };
}

async function loadUserGoals(userId: string): Promise<LearningGoal[]> {
  return [
    {
      id: 'goal-1',
      title: 'Master Sorting Algorithms',
      description: 'Complete all sorting algorithm modules',
      targetValue: 10,
      currentProgress: 7,
      unit: 'algorithms',
      deadline: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
      status: 'active',
      category: 'algorithms'
    },
    {
      id: 'goal-2',
      title: 'Build Daily Habit',
      description: 'Practice algorithms daily',
      targetValue: 30,
      currentProgress: 12,
      unit: 'days',
      status: 'active',
      category: 'habits'
    }
  ];
}

function calculateLevel(xp: number): number {
  return Math.floor(xp / 1000) + 1;
}

function calculateNextLevelXP(xp: number): number {
  const currentLevel = calculateLevel(xp);
  return currentLevel * 1000;
}

function calculateSkillDistribution(progress: UserProgress): Record<string, number> {
  // Mock calculation based on completed modules
  return {
    'Sorting': Math.min(progress.completedModules.length * 4, 100),
    'Searching': Math.min(progress.completedModules.length * 3.5, 100),
    'Graph': Math.min(progress.completedModules.length * 2.8, 100),
    'Dynamic Programming': Math.min(progress.completedModules.length * 2, 100),
    'Greedy': Math.min(progress.completedModules.length * 2.5, 100),
    'Data Structures': Math.min(progress.completedModules.length * 3.8, 100)
  };
}

function generateMockAchievements(): Achievement[] {
  return [
    {
      id: 'first-sort',
      title: 'First Sort',
      description: 'Complete your first sorting algorithm',
      icon: '🔄',
      criteria: { type: 'completion', target: 1, current: 1 },
      unlocked: true,
      unlockedAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000)
    },
    {
      id: 'speed-demon',
      title: 'Speed Demon',
      description: 'Complete 5 algorithms in under 10 minutes each',
      icon: '⚡',
      criteria: { type: 'time', target: 5, current: 3 },
      unlocked: false
    },
    {
      id: 'pattern-master',
      title: 'Pattern Master',
      description: 'Recognize 50 algorithm patterns',
      icon: '🧩',
      criteria: { type: 'completion', target: 50, current: 23 },
      unlocked: false
    }
  ];
}

function generateMockProgressData(timeRange: string) {
  const days = timeRange === 'week' ? 7 : timeRange === 'month' ? 30 : 365;
  return Array.from({length: days}, (_, i) => ({
    date: new Date(Date.now() - (days - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    xp: Math.floor(Math.random() * 200) + 50,
    completion: Math.floor(Math.random() * 30) + 10,
    accuracy: Math.floor(Math.random() * 20) + 75
  }));
}

function groupAchievementsByCategory(achievements: Achievement[]) {
  const categories = achievements.reduce((acc, achievement) => {
    const category = achievement.title.includes('Sort') ? 'Sorting' : 
                     achievement.title.includes('Speed') ? 'Performance' : 'General';
    
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(achievement);
    return acc;
  }, {} as Record<string, Achievement[]>);

  return Object.entries(categories).map(([name, achievements]) => ({
    name,
    achievements
  }));
}

function getSkillRecommendations(skill: string, progress: number): string[] {
  if (progress < 30) {
    return ['Start with basics', 'Practice fundamentals'];
  } else if (progress < 70) {
    return ['Try advanced problems', 'Focus on edge cases'];
  } else {
    return ['Teach others', 'Explore variations'];
  }
}

function createDefaultGoal(): LearningGoal {
  return {
    id: `goal-${Date.now()}`,
    title: 'New Learning Goal',
    description: 'Set your target and start learning',
    targetValue: 10,
    currentProgress: 0,
    unit: 'items',
    status: 'active',
    category: 'general'
  };
}

async function loadFriendActivities(userId: string) {
  // Mock friend activities
  return [
    {
      friendId: 'friend-1',
      friendName: 'Alice',
      description: 'completed Merge Sort challenge',
      timestamp: '2 hours ago'
    },
    {
      friendId: 'friend-2',
      friendName: 'Bob',
      description: 'earned Speed Demon achievement',
      timestamp: '5 hours ago'
    }
  ];
}