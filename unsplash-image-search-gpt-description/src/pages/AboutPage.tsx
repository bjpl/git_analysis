import React from 'react';
import { Link } from 'react-router-dom';
import { cn } from '@/utils/cn';
import { Button } from '@/components/Shared/Button/Button';
import {
  SparklesIcon,
  AcademicCapIcon,
  GlobeAltIcon,
  DevicePhoneMobileIcon,
  ShieldCheckIcon,
  ArrowRightIcon,
  HeartIcon,
  LightBulbIcon,
  RocketLaunchIcon
} from '@heroicons/react/24/outline';

interface FeatureHighlight {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  description: string;
}

interface TeamMember {
  name: string;
  role: string;
  description: string;
  avatar?: string;
}

const features: FeatureHighlight[] = [
  {
    icon: SparklesIcon,
    title: 'AI-Powered Learning',
    description: 'Advanced AI generates contextual Spanish descriptions with vocabulary extraction and difficulty adaptation.'
  },
  {
    icon: AcademicCapIcon,
    title: 'Spaced Repetition',
    description: 'Scientifically-proven spaced repetition algorithm optimizes your learning schedule for maximum retention.'
  },
  {
    icon: GlobeAltIcon,
    title: 'Visual Learning',
    description: 'Beautiful images from Unsplash create visual associations that enhance memory and make learning engaging.'
  },
  {
    icon: DevicePhoneMobileIcon,
    title: 'Progressive Web App',
    description: 'Works offline, installs like a native app, and syncs across all your devices for learning on the go.'
  },
  {
    icon: ShieldCheckIcon,
    title: 'Privacy First',
    description: 'Your learning data stays private and secure. We never sell your information or track you unnecessarily.'
  },
  {
    icon: LightBulbIcon,
    title: 'Adaptive Difficulty',
    description: 'The app learns your proficiency level and adapts question difficulty to keep you in the optimal learning zone.'
  }
];

const team: TeamMember[] = [
  {
    name: 'VocabLens Team',
    role: 'Development Team',
    description: 'Passionate language learners and developers committed to making vocabulary acquisition more effective and enjoyable.'
  }
];

/**
 * About Page - Information about VocabLens
 * Features:
 * - Project overview and mission
 * - Feature highlights with visual icons
 * - Technology stack information
 * - Privacy and security information
 * - Getting started call-to-action
 */
export function AboutPage() {
  return (
    <div className="min-h-screen bg-white dark:bg-gray-900">
      {/* Hero Section */}
      <div className="relative overflow-hidden bg-gradient-to-b from-primary-50 to-white dark:from-primary-900/20 dark:to-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 lg:py-24">
          <div className="text-center max-w-4xl mx-auto">
            <div className="flex items-center justify-center mb-6">
              <div className="w-16 h-16 bg-gradient-to-br from-primary-500 to-primary-600 rounded-2xl flex items-center justify-center shadow-lg">
                <AcademicCapIcon className="w-10 h-10 text-white" />
              </div>
            </div>
            
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 dark:text-white mb-6">
              About{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-600 to-blue-600">
                VocabLens
              </span>
            </h1>
            
            <p className="text-xl sm:text-2xl text-gray-600 dark:text-gray-300 mb-8 leading-relaxed">
              VocabLens revolutionizes Spanish vocabulary learning by combining visual learning, 
              AI-powered descriptions, and spaced repetition in a beautiful, offline-ready Progressive Web App.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Button
                as={Link}
                to="/search"
                variant="primary"
                size="lg"
                className="group"
              >
                Try It Now
                <ArrowRightIcon className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Button>
              
              <Button
                as={Link}
                to="/vocabulary"
                variant="outline"
                size="lg"
              >
                View Features
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Mission Section */}
      <div className="py-16 lg:py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <HeartIcon className="w-12 h-12 text-primary-600 dark:text-primary-400 mx-auto mb-6" />
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-6">
              Our Mission
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-300 leading-relaxed">
              We believe language learning should be visual, engaging, and scientifically effective. 
              VocabLens makes Spanish vocabulary acquisition more intuitive by connecting words with 
              beautiful imagery and leveraging proven learning techniques like spaced repetition.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <div className="text-center p-6">
              <div className="w-16 h-16 bg-blue-100 dark:bg-blue-900/20 rounded-xl flex items-center justify-center mx-auto mb-4">
                <LightBulbIcon className="w-8 h-8 text-blue-600 dark:text-blue-400" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">
                Visual Learning
              </h3>
              <p className="text-gray-600 dark:text-gray-300">
                Research shows that visual associations dramatically improve vocabulary retention 
                and recall compared to traditional text-only methods.
              </p>
            </div>

            <div className="text-center p-6">
              <div className="w-16 h-16 bg-green-100 dark:bg-green-900/20 rounded-xl flex items-center justify-center mx-auto mb-4">
                <SparklesIcon className="w-8 h-8 text-green-600 dark:text-green-400" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">
                AI Enhancement
              </h3>
              <p className="text-gray-600 dark:text-gray-300">
                AI-generated descriptions provide rich context and extract key vocabulary, 
                creating comprehensive learning experiences from every image.
              </p>
            </div>

            <div className="text-center p-6">
              <div className="w-16 h-16 bg-purple-100 dark:bg-purple-900/20 rounded-xl flex items-center justify-center mx-auto mb-4">
                <RocketLaunchIcon className="w-8 h-8 text-purple-600 dark:text-purple-400" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">
                Scientific Approach
              </h3>
              <p className="text-gray-600 dark:text-gray-300">
                Built on proven spaced repetition algorithms that optimize review timing 
                for maximum long-term retention and minimal study time.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="bg-gray-50 dark:bg-gray-800/50 py-16 lg:py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
              Why Choose VocabLens?
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
              We've carefully designed every feature to make your Spanish learning journey 
              more effective, enjoyable, and sustainable.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div
                key={index}
                className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6 hover:shadow-lg transition-shadow"
              >
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0">
                    <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900/20 rounded-lg flex items-center justify-center">
                      <feature.icon className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                    </div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                      {feature.title}
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-300 leading-relaxed">
                      {feature.description}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Technology Section */}
      <div className="py-16 lg:py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
              Built with Modern Technology
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
              VocabLens is built as a Progressive Web App using cutting-edge technologies 
              for the best possible user experience.
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-4xl mx-auto">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 dark:bg-blue-900/20 rounded-xl flex items-center justify-center mx-auto mb-3">
                <span className="text-2xl font-bold text-blue-600 dark:text-blue-400">⚛️</span>
              </div>
              <h4 className="font-semibold text-gray-900 dark:text-white">React 18</h4>
              <p className="text-sm text-gray-600 dark:text-gray-300">Modern UI framework</p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-purple-100 dark:bg-purple-900/20 rounded-xl flex items-center justify-center mx-auto mb-3">
                <span className="text-2xl font-bold text-purple-600 dark:text-purple-400">TS</span>
              </div>
              <h4 className="font-semibold text-gray-900 dark:text-white">TypeScript</h4>
              <p className="text-sm text-gray-600 dark:text-gray-300">Type-safe development</p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 dark:bg-green-900/20 rounded-xl flex items-center justify-center mx-auto mb-3">
                <span className="text-2xl font-bold text-green-600 dark:text-green-400">🔧</span>
              </div>
              <h4 className="font-semibold text-gray-900 dark:text-white">Vite</h4>
              <p className="text-sm text-gray-600 dark:text-gray-300">Lightning-fast builds</p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-indigo-100 dark:bg-indigo-900/20 rounded-xl flex items-center justify-center mx-auto mb-3">
                <span className="text-2xl font-bold text-indigo-600 dark:text-indigo-400">🎨</span>
              </div>
              <h4 className="font-semibold text-gray-900 dark:text-white">Tailwind</h4>
              <p className="text-sm text-gray-600 dark:text-gray-300">Utility-first CSS</p>
            </div>
          </div>
        </div>
      </div>

      {/* Privacy Section */}
      <div className="bg-gray-50 dark:bg-gray-800/50 py-16 lg:py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto">
            <ShieldCheckIcon className="w-12 h-12 text-green-600 dark:text-green-400 mx-auto mb-6" />
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-6">
              Your Privacy Matters
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-300 mb-8 leading-relaxed">
              We believe privacy is fundamental. VocabLens is designed with privacy by design principles:
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-left">
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 bg-green-500 rounded-full mt-3 flex-shrink-0" />
                <div>
                  <h4 className="font-semibold text-gray-900 dark:text-white mb-1">
                    Local-First Storage
                  </h4>
                  <p className="text-sm text-gray-600 dark:text-gray-300">
                    Your vocabulary and progress data is stored locally on your device first.
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <div className="w-2 h-2 bg-green-500 rounded-full mt-3 flex-shrink-0" />
                <div>
                  <h4 className="font-semibold text-gray-900 dark:text-white mb-1">
                    No Unnecessary Tracking
                  </h4>
                  <p className="text-sm text-gray-600 dark:text-gray-300">
                    We only collect data that directly improves your learning experience.
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <div className="w-2 h-2 bg-green-500 rounded-full mt-3 flex-shrink-0" />
                <div>
                  <h4 className="font-semibold text-gray-900 dark:text-white mb-1">
                    Transparent Practices
                  </h4>
                  <p className="text-sm text-gray-600 dark:text-gray-300">
                    Clear information about what data we collect and how it's used.
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <div className="w-2 h-2 bg-green-500 rounded-full mt-3 flex-shrink-0" />
                <div>
                  <h4 className="font-semibold text-gray-900 dark:text-white mb-1">
                    Data Portability
                  </h4>
                  <p className="text-sm text-gray-600 dark:text-gray-300">
                    Export your vocabulary and learning data at any time.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Call to Action */}
      <div className="py-16 lg:py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-6">
            Ready to Transform Your Spanish Learning?
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-300 mb-8 max-w-2xl mx-auto">
            Join thousands of learners who are already using VocabLens to master Spanish vocabulary 
            through visual learning and spaced repetition.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button
              as={Link}
              to="/search"
              variant="primary"
              size="lg"
              className="group"
            >
              Start Learning Today
              <ArrowRightIcon className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Button>
            
            <Button
              as={Link}
              to="/vocabulary"
              variant="outline"
              size="lg"
            >
              Explore Features
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AboutPage;