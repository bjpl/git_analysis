import React, { useState, useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  ScatterChart,
  Scatter
} from 'recharts';
import {
  TrendingUp,
  TrendingDown,
  Target,
  Clock,
  Calendar,
  Brain,
  Award,
  Zap,
  BarChart3,
  PieChart as PieChartIcon,
  Activity,
  Users
} from 'lucide-react';
import { VocabularyAnalytics, VocabularyItem, MasteryLevel } from '../../types';
import { useVocabulary } from '../../hooks/useVocabulary';
import { Card } from '../Shared/Card/Card';
import { Button } from '../Shared/Button/Button';

interface VocabularyAnalyticsProps {
  className?: string;
  timeRange?: '7d' | '30d' | '90d' | '1y' | 'all';
}

export function VocabularyAnalyticsDashboard({
  className = '',
  timeRange = '30d'
}: VocabularyAnalyticsProps) {
  const { vocabularyItems, stats, isLoading } = useVocabulary();
  const [selectedTab, setSelectedTab] = useState<'overview' | 'learning' | 'performance' | 'trends'>('overview');
  const [chartType, setChartType] = useState<'line' | 'area' | 'bar'>('area');

  // Calculate analytics data
  const analytics = useMemo(() => {
    return calculateAnalytics(vocabularyItems, timeRange);
  }, [vocabularyItems, timeRange]);

  const tabs = [
    { id: 'overview', label: 'Overview', icon: <BarChart3 className="w-4 h-4" /> },
    { id: 'learning', label: 'Learning', icon: <Brain className="w-4 h-4" /> },
    { id: 'performance', label: 'Performance', icon: <Target className="w-4 h-4" /> },
    { id: 'trends', label: 'Trends', icon: <TrendingUp className="w-4 h-4" /> }
  ];

  if (isLoading) {
    return (
      <div className={`vocabulary-analytics ${className}`}>
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`vocabulary-analytics ${className}`}>
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Learning Analytics
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Insights into your vocabulary learning journey and progress patterns.
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-1 mb-6 p-1 bg-gray-100 dark:bg-gray-800 rounded-lg">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setSelectedTab(tab.id as any)}
            className={`flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-md transition-colors ${
              selectedTab === tab.id
                ? 'bg-white dark:bg-gray-700 text-blue-600 dark:text-blue-400 shadow-sm'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            {tab.icon}
            {tab.label}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {selectedTab === 'overview' && (
        <div className="space-y-6">
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <MetricCard
              title="Learning Velocity"
              value={`${analytics.learningVelocity.toFixed(1)} words/day`}
              change={+12.5}
              icon={<TrendingUp className="w-5 h-5" />}
              color="blue"
            />
            
            <MetricCard
              title="Retention Rate"
              value={`${(analytics.retentionRate * 100).toFixed(1)}%`}
              change={+5.2}
              icon={<Brain className="w-5 h-5" />}
              color="green"
            />
            
            <MetricCard
              title="Study Streak"
              value={`${stats?.streak || 0} days`}
              change={stats?.streak ? +1 : 0}
              icon={<Zap className="w-5 h-5" />}
              color="orange"
            />
            
            <MetricCard
              title="Avg. Session Time"
              value="12.5 min"
              change={-2.1}
              icon={<Clock className="w-5 h-5" />}
              color="purple"
            />
          </div>

          {/* Weekly Activity Chart */}
          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Weekly Activity
              </h3>
              <div className="flex gap-2">
                {(['line', 'area', 'bar'] as const).map((type) => (
                  <Button
                    key={type}
                    variant={chartType === type ? 'primary' : 'ghost'}
                    size="sm"
                    onClick={() => setChartType(type)}
                  >
                    {type}
                  </Button>
                ))}
              </div>
            </div>
            
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                {chartType === 'line' && (
                  <LineChart data={analytics.weeklyActivity}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Line
                      type="monotone"
                      dataKey="wordsLearned"
                      stroke="#3b82f6"
                      strokeWidth={2}
                      name="Words Learned"
                    />
                    <Line
                      type="monotone"
                      dataKey="reviewsCompleted"
                      stroke="#10b981"
                      strokeWidth={2}
                      name="Reviews Completed"
                    />
                  </LineChart>
                )}
                
                {chartType === 'area' && (
                  <AreaChart data={analytics.weeklyActivity}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Area
                      type="monotone"
                      dataKey="wordsLearned"
                      stackId="1"
                      stroke="#3b82f6"
                      fill="#3b82f6"
                      fillOpacity={0.6}
                      name="Words Learned"
                    />
                    <Area
                      type="monotone"
                      dataKey="reviewsCompleted"
                      stackId="2"
                      stroke="#10b981"
                      fill="#10b981"
                      fillOpacity={0.6}
                      name="Reviews Completed"
                    />
                  </AreaChart>
                )}
                
                {chartType === 'bar' && (
                  <BarChart data={analytics.weeklyActivity}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="wordsLearned" fill="#3b82f6" name="Words Learned" />
                    <Bar dataKey="reviewsCompleted" fill="#10b981" name="Reviews Completed" />
                  </BarChart>
                )}
              </ResponsiveContainer>
            </div>
          </Card>

          {/* Category Progress */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Category Progress
            </h3>
            
            <div className="space-y-4">
              {Object.entries(analytics.categoryProgress).map(([category, progress]) => (
                <div key={category}>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      {category}
                    </span>
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                      {progress.mastered}/{progress.total} ({((progress.mastered / progress.total) * 100).toFixed(0)}%)
                    </div>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${(progress.mastered / progress.total) * 100}%` }}
                    ></div>
                  </div>
                  <div className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                    Avg. Accuracy: {(progress.accuracy * 100).toFixed(1)}%
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}

      {/* Learning Tab */}
      {selectedTab === 'learning' && (
        <div className="space-y-6">
          {/* Difficulty Distribution */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Difficulty Distribution
            </h3>
            
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={Object.entries(analytics.difficultyDistribution).map(([level, count]) => ({
                  difficulty: `Level ${level}`,
                  count
                }))}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="difficulty" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#8b5cf6" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>

          {/* Mastery Timeline */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Learning Progress Over Time
            </h3>
            
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={generateMasteryTimeline(vocabularyItems)}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Area
                    type="monotone"
                    dataKey="new"
                    stackId="1"
                    stroke="#6b7280"
                    fill="#6b7280"
                    name="New"
                  />
                  <Area
                    type="monotone"
                    dataKey="learning"
                    stackId="1"
                    stroke="#f59e0b"
                    fill="#f59e0b"
                    name="Learning"
                  />
                  <Area
                    type="monotone"
                    dataKey="review"
                    stackId="1"
                    stroke="#3b82f6"
                    fill="#3b82f6"
                    name="Review"
                  />
                  <Area
                    type="monotone"
                    dataKey="mastered"
                    stackId="1"
                    stroke="#10b981"
                    fill="#10b981"
                    name="Mastered"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </div>
      )}

      {/* Performance Tab */}
      {selectedTab === 'performance' && (
        <div className="space-y-6">
          {/* Accuracy vs Difficulty Scatter */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Accuracy vs Difficulty
            </h3>
            
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart data={vocabularyItems.map(item => ({
                  difficulty: item.difficulty,
                  accuracy: item.timesReviewed > 0 ? (item.timesCorrect / item.timesReviewed) * 100 : 0,
                  masteryLevel: item.masteryLevel
                })).filter(item => item.accuracy > 0)}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="difficulty" type="number" domain={[1, 10]} name="Difficulty" />
                  <YAxis dataKey="accuracy" type="number" domain={[0, 100]} name="Accuracy %" />
                  <Tooltip />
                  <Scatter dataKey="accuracy" fill="#3b82f6" />
                </ScatterChart>
              </ResponsiveContainer>
            </div>
          </Card>

          {/* Review Performance */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Review Performance Trends
            </h3>
            
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={analytics.weeklyActivity}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Line
                    type="monotone"
                    dataKey="accuracy"
                    stroke="#10b981"
                    strokeWidth={2}
                    name="Accuracy %"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </div>
      )}

      {/* Trends Tab */}
      {selectedTab === 'trends' && (
        <div className="space-y-6">
          {/* Streak History */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Study Streak History
            </h3>
            
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={analytics.streakHistory}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Area
                    type="monotone"
                    dataKey="streak"
                    stroke="#f59e0b"
                    fill="#f59e0b"
                    fillOpacity={0.6}
                    name="Streak Days"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </Card>

          {/* Learning Insights */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Learning Insights
            </h3>
            
            <div className="space-y-4">
              <div className="p-4 bg-blue-50 dark:bg-blue-900 rounded-lg">
                <div className="flex items-center gap-3">
                  <TrendingUp className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                  <div>
                    <h4 className="font-medium text-blue-900 dark:text-blue-100">
                      Strong Learning Velocity
                    </h4>
                    <p className="text-sm text-blue-700 dark:text-blue-300">
                      You're learning {analytics.learningVelocity.toFixed(1)} words per day on average.
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="p-4 bg-green-50 dark:bg-green-900 rounded-lg">
                <div className="flex items-center gap-3">
                  <Brain className="w-5 h-5 text-green-600 dark:text-green-400" />
                  <div>
                    <h4 className="font-medium text-green-900 dark:text-green-100">
                      Excellent Retention
                    </h4>
                    <p className="text-sm text-green-700 dark:text-green-300">
                      Your retention rate is {(analytics.retentionRate * 100).toFixed(1)}%, which is above average.
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="p-4 bg-yellow-50 dark:bg-yellow-900 rounded-lg">
                <div className="flex items-center gap-3">
                  <Target className="w-5 h-5 text-yellow-600 dark:text-yellow-400" />
                  <div>
                    <h4 className="font-medium text-yellow-900 dark:text-yellow-100">
                      Recommendation
                    </h4>
                    <p className="text-sm text-yellow-700 dark:text-yellow-300">
                      Consider focusing more on Level {getMostChallengingLevel(analytics.difficultyDistribution)} words to improve overall proficiency.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}

// Helper Components
interface MetricCardProps {
  title: string;
  value: string;
  change: number;
  icon: React.ReactNode;
  color: 'blue' | 'green' | 'orange' | 'purple';
}

function MetricCard({ title, value, change, icon, color }: MetricCardProps) {
  const colorClasses = {
    blue: 'bg-blue-100 text-blue-600 dark:bg-blue-900 dark:text-blue-400',
    green: 'bg-green-100 text-green-600 dark:bg-green-900 dark:text-green-400',
    orange: 'bg-orange-100 text-orange-600 dark:bg-orange-900 dark:text-orange-400',
    purple: 'bg-purple-100 text-purple-600 dark:bg-purple-900 dark:text-purple-400'
  };

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600 dark:text-gray-400">{title}</p>
          <p className="text-2xl font-bold text-gray-900 dark:text-white">{value}</p>
        </div>
        <div className={`p-3 rounded-full ${colorClasses[color]}`}>
          {icon}
        </div>
      </div>
      <div className="mt-4 flex items-center text-sm">
        {change > 0 ? (
          <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
        ) : (
          <TrendingDown className="w-4 h-4 text-red-500 mr-1" />
        )}
        <span className={change > 0 ? 'text-green-600' : 'text-red-600'}>
          {change > 0 ? '+' : ''}{change}%
        </span>
        <span className="text-gray-600 dark:text-gray-400 ml-1">from last period</span>
      </div>
    </Card>
  );
}

// Helper Functions
function calculateAnalytics(items: VocabularyItem[], timeRange: string): VocabularyAnalytics {
  const now = new Date();
  const daysMap = { '7d': 7, '30d': 30, '90d': 90, '1y': 365, 'all': Infinity };
  const days = daysMap[timeRange as keyof typeof daysMap] || 30;
  
  const cutoffDate = new Date(now.getTime() - (days * 24 * 60 * 60 * 1000));
  const recentItems = items.filter(item => new Date(item.createdAt) >= cutoffDate);
  
  // Calculate learning velocity
  const learningVelocity = days === Infinity ? 0 : recentItems.length / days;
  
  // Calculate retention rate
  const masteredCount = items.filter(item => item.masteryLevel === MasteryLevel.MASTERED).length;
  const retentionRate = items.length > 0 ? masteredCount / items.length : 0;
  
  // Calculate difficulty distribution
  const difficultyDistribution = items.reduce((acc, item) => {
    acc[item.difficulty] = (acc[item.difficulty] || 0) + 1;
    return acc;
  }, {} as Record<number, number>);
  
  // Calculate category progress
  const categoryProgress = items.reduce((acc, item) => {
    const category = item.category || 'Uncategorized';
    if (!acc[category]) {
      acc[category] = { total: 0, mastered: 0, accuracy: 0 };
    }
    acc[category].total++;
    if (item.masteryLevel === MasteryLevel.MASTERED) {
      acc[category].mastered++;
    }
    // Calculate accuracy for category
    const accuracy = item.timesReviewed > 0 ? item.timesCorrect / item.timesReviewed : 0;
    acc[category].accuracy = (acc[category].accuracy + accuracy) / acc[category].total;
    return acc;
  }, {} as Record<string, { total: number; mastered: number; accuracy: number }>);
  
  // Generate weekly activity (mock data)
  const weeklyActivity = Array.from({ length: Math.min(days, 30) }, (_, i) => {
    const date = new Date(now.getTime() - (i * 24 * 60 * 60 * 1000));
    return {
      date: date.toISOString().split('T')[0],
      wordsLearned: Math.floor(Math.random() * 5) + 1,
      reviewsCompleted: Math.floor(Math.random() * 10) + 5,
      accuracy: 0.7 + Math.random() * 0.3
    };
  }).reverse();
  
  // Generate streak history (mock data)
  const streakHistory = Array.from({ length: Math.min(days, 30) }, (_, i) => {
    const date = new Date(now.getTime() - (i * 24 * 60 * 60 * 1000));
    return {
      date: date.toISOString().split('T')[0],
      streak: Math.max(0, 10 - Math.floor(Math.random() * 5))
    };
  }).reverse();
  
  return {
    learningVelocity,
    retentionRate,
    difficultyDistribution,
    categoryProgress,
    weeklyActivity,
    streakHistory
  };
}

function generateMasteryTimeline(items: VocabularyItem[]) {
  // Group items by creation date and calculate mastery distribution
  const timeline = items.reduce((acc, item) => {
    const date = item.createdAt.toISOString().split('T')[0];
    if (!acc[date]) {
      acc[date] = { new: 0, learning: 0, review: 0, mastered: 0 };
    }
    acc[date][item.masteryLevel]++;
    return acc;
  }, {} as Record<string, Record<MasteryLevel, number>>);
  
  return Object.entries(timeline)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([date, counts]) => ({ date, ...counts }));
}

function getMostChallengingLevel(distribution: Record<number, number>): number {
  return parseInt(Object.entries(distribution)
    .sort(([, a], [, b]) => b - a)
    .filter(([level]) => parseInt(level) > 5)
    [0]?.[0] || '5');
}

// Export alias for compatibility
export { VocabularyAnalyticsDashboard as VocabularyAnalytics };