// src/components/QuizList.tsx
'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { QuestionSetsService, QuestionSetSchema } from '@/api';

const QuizList = () => {
  const [quizzes, setQuizzes] = useState<QuestionSetSchema[]>([]);

  useEffect(() => {
    const fetchQuizzes = async () => {
      try {
        const response = await QuestionSetsService.readQuestionSetsEndpointQuestionSetsGet();
        setQuizzes(response);
      } catch (error) {
        console.error('Failed to fetch quizzes:', error);
      }
    };

    fetchQuizzes();
  }, []);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {quizzes.map((quiz) => (
        <Link key={quiz.id} href={`/quizzes/${quiz.id}`}>
          <div className="border p-4 rounded-lg hover:shadow-md transition-shadow">
            <h2 className="text-xl font-bold mb-2">{quiz.name}</h2>
            <p>Number of questions: {quiz.question_ids?.length || 0}</p>
          </div>
        </Link>
      ))}
    </div>
  );
};

export default QuizList;