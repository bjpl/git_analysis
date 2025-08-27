import React from 'react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  PieChart, 
  Pie, 
  Cell, 
  LineChart, 
  Line, 
  ResponsiveContainer,
  Area,
  AreaChart
} from 'recharts';
import { 
  TrendingUp, 
  Target, 
  Award, 
  Clock, 
  Brain,
  Zap,
  BookOpen,
  CheckCircle,
  AlertCircle,
  Calendar
} from 'lucide-react';
import { VocabularyStats, MasteryLevel } from '../../types';
import { useVocabulary } from '../../hooks/useVocabulary';
import { Card } from '../Shared/Card/Card';

interface VocabularyStatsProps {
  className?: string;
  showDetailedCharts?: boolean;
}

export function VocabularyStats({ 
  className = '', 
  showDetailedCharts = true 
}: VocabularyStatsProps) {
  const { stats, vocabularyItems, getDueForReview, isLoading } = useVocabulary();

  if (isLoading) {
    return (
      <div className={`vocabulary-stats ${className}`}>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          {[1, 2, 3, 4].map(i => (
            <Card key={i} className="p-6">
              <div className="animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-8 bg-gray-200 rounded w-1/2"></div>
              </div>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (!stats) return null;

  const dueForReview = getDueForReview();
  const masteryData = [
    { name: 'New', value: stats.newWords, color: '#6b7280' },
    { name: 'Learning', value: stats.learningWords, color: '#f59e0b' },
    { name: 'Review', value: stats.reviewWords, color: '#3b82f6' },
    { name: 'Mastered', value: stats.masteredWords, color: '#10b981' }
  ];

  const categoryData = Object.entries(stats.categoryBreakdown).map(([name, count]) => ({
    name,
    value: count
  }));

  const weeklyData = stats.weeklyProgress.map((count, index) => ({
    day: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][index],
    words: count,
    reviews: Math.floor(count * 1.5) // Estimated reviews
  }));

  const difficultyData = Array.from({ length: 10 }, (_, i) => {
    const level = i + 1;
    const count = vocabularyItems.filter(item => item.difficulty === level).length;
    return { difficulty: level, count };
  });

  const progressPercentage = stats.dailyGoal > 0 
    ? Math.min(100, (stats.dailyProgress / stats.dailyGoal) * 100)
    : 0;

  const avgAccuracy = stats.accuracy;
  const retentionRate = stats.totalWords > 0 
    ? (stats.masteredWords / stats.totalWords) * 100 
    : 0;

  return (
    <div className={`vocabulary-stats ${className}`}>
      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {/* Total Words */}
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Words</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {stats.totalWords.toLocaleString()}
              </p>
            </div>
            <div className="p-3 bg-blue-100 dark:bg-blue-900 rounded-full">
              <BookOpen className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
          </div>
          <div className="mt-4">
            <div className="flex items-center text-sm">
              <span className={`font-medium ${
                stats.masteredWords > stats.totalWords * 0.5 
                  ? 'text-green-600' 
                  : 'text-yellow-600'
              }`}>
                {Math.round(retentionRate)}% mastered
              </span>
            </div>
          </div>
        </Card>

        {/* Daily Progress */}
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Daily Progress</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {stats.dailyProgress}/{stats.dailyGoal}
              </p>
            </div>
            <div className="p-3 bg-green-100 dark:bg-green-900 rounded-full">
              <Target className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
          </div>
          <div className="mt-4">
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div 
                className="bg-green-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${progressPercentage}%` }}
              ></div>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              {Math.round(progressPercentage)}% of daily goal
            </p>
          </div>
        </Card>

        {/* Current Streak */}
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Current Streak</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {stats.streak} days
              </p>
            </div>
            <div className="p-3 bg-orange-100 dark:bg-orange-900 rounded-full">
              <Zap className="w-6 h-6 text-orange-600 dark:text-orange-400" />
            </div>
          </div>
          <div className="mt-4">
            <div className="flex items-center text-sm">
              <span className="text-orange-600 font-medium">
                🔥 Keep it going!
              </span>
            </div>
          </div>
        </Card>

        {/* Due for Review */}
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Due for Review</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {dueForReview.length}
              </p>
            </div>
            <div className={`p-3 rounded-full ${
              dueForReview.length > 10 
                ? 'bg-red-100 dark:bg-red-900' 
                : dueForReview.length > 0 
                ? 'bg-yellow-100 dark:bg-yellow-900' 
                : 'bg-gray-100 dark:bg-gray-700'
            }`}>
              <Clock className={`w-6 h-6 ${
                dueForReview.length > 10 
                  ? 'text-red-600 dark:text-red-400' 
                  : dueForReview.length > 0 
                  ? 'text-yellow-600 dark:text-yellow-400' 
                  : 'text-gray-600 dark:text-gray-400'
              }`} />
            </div>
          </div>
          <div className="mt-4">
            <div className="text-sm text-gray-600 dark:text-gray-400">
              {dueForReview.length === 0 
                ? 'All caught up!' 
                : dueForReview.length === 1 
                ? 'Start reviewing' 
                : 'Time to review'
              }
            </div>
          </div>
        </Card>
      </div>

      {/* Detailed Charts */}
      {showDetailedCharts && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Mastery Level Distribution */}
          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Mastery Distribution
              </h3>
              <Award className="w-5 h-5 text-gray-500" />
            </div>
            
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={masteryData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    dataKey="value"
                    label={({ name, value, percent }) => 
                      `${name}: ${value} (${(percent * 100).toFixed(0)}%)`
                    }
                  >
                    {masteryData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </Card>

          {/* Weekly Activity */}
          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Weekly Activity
              </h3>
              <TrendingUp className="w-5 h-5 text-gray-500" />
            </div>
            
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={weeklyData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="day" />
                  <YAxis />
                  <Tooltip />
                  <Area 
                    type="monotone" 
                    dataKey="words" 
                    stackId="1"
                    stroke="#3b82f6" 
                    fill="#3b82f6" 
                    fillOpacity={0.6}
                    name="Words Added"
                  />
                  <Area 
                    type="monotone" 
                    dataKey="reviews" 
                    stackId="1"
                    stroke="#10b981" 
                    fill="#10b981" 
                    fillOpacity={0.6}
                    name="Reviews Completed"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </div>
      )}

      {/* Additional Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Category Breakdown */}
        {categoryData.length > 0 && (
          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Categories
              </h3>
              <Brain className="w-5 h-5 text-gray-500" />
            </div>
            
            <div className="space-y-3">
              {categoryData.slice(0, 5).map((category, index) => {
                const percentage = (category.value / stats.totalWords) * 100;
                return (
                  <div key={category.name} className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      {category.name}
                    </span>
                    <div className="flex items-center gap-3">
                      <div className="w-24 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full"
                          style={{ width: `${percentage}%` }}
                        ></div>
                      </div>
                      <span className="text-sm text-gray-600 dark:text-gray-400 w-8">
                        {category.value}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </Card>
        )}

        {/* Performance Metrics */}
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Performance
            </h3>
            <CheckCircle className="w-5 h-5 text-gray-500" />
          </div>
          
          <div className="space-y-4">
            {/* Accuracy */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Average Accuracy
                </span>
                <span className={`text-sm font-bold ${
                  avgAccuracy >= 80 
                    ? 'text-green-600' 
                    : avgAccuracy >= 60 
                    ? 'text-yellow-600' 
                    : 'text-red-600'
                }`}>
                  {Math.round(avgAccuracy)}%
                </span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full transition-all duration-300 ${
                    avgAccuracy >= 80 
                      ? 'bg-green-600' 
                      : avgAccuracy >= 60 
                      ? 'bg-yellow-600' 
                      : 'bg-red-600'
                  }`}
                  style={{ width: `${avgAccuracy}%` }}
                ></div>
              </div>
            </div>

            {/* Average Difficulty */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Average Difficulty
                </span>
                <span className="text-sm font-bold text-gray-900 dark:text-white">
                  {stats.averageDifficulty.toFixed(1)}/10
                </span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div 
                  className="bg-purple-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${(stats.averageDifficulty / 10) * 100}%` }}
                ></div>
              </div>
            </div>

            {/* Retention Rate */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Retention Rate
                </span>
                <span className="text-sm font-bold text-green-600">
                  {Math.round(retentionRate)}%
                </span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div 
                  className="bg-green-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${retentionRate}%` }}
                ></div>
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card className="mt-6 p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Quick Actions
        </h3>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button className="flex flex-col items-center p-4 bg-blue-50 dark:bg-blue-900 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-800 transition-colors">
            <Zap className="w-6 h-6 text-blue-600 dark:text-blue-400 mb-2" />
            <span className="text-sm font-medium text-blue-700 dark:text-blue-300">
              Start Review
            </span>
            <span className="text-xs text-blue-600 dark:text-blue-400">
              {dueForReview.length} due
            </span>
          </button>
          
          <button className="flex flex-col items-center p-4 bg-green-50 dark:bg-green-900 rounded-lg hover:bg-green-100 dark:hover:bg-green-800 transition-colors">
            <Target className="w-6 h-6 text-green-600 dark:text-green-400 mb-2" />
            <span className="text-sm font-medium text-green-700 dark:text-green-300">
              Set Goal
            </span>
            <span className="text-xs text-green-600 dark:text-green-400">
              Daily target
            </span>
          </button>
          
          <button className="flex flex-col items-center p-4 bg-purple-50 dark:bg-purple-900 rounded-lg hover:bg-purple-100 dark:hover:bg-purple-800 transition-colors">
            <BookOpen className="w-6 h-6 text-purple-600 dark:text-purple-400 mb-2" />
            <span className="text-sm font-medium text-purple-700 dark:text-purple-300">
              Add Words
            </span>
            <span className="text-xs text-purple-600 dark:text-purple-400">
              Expand vocabulary
            </span>
          </button>
          
          <button className="flex flex-col items-center p-4 bg-orange-50 dark:bg-orange-900 rounded-lg hover:bg-orange-100 dark:hover:bg-orange-800 transition-colors">
            <Calendar className="w-6 h-6 text-orange-600 dark:text-orange-400 mb-2" />
            <span className="text-sm font-medium text-orange-700 dark:text-orange-300">
              Schedule
            </span>
            <span className="text-xs text-orange-600 dark:text-orange-400">
              Plan reviews
            </span>
          </button>
        </div>
      </Card>
    </div>
  );
}