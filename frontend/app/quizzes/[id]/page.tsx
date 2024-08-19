'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import ProtectedRoute from '@/components/ProtectedRoute';
import { QuestionSetsApi, QuestionSchema } from '@/api';

export default function Quiz() {
  const { id } = useParams();
  const [questions, setQuestions] = useState<QuestionSchema[]>([]);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [userAnswers, setUserAnswers] = useState<{[key: number]: number}>({});
  const [quizCompleted, setQuizCompleted] = useState(false);

  useEffect(() => {
    const fetchQuestions = async () => {
      const api = new QuestionSetsApi();
      try {
        const response = await api.readQuestionSetEndpointQuestionSetsQuestionSetIdGet(Number(id));
        setQuestions(response.data.questions || []);
      } catch (error) {
        console.error('Failed to fetch questions:', error);
      }
    };

    fetchQuestions();
  }, [id]);

  const handleAnswer = (answerId: number) => {
    setUserAnswers({...userAnswers, [currentQuestion]: answerId});
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    } else {
      setQuizCompleted(true);
    }
  };

  const renderQuestion = () => {
    if (questions.length === 0) return <p>Loading...</p>;
    const question = questions[currentQuestion];
    return (
      <div>
        <h2 className="text-xl font-bold mb-4">{question.text}</h2>
        <ul>
          {question.answer_choices?.map((choice) => (
            <li key={choice.id} className="mb-2">
              <button 
                onClick={() => handleAnswer(choice.id)}
                className="w-full text-left p-2 border rounded hover:bg-gray-100"
              >
                {choice.text}
              </button>
            </li>
          ))}
        </ul>
      </div>
    );
  };

  const renderResults = () => {
    const correctAnswers = questions.filter((q, index) => 
      q.answer_choices?.find(c => c.id === userAnswers[index])?.is_correct
    ).length;

    return (
      <div>
        <h2 className="text-2xl font-bold mb-4">Quiz Completed!</h2>
        <p className="text-xl">You got {correctAnswers} out of {questions.length} correct.</p>
      </div>
    );
  };

  return (
    <ProtectedRoute>
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">Quiz {id}</h1>
        {quizCompleted ? renderResults() : renderQuestion()}
      </div>
    </ProtectedRoute>
  );
}