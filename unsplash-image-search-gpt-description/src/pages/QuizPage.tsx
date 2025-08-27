import React from 'react';

const QuizPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Vocabulary Quiz
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            Practice your Spanish vocabulary with spaced repetition quizzes
          </p>
        </div>
        
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Practice Session</h2>
          <p className="text-gray-600 dark:text-gray-300">
            Quiz functionality will be available here. Add some vocabulary words first!
          </p>
          {/* Quiz components will be integrated here */}
        </div>
      </div>
    </div>
  );
};

export default QuizPage;