import React from 'react';
import { SignupForm } from '../components/Auth/SignupForm';
import { Card } from '../components/Shared/Card/Card';
import { Link } from 'react-router-dom';

const SignupPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
      <div className="max-w-md w-full mx-4">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Join VocabLens
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            Start your visual vocabulary learning journey
          </p>
        </div>

        <Card className="p-6">
          <SignupForm />
          
          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600 dark:text-gray-300">
              Already have an account?{' '}
              <Link 
                to="/login" 
                className="text-indigo-600 hover:text-indigo-700 font-medium"
              >
                Sign in
              </Link>
            </p>
          </div>
        </Card>

        <div className="mt-8 text-center">
          <div className="text-xs text-gray-500 dark:text-gray-400">
            By signing up, you agree to our Terms of Service and Privacy Policy
          </div>
        </div>
      </div>
    </div>
  );
};

export default SignupPage;