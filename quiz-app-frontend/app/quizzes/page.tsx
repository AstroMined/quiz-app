'use client';

import ProtectedRoute from '@/components/ProtectedRoute';
import QuizList from '@/components/QuizList';

export default function Quizzes() {
  return (
    <ProtectedRoute>
      <div className="container mx-auto px-4">
        <h1 className="text-3xl font-bold mb-4">Available Quizzes</h1>
        <QuizList />
      </div>
    </ProtectedRoute>
  );
}