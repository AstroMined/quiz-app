
# Directory: /code/quiz-app/quiz-app-frontend

## File: next-env.d.ts
```ts
/// <reference types="next" />
/// <reference types="next/image-types/global" />

// NOTE: This file should not be edited
// see https://nextjs.org/docs/basic-features/typescript for more information.

```

## File: postcss.config.js
```js
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}

```

## File: tailwind.config.js
```js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

## File: tailwind.config.ts
```ts
import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "gradient-conic":
          "conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))",
      },
    },
  },
  plugins: [],
};
export default config;

```

# Directory: /code/quiz-app/quiz-app-frontend/app

## File: globals.css
```css
@import 'tailwindcss/base';
@import 'tailwindcss/components';
@import 'tailwindcss/utilities';


:root {
  --foreground-rgb: 0, 0, 0;
  --background-start-rgb: 214, 219, 220;
  --background-end-rgb: 255, 255, 255;
}

body {
  color: rgb(var(--foreground-rgb));
  background: linear-gradient(
      to bottom,
      transparent,
      rgb(var(--background-end-rgb))
    )
    rgb(var(--background-start-rgb));
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

h1, h2, h3, h4, h5, h6 {
  font-weight: bold;
}

h1 {
  font-size: 2.5rem;
}

h2 {
  font-size: 2rem;
}

h3 {
  font-size: 1.75rem;
}

a {
  color: #0070f3;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}
```

## File: layout.tsx
```tsx
// app/layout.tsx
import './globals.css';
import { AuthProvider } from '@/contexts/AuthContext';
import NavBar from '@/components/NavBar';
import { initializeApi } from '@/config/api';

// Initialize API configuration
initializeApi();
console.log('API initialized in layout');

export const metadata = {
  title: 'Quiz App',
  description: 'Test your knowledge with our exciting quizzes!',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <AuthProvider>
        <body>
          <div className="min-h-screen flex flex-col">
            <NavBar />
            <main className="flex-grow container mx-auto px-4 py-8">
              {children}
            </main>
            <footer className="bg-gray-200 p-4 text-center">
              © 2023 Quiz App
            </footer>
          </div>
        </body>
      </AuthProvider>
    </html>
  );
}
```

## File: page.tsx
```tsx
import Link from 'next/link';

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen py-2">
      <main className="flex flex-col items-center justify-center w-full flex-1 px-20 text-center">
        <h1 className="text-6xl font-bold">
          Welcome to the Quiz App!
        </h1>

        <p className="mt-3 text-2xl">
          Test your knowledge with our exciting quizzes!
        </p>

        <div className="flex flex-wrap items-center justify-around max-w-4xl mt-6 sm:w-full">
          <Link href="/quizzes" className="p-6 mt-6 text-left border w-96 rounded-xl hover:text-blue-600 focus:text-blue-600">
            <h3 className="text-2xl font-bold">Start a Quiz &rarr;</h3>
            <p className="mt-4 text-xl">
              Choose from a variety of topics and test your knowledge!
            </p>
          </Link>

          <Link href="/leaderboard" className="p-6 mt-6 text-left border w-96 rounded-xl hover:text-blue-600 focus:text-blue-600">
            <h3 className="text-2xl font-bold">Leaderboard &rarr;</h3>
            <p className="mt-4 text-xl">
              See how you rank against other quiz takers!
            </p>
          </Link>
        </div>
      </main>
    </div>
  );
}
```

# Directory: /code/quiz-app/quiz-app-frontend/app/login

## File: page.tsx
```tsx
// app/login/page.tsx
'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { AuthenticationService } from '@/api/services/AuthenticationService';
import { useAuth } from '@/contexts/AuthContext';
import { OpenAPI } from '@/api';
import { initializeApi } from '@/config/api';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const router = useRouter();
  const { login } = useAuth();

  useEffect(() => {
    initializeApi();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    console.log('Login form submitted');
    console.log('API Base URL:', OpenAPI.BASE);
    console.log('Attempting login for username:', username);

    try {
      console.log('Sending login request...');
      const response = await AuthenticationService.loginEndpointLoginPost({
        username: username,
        password: password,
      });

      console.log('Login response received:', response);

      if (response.access_token) {
        console.log('Access token received, logging in...');
        login(response.access_token);
        router.push('/');
      } else {
        console.error('No access token in response:', response);
        setError('Login failed: No access token received');
      }
    } catch (err) {
      console.error('Login error:', err);
      if (err instanceof Error) {
        setError(`Login failed: ${err.message}`);
      } else {
        setError('Invalid username or password');
      }
    }
  };

  return (
    <div className="flex justify-center items-center min-h-screen bg-gray-100">
      <form onSubmit={handleSubmit} className="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4">
        <h2 className="mb-4 text-2xl font-bold">Login</h2>
        {error && <p className="text-red-500 mb-4">{error}</p>}
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="username">
            Username
          </label>
          <input
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            id="username"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        <div className="mb-6">
          <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="password">
            Password
          </label>
          <input
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:shadow-outline"
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <div className="flex items-center justify-between">
          <button
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
            type="submit"
          >
            Sign In
          </button>
        </div>
      </form>
    </div>
  );
}
```

# Directory: /code/quiz-app/quiz-app-frontend/app/register

## File: page.tsx
```tsx
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { AuthenticationService } from '@/api/services/AuthenticationService';
import { OpenAPI } from '@/api/core/OpenAPI';

// Set the base URL for the API
OpenAPI.BASE = 'http://localhost:8000'; // Replace with your actual backend URL

export default function Register() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      const response = await AuthenticationService.registerUserRegisterPost({
        username: username,
        email: email,
        password: password,
      });

      console.log('Registration successful:', response);
      router.push('/login'); // Redirect to login page after successful registration
    } catch (err) {
      console.error('Registration error:', err);
      if (err instanceof Error) {
        setError(`Registration failed: ${err.message}`);
      } else {
        setError('Registration failed. Please try again.');
      }
    }
  };

  return (
    <div className="flex justify-center items-center min-h-screen bg-gray-100">
      <form onSubmit={handleSubmit} className="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4">
        <h2 className="mb-4 text-2xl font-bold">Register</h2>
        {error && <p className="text-red-500 mb-4">{error}</p>}
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="username">
            Username
          </label>
          <input
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            id="username"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="email">
            Email
          </label>
          <input
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div className="mb-6">
          <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="password">
            Password
          </label>
          <input
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:shadow-outline"
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <div className="flex items-center justify-between">
          <button
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
            type="submit"
          >
            Register
          </button>
        </div>
      </form>
    </div>
  );
}
```

# Directory: /code/quiz-app/quiz-app-frontend/app/leaderboard

## File: page.tsx
```tsx
'use client';

import { useEffect, useState } from 'react';
import ProtectedRoute from '@/components/ProtectedRoute';
import { LeaderboardService, LeaderboardSchema } from '@/api';

export default function Leaderboard() {
  const [leaderboard, setLeaderboard] = useState<LeaderboardSchema[]>([]);

  useEffect(() => {
    const fetchLeaderboard = async () => {
      const api = new LeaderboardService();
      try {
        const response = await api.getLeaderboardLeaderboardGet('weekly');
        setLeaderboard(response.data);
      } catch (error) {
        console.error('Failed to fetch leaderboard:', error);
      }
    };

    fetchLeaderboard();
  }, []);

  return (
    <ProtectedRoute>
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">Leaderboard</h1>
        <table className="w-full">
          <thead>
            <tr className="bg-gray-100">
              <th className="p-2 text-left">Rank</th>
              <th className="p-2 text-left">User</th>
              <th className="p-2 text-left">Score</th>
            </tr>
          </thead>
          <tbody>
            {leaderboard.map((entry, index) => (
              <tr key={entry.id} className="border-b">
                <td className="p-2">{index + 1}</td>
                <td className="p-2">{entry.user_id}</td>
                <td className="p-2">{entry.score}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </ProtectedRoute>
  );
}
```

# Directory: /code/quiz-app/quiz-app-frontend/app/quizzes

## File: page.tsx
```tsx
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
```

# Directory: /code/quiz-app/quiz-app-frontend/app/quizzes/[id]

## File: page.tsx
```tsx
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
```

# Directory: /code/quiz-app/quiz-app-frontend/src/contexts

## File: AuthContext.tsx
```tsx
'use client';

import React, { createContext, useState, useEffect, useContext } from 'react';
import { useRouter } from 'next/navigation';

interface AuthContextType {
  isAuthenticated: boolean;
  login: (token: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      setIsAuthenticated(true);
    }
  }, []);

  const login = (token: string) => {
    localStorage.setItem('token', token);
    setIsAuthenticated(true);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
    router.push('/login');
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
```

# Directory: /code/quiz-app/quiz-app-frontend/src/config

## File: api.ts
```ts
// src/config/api.ts
import { OpenAPI } from '@/api';

export const initializeApi = () => {
  OpenAPI.BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
  console.log('API Base URL set to:', OpenAPI.BASE);
};
```

# Directory: /code/quiz-app/quiz-app-frontend/src/utils

## File: api.ts
```ts
import { Configuration, QuestionSetsApi } from '../api';

const getConfig = () => {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
  return new Configuration({
    basePath: 'http://localhost:8000', // Update this to your backend URL
    accessToken: token || undefined,
  });
};

export const questionSetsApi = new QuestionSetsApi(getConfig());

// You can create similar exports for other API services
```

# Directory: /code/quiz-app/quiz-app-frontend/src/api

## File: index.ts
```ts
/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export { ApiError } from './core/ApiError';
export { CancelablePromise, CancelError } from './core/CancelablePromise';
export { OpenAPI } from './core/OpenAPI';
export type { OpenAPIConfig } from './core/OpenAPI';

export type { AnswerChoiceCreateSchema } from './models/AnswerChoiceCreateSchema';
export type { AnswerChoiceSchema } from './models/AnswerChoiceSchema';
export type { Body_login_endpoint_login_post } from './models/Body_login_endpoint_login_post';
export type { Body_upload_question_set_endpoint_upload_questions__post } from './models/Body_upload_question_set_endpoint_upload_questions__post';
export type { GroupSchema } from './models/GroupSchema';
export type { HTTPValidationError } from './models/HTTPValidationError';
export type { LeaderboardSchema } from './models/LeaderboardSchema';
export type { QuestionSchema } from './models/QuestionSchema';
export type { QuestionSetSchema } from './models/QuestionSetSchema';
export type { QuestionTagSchema } from './models/QuestionTagSchema';
export type { QuestionUpdateSchema } from './models/QuestionUpdateSchema';
export type { SubjectCreateSchema } from './models/SubjectCreateSchema';
export type { SubjectSchema } from './models/SubjectSchema';
export { TimePeriodModel } from './models/TimePeriodModel';
export type { TokenSchema } from './models/TokenSchema';
export type { TopicCreateSchema } from './models/TopicCreateSchema';
export type { TopicSchema } from './models/TopicSchema';
export type { UserCreateSchema } from './models/UserCreateSchema';
export type { UserResponseSchema } from './models/UserResponseSchema';
export type { UserSchema } from './models/UserSchema';
export type { ValidationError } from './models/ValidationError';

export { AuthenticationService } from './services/AuthenticationService';
export { DefaultService } from './services/DefaultService';
export { FiltersService } from './services/FiltersService';
export { GroupsService } from './services/GroupsService';
export { LeaderboardService } from './services/LeaderboardService';
export { QuestionService } from './services/QuestionService';
export { QuestionsService } from './services/QuestionsService';
export { QuestionSetsService } from './services/QuestionSetsService';
export { SubjectsService } from './services/SubjectsService';
export { TopicsService } from './services/TopicsService';
export { UserManagementService } from './services/UserManagementService';
export { UserResponsesService } from './services/UserResponsesService';

```

# Directory: /code/quiz-app/quiz-app-frontend/src/api/services

## File: AuthenticationService.ts
```ts
/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_login_endpoint_login_post } from '../models/Body_login_endpoint_login_post';
import type { TokenSchema } from '../models/TokenSchema';
import type { UserCreateSchema } from '../models/UserCreateSchema';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class AuthenticationService {
    /**
     * Login Endpoint
     * @param formData
     * @returns TokenSchema Successful Response
     * @throws ApiError
     */
    public static loginEndpointLoginPost(
        formData: Body_login_endpoint_login_post,
    ): CancelablePromise<TokenSchema> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/login',
            formData: formData,
            mediaType: 'application/x-www-form-urlencoded',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Logout Endpoint
     * This function logs out a user by adding their token to the revoked tokens list.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static logoutEndpointLogoutPost(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/logout',
        });
    }
    /**
     * Register User
     * Endpoint to register a new user.
     *
     * Args:
     * user: A UserCreate schema object containing the user's registration information.
     * db: A database session dependency injected by FastAPI.
     *
     * Raises:
     * HTTPException: If the username is already registered.
     *
     * Returns:
     * The newly created user object.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static registerUserRegisterPost(
        requestBody: UserCreateSchema,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/register',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}

```

## File: DefaultService.ts
```ts
/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class DefaultService {
    /**
     * Read Root
     * @returns any Successful Response
     * @throws ApiError
     */
    public static readRootGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/',
        });
    }
}

```

## File: FiltersService.ts
```ts
/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { QuestionSchema } from '../models/QuestionSchema';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class FiltersService {
    /**
     * Filter Questions Endpoint
     * This function filters questions based on the provided parameters.
     * Returns a list of questions that match the filters.
     *
     * Parameters:
     * ----------
     * request: Request
     * The request object containing all the parameters.
     * subject: Optional[str]
     * The subject to filter the questions by.
     * topic: Optional[str]
     * The topic to filter the questions by.
     * subtopic: Optional[str]
     * The subtopic to filter the questions by.
     * difficulty: Optional[str]
     * The difficulty level to filter the questions by.
     * tags: Optional[List[str]]
     * The tags to filter the questions by.
     * db: Session
     * The database session.
     * skip: int
     * The number of records to skip.
     * limit: int
     * The maximum number of records to return.
     *
     * Returns:
     * ----------
     * List[QuestionSchema]
     * A list of questions that match the filters.
     * @param subject
     * @param topic
     * @param subtopic
     * @param difficulty
     * @param tags
     * @param skip
     * @param limit
     * @returns QuestionSchema Successful Response
     * @throws ApiError
     */
    public static filterQuestionsEndpointQuestionsFilterGet(
        subject?: (string | null),
        topic?: (string | null),
        subtopic?: (string | null),
        difficulty?: (string | null),
        tags?: (Array<string> | null),
        skip?: number,
        limit: number = 100,
    ): CancelablePromise<Array<QuestionSchema>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/questions/filter',
            query: {
                'subject': subject,
                'topic': topic,
                'subtopic': subtopic,
                'difficulty': difficulty,
                'tags': tags,
                'skip': skip,
                'limit': limit,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}

```

## File: GroupsService.ts
```ts
/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { GroupSchema } from '../models/GroupSchema';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class GroupsService {
    /**
     * Create Group Endpoint
     * @param requestBody
     * @returns GroupSchema Successful Response
     * @throws ApiError
     */
    public static createGroupEndpointGroupsPost(
        requestBody: Record<string, any>,
    ): CancelablePromise<GroupSchema> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/groups',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Group Endpoint
     * @param groupId
     * @returns GroupSchema Successful Response
     * @throws ApiError
     */
    public static getGroupEndpointGroupsGroupIdGet(
        groupId: number,
    ): CancelablePromise<GroupSchema> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/groups/{group_id}',
            path: {
                'group_id': groupId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Group Endpoint
     * @param groupId
     * @param requestBody
     * @returns GroupSchema Successful Response
     * @throws ApiError
     */
    public static updateGroupEndpointGroupsGroupIdPut(
        groupId: number,
        requestBody: Record<string, any>,
    ): CancelablePromise<GroupSchema> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/groups/{group_id}',
            path: {
                'group_id': groupId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Group Endpoint
     * @param groupId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static deleteGroupEndpointGroupsGroupIdDelete(
        groupId: number,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/groups/{group_id}',
            path: {
                'group_id': groupId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}

```

## File: LeaderboardService.ts
```ts
/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { LeaderboardSchema } from '../models/LeaderboardSchema';
import type { TimePeriodModel } from '../models/TimePeriodModel';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class LeaderboardService {
    /**
     * Get Leaderboard
     * @param timePeriod
     * @param groupId
     * @param limit
     * @returns LeaderboardSchema Successful Response
     * @throws ApiError
     */
    public static getLeaderboardLeaderboardGet(
        timePeriod: TimePeriodModel,
        groupId?: number,
        limit: number = 10,
    ): CancelablePromise<Array<LeaderboardSchema>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/leaderboard/',
            query: {
                'time_period': timePeriod,
                'group_id': groupId,
                'limit': limit,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}

```

## File: QuestionService.ts
```ts
/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { QuestionSchema } from '../models/QuestionSchema';
import type { QuestionUpdateSchema } from '../models/QuestionUpdateSchema';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class QuestionService {
    /**
     * Create Question Endpoint
     * @param requestBody
     * @returns QuestionSchema Successful Response
     * @throws ApiError
     */
    public static createQuestionEndpointQuestionPost(
        requestBody: Record<string, any>,
    ): CancelablePromise<QuestionSchema> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/question',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Question Endpoint
     * @param questionId
     * @param requestBody
     * @returns QuestionSchema Successful Response
     * @throws ApiError
     */
    public static getQuestionEndpointQuestionQuestionIdGet(
        questionId: number,
        requestBody: QuestionUpdateSchema,
    ): CancelablePromise<QuestionSchema> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/question/question_id}',
            query: {
                'question_id': questionId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Question Endpoint
     * @param questionId
     * @param requestBody
     * @returns QuestionSchema Successful Response
     * @throws ApiError
     */
    public static updateQuestionEndpointQuestionQuestionIdPut(
        questionId: number,
        requestBody: Record<string, any>,
    ): CancelablePromise<QuestionSchema> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/question/{question_id}',
            path: {
                'question_id': questionId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Question Endpoint
     * @param questionId
     * @returns void
     * @throws ApiError
     */
    public static deleteQuestionEndpointQuestionQuestionIdDelete(
        questionId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/question/{question_id}',
            path: {
                'question_id': questionId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}

```

## File: QuestionSetsService.ts
```ts
/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_upload_question_set_endpoint_upload_questions__post } from '../models/Body_upload_question_set_endpoint_upload_questions__post';
import type { QuestionSetSchema } from '../models/QuestionSetSchema';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class QuestionSetsService {
    /**
     * Upload Question Set Endpoint
     * @param formData
     * @returns any Successful Response
     * @throws ApiError
     */
    public static uploadQuestionSetEndpointUploadQuestionsPost(
        formData: Body_upload_question_set_endpoint_upload_questions__post,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/upload-questions/',
            formData: formData,
            mediaType: 'multipart/form-data',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Read Questions Endpoint
     * @param skip
     * @param limit
     * @returns QuestionSetSchema Successful Response
     * @throws ApiError
     */
    public static readQuestionsEndpointQuestionSetGet(
        skip?: number,
        limit: number = 100,
    ): CancelablePromise<Array<QuestionSetSchema>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/question-set/',
            query: {
                'skip': skip,
                'limit': limit,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Create Question Set Endpoint
     * @param requestBody
     * @returns QuestionSetSchema Successful Response
     * @throws ApiError
     */
    public static createQuestionSetEndpointQuestionSetsPost(
        requestBody: Record<string, any>,
    ): CancelablePromise<QuestionSetSchema> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/question-sets/',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Read Question Sets Endpoint
     * @param skip
     * @param limit
     * @returns QuestionSetSchema Successful Response
     * @throws ApiError
     */
    public static readQuestionSetsEndpointQuestionSetsGet(
        skip?: number,
        limit: number = 100,
    ): CancelablePromise<Array<QuestionSetSchema>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/question-sets/',
            query: {
                'skip': skip,
                'limit': limit,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Question Set Endpoint
     * @param questionSetId
     * @returns QuestionSetSchema Successful Response
     * @throws ApiError
     */
    public static getQuestionSetEndpointQuestionSetsQuestionSetIdGet(
        questionSetId: number,
    ): CancelablePromise<QuestionSetSchema> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/question-sets/{question_set_id}',
            path: {
                'question_set_id': questionSetId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Question Set Endpoint
     * @param questionSetId
     * @param requestBody
     * @returns QuestionSetSchema Successful Response
     * @throws ApiError
     */
    public static updateQuestionSetEndpointQuestionSetsQuestionSetIdPut(
        questionSetId: number,
        requestBody: Record<string, any>,
    ): CancelablePromise<QuestionSetSchema> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/question-sets/{question_set_id}',
            path: {
                'question_set_id': questionSetId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Question Set Endpoint
     * @param questionSetId
     * @returns void
     * @throws ApiError
     */
    public static deleteQuestionSetEndpointQuestionSetsQuestionSetIdDelete(
        questionSetId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/question-sets/{question_set_id}',
            path: {
                'question_set_id': questionSetId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}

```

## File: QuestionsService.ts
```ts
/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { QuestionSchema } from '../models/QuestionSchema';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class QuestionsService {
    /**
     * Get Questions Endpoint
     * @param skip
     * @param limit
     * @returns QuestionSchema Successful Response
     * @throws ApiError
     */
    public static getQuestionsEndpointQuestionsGet(
        skip?: number,
        limit: number = 100,
    ): CancelablePromise<Array<QuestionSchema>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/questions/',
            query: {
                'skip': skip,
                'limit': limit,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}

```

## File: SubjectsService.ts
```ts
/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SubjectCreateSchema } from '../models/SubjectCreateSchema';
import type { SubjectSchema } from '../models/SubjectSchema';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class SubjectsService {
    /**
     * Create Subject Endpoint
     * Create a new subject.
     *
     * Args:
     * subject (SubjectCreateSchema): The subject data to be created.
     * db (Session, optional): The database session. Defaults to Depends(get_db).
     *
     * Returns:
     * SubjectSchema: The created subject.
     * @param requestBody
     * @returns SubjectSchema Successful Response
     * @throws ApiError
     */
    public static createSubjectEndpointSubjectsPost(
        requestBody: SubjectCreateSchema,
    ): CancelablePromise<SubjectSchema> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/subjects/',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Read Subject Endpoint
     * Read a subject by ID.
     *
     * Args:
     * subject_id (int): The ID of the subject to be read.
     * db (Session, optional): The database session. Defaults to Depends(get_db).
     *
     * Returns:
     * SubjectSchema: The read subject.
     *
     * Raises:
     * HTTPException: If the subject is not found.
     * @param subjectId
     * @returns SubjectSchema Successful Response
     * @throws ApiError
     */
    public static readSubjectEndpointSubjectsSubjectIdGet(
        subjectId: number,
    ): CancelablePromise<SubjectSchema> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/subjects/{subject_id}',
            path: {
                'subject_id': subjectId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Subject Endpoint
     * Update a subject by ID.
     *
     * Args:
     * subject_id (int): The ID of the subject to be updated.
     * subject (SubjectCreateSchema): The updated subject data.
     * db (Session, optional): The database session. Defaults to Depends(get_db).
     *
     * Returns:
     * SubjectSchema: The updated subject.
     *
     * Raises:
     * HTTPException: If the subject is not found.
     * @param subjectId
     * @param requestBody
     * @returns SubjectSchema Successful Response
     * @throws ApiError
     */
    public static updateSubjectEndpointSubjectsSubjectIdPut(
        subjectId: number,
        requestBody: SubjectCreateSchema,
    ): CancelablePromise<SubjectSchema> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/subjects/{subject_id}',
            path: {
                'subject_id': subjectId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Subject Endpoint
     * Delete a subject by ID.
     *
     * Args:
     * subject_id (int): The ID of the subject to be deleted.
     * db (Session, optional): The database session. Defaults to Depends(get_db).
     *
     * Raises:
     * HTTPException: If the subject is not found.
     * @param subjectId
     * @returns void
     * @throws ApiError
     */
    public static deleteSubjectEndpointSubjectsSubjectIdDelete(
        subjectId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/subjects/{subject_id}',
            path: {
                'subject_id': subjectId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}

```

## File: TopicsService.ts
```ts
/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { TopicCreateSchema } from '../models/TopicCreateSchema';
import type { TopicSchema } from '../models/TopicSchema';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class TopicsService {
    /**
     * Create Topic Endpoint
     * Create a new topic.
     *
     * Args:
     * topic (TopicCreateSchema): The topic data to be created.
     * db (Session, optional): The database session. Defaults to Depends(get_db).
     *
     * Returns:
     * TopicSchema: The created topic.
     * @param requestBody
     * @returns TopicSchema Successful Response
     * @throws ApiError
     */
    public static createTopicEndpointTopicsPost(
        requestBody: TopicCreateSchema,
    ): CancelablePromise<TopicSchema> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/topics/',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Read Topic Endpoint
     * Read a topic by its ID.
     *
     * Args:
     * topic_id (int): The ID of the topic to be read.
     * db (Session, optional): The database session. Defaults to Depends(get_db).
     *
     * Returns:
     * TopicSchema: The read topic.
     *
     * Raises:
     * HTTPException: If the topic is not found.
     * @param topicId
     * @returns TopicSchema Successful Response
     * @throws ApiError
     */
    public static readTopicEndpointTopicsTopicIdGet(
        topicId: number,
    ): CancelablePromise<TopicSchema> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/topics/{topic_id}',
            path: {
                'topic_id': topicId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Topic Endpoint
     * Update a topic by its ID.
     *
     * Args:
     * topic_id (int): The ID of the topic to be updated.
     * topic (TopicCreateSchema): The updated topic data.
     * db (Session, optional): The database session. Defaults to Depends(get_db).
     *
     * Returns:
     * TopicSchema: The updated topic.
     *
     * Raises:
     * HTTPException: If the topic is not found.
     * @param topicId
     * @param requestBody
     * @returns TopicSchema Successful Response
     * @throws ApiError
     */
    public static updateTopicEndpointTopicsTopicIdPut(
        topicId: number,
        requestBody: TopicCreateSchema,
    ): CancelablePromise<TopicSchema> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/topics/{topic_id}',
            path: {
                'topic_id': topicId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Topic Endpoint
     * Delete a topic by its ID.
     *
     * Args:
     * topic_id (int): The ID of the topic to be deleted.
     * db (Session, optional): The database session. Defaults to Depends(get_db).
     *
     * Raises:
     * HTTPException: If the topic is not found.
     * @param topicId
     * @returns void
     * @throws ApiError
     */
    public static deleteTopicEndpointTopicsTopicIdDelete(
        topicId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/topics/{topic_id}',
            path: {
                'topic_id': topicId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}

```

## File: UserManagementService.ts
```ts
/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { UserSchema } from '../models/UserSchema';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class UserManagementService {
    /**
     * Read Users
     * @returns UserSchema Successful Response
     * @throws ApiError
     */
    public static readUsersUsersGet(): CancelablePromise<Array<UserSchema>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/users/',
        });
    }
    /**
     * Create User
     * @param requestBody
     * @returns UserSchema Successful Response
     * @throws ApiError
     */
    public static createUserUsersPost(
        requestBody: Record<string, any>,
    ): CancelablePromise<UserSchema> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/users/',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Read User Me
     * @returns UserSchema Successful Response
     * @throws ApiError
     */
    public static readUserMeUsersMeGet(): CancelablePromise<UserSchema> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/users/me',
        });
    }
    /**
     * Update User Me
     * @param requestBody
     * @returns UserSchema Successful Response
     * @throws ApiError
     */
    public static updateUserMeUsersMePut(
        requestBody: Record<string, any>,
    ): CancelablePromise<UserSchema> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/users/me',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}

```

## File: UserResponsesService.ts
```ts
/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { UserResponseSchema } from '../models/UserResponseSchema';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class UserResponsesService {
    /**
     * Create User Response Endpoint
     * @param requestBody
     * @returns UserResponseSchema Successful Response
     * @throws ApiError
     */
    public static createUserResponseEndpointUserResponsesPost(
        requestBody: Record<string, any>,
    ): CancelablePromise<UserResponseSchema> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/user-responses/',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get User Responses Endpoint
     * @param userId
     * @param questionId
     * @param startTime
     * @param endTime
     * @param skip
     * @param limit
     * @returns UserResponseSchema Successful Response
     * @throws ApiError
     */
    public static getUserResponsesEndpointUserResponsesGet(
        userId?: (number | null),
        questionId?: (number | null),
        startTime?: (string | null),
        endTime?: (string | null),
        skip?: number,
        limit: number = 100,
    ): CancelablePromise<Array<UserResponseSchema>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/user-responses/',
            query: {
                'user_id': userId,
                'question_id': questionId,
                'start_time': startTime,
                'end_time': endTime,
                'skip': skip,
                'limit': limit,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get User Response Endpoint
     * @param userResponseId
     * @returns UserResponseSchema Successful Response
     * @throws ApiError
     */
    public static getUserResponseEndpointUserResponsesUserResponseIdGet(
        userResponseId: number,
    ): CancelablePromise<UserResponseSchema> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/user-responses/{user_response_id}',
            path: {
                'user_response_id': userResponseId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update User Response Endpoint
     * @param userResponseId
     * @param requestBody
     * @returns UserResponseSchema Successful Response
     * @throws ApiError
     */
    public static updateUserResponseEndpointUserResponsesUserResponseIdPut(
        userResponseId: number,
        requestBody: Record<string, any>,
    ): CancelablePromise<UserResponseSchema> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/user-responses/{user_response_id}',
            path: {
                'user_response_id': userResponseId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete User Response Endpoint
     * @param userResponseId
     * @returns void
     * @throws ApiError
     */
    public static deleteUserResponseEndpointUserResponsesUserResponseIdDelete(
        userResponseId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/user-responses/{user_response_id}',
            path: {
                'user_response_id': userResponseId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}

```

# Directory: /code/quiz-app/quiz-app-frontend/src/api/models

## File: AnswerChoiceCreateSchema.ts
```ts
/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type AnswerChoiceCreateSchema = {
    text: string;
    is_correct: boolean;
    explanation: string;
};


```

## File: AnswerChoiceSchema.ts
```ts
/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type AnswerChoiceSchema = {
    id: number;
    text: string;
    is_correct: boolean;
    explanation: string;
};


```

## File: Body_login_endpoint_login_post.ts
```ts
/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type Body_login_endpoint_login_post = {
    grant_type?: (string | null);
    username: string;
    password: string;
    scope?: string;
    client_id?: (string | null);
    client_secret?: (string | null);
};


```

## File: Body_upload_question_set_endpoint_upload_questions__post.ts
```ts
/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type Body_upload_question_set_endpoint_upload_questions__post = {
    file: Blob;
    question_set_name: string;
};


```

## File: GroupSchema.ts
```ts
/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type GroupSchema = {
    name: string;
    creator_id: number;
    description?: (string | null);
    id: number;
};


```

## File: HTTPValidationError.ts
```ts
/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ValidationError } from './ValidationError';
export type HTTPValidationError = {
    detail?: Array<ValidationError>;
};


```

## File: LeaderboardSchema.ts
```ts
/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { TimePeriodModel } from './TimePeriodModel';
export type LeaderboardSchema = {
    id: number;
    user_id: number;
    score: number;
    time_period: TimePeriodModel;
    group_id?: (number | null);
};


```

## File: QuestionSchema.ts
```ts
/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AnswerChoiceSchema } from './AnswerChoiceSchema';
import type { QuestionTagSchema } from './QuestionTagSchema';
export type QuestionSchema = {
    text: string;
    subject_id: number;
    topic_id: number;
    subtopic_id: number;
    id: number;
    difficulty?: (string | null);
    tags?: (Array<QuestionTagSchema> | null);
    answer_choices?: Array<AnswerChoiceSchema>;
    question_set_ids?: (Array<number> | null);
};


```

## File: QuestionSetSchema.ts
```ts
/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type QuestionSetSchema = {
    name: string;
    is_public?: boolean;
    question_ids?: (Array<number> | null);
    creator_id?: number;
    group_ids?: (Array<number> | null);
    id: number;
};


```

## File: QuestionTagSchema.ts
```ts
/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type QuestionTagSchema = {
    tag: string;
    id: number;
};


```

## File: QuestionUpdateSchema.ts
```ts
/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AnswerChoiceCreateSchema } from './AnswerChoiceCreateSchema';
import type { QuestionTagSchema } from './QuestionTagSchema';
export type QuestionUpdateSchema = {
    /**
     * The text of the question
     */
    text?: (string | null);
    /**
     * ID of the subject associated with the question
     */
    subject_id?: (number | null);
    /**
     * ID of the topic associated with the question
     */
    topic_id?: (number | null);
    /**
     * ID of the subtopic associated with the question
     */
    subtopic_id?: (number | null);
    /**
     * The difficulty level of the question
     */
    difficulty?: (string | null);
    /**
     * A list of answer choices
     */
    answer_choices?: (Array<AnswerChoiceCreateSchema> | null);
    /**
     * A list of tags associated with the question
     */
    tags?: (Array<QuestionTagSchema> | null);
    /**
     * Updated list of question set IDs the question belongs to
     */
    question_set_ids?: (Array<number> | null);
};


```

## File: SubjectCreateSchema.ts
```ts
/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type SubjectCreateSchema = {
    name: string;
};


```

## File: SubjectSchema.ts
```ts
/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type SubjectSchema = {
    name: string;
    id: number;
};


```

## File: TimePeriodModel.ts
```ts
/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export enum TimePeriodModel {
    DAILY = 'daily',
    WEEKLY = 'weekly',
    MONTHLY = 'monthly',
    YEARLY = 'yearly',
}

```

## File: TokenSchema.ts
```ts
/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type TokenSchema = {
    access_token: string;
    token_type: string;
};


```

## File: TopicCreateSchema.ts
```ts
/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type TopicCreateSchema = {
    name: string;
    subject_id: number;
};


```

## File: TopicSchema.ts
```ts
/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type TopicSchema = {
    name: string;
    subject_id: number;
    id: number;
};


```

## File: UserCreateSchema.ts
```ts
/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type UserCreateSchema = {
    username: string;
    email: string;
    role?: (string | null);
    password: string;
};


```

## File: UserResponseSchema.ts
```ts
/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type UserResponseSchema = {
    user_id: number;
    question_id: number;
    answer_choice_id: number;
    is_correct?: (boolean | null);
    timestamp: string;
    id: number;
};


```

## File: UserSchema.ts
```ts
/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { GroupSchema } from './GroupSchema';
import type { QuestionSetSchema } from './QuestionSetSchema';
export type UserSchema = {
    username: string;
    email: string;
    role: string;
    id: number;
    is_active: boolean;
    is_admin: boolean;
    group_ids?: Array<GroupSchema>;
    created_groups?: Array<GroupSchema>;
    created_question_sets?: Array<QuestionSetSchema>;
};


```

## File: ValidationError.ts
```ts
/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type ValidationError = {
    loc: Array<(string | number)>;
    msg: string;
    type: string;
};


```

# Directory: /code/quiz-app/quiz-app-frontend/src/api/core

## File: ApiError.ts
```ts
/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ApiRequestOptions } from './ApiRequestOptions';
import type { ApiResult } from './ApiResult';

export class ApiError extends Error {
    public readonly url: string;
    public readonly status: number;
    public readonly statusText: string;
    public readonly body: any;
    public readonly request: ApiRequestOptions;

    constructor(request: ApiRequestOptions, response: ApiResult, message: string) {
        super(message);

        this.name = 'ApiError';
        this.url = response.url;
        this.status = response.status;
        this.statusText = response.statusText;
        this.body = response.body;
        this.request = request;
    }
}

```

## File: ApiRequestOptions.ts
```ts
/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type ApiRequestOptions = {
    readonly method: 'GET' | 'PUT' | 'POST' | 'DELETE' | 'OPTIONS' | 'HEAD' | 'PATCH';
    readonly url: string;
    readonly path?: Record<string, any>;
    readonly cookies?: Record<string, any>;
    readonly headers?: Record<string, any>;
    readonly query?: Record<string, any>;
    readonly formData?: Record<string, any>;
    readonly body?: any;
    readonly mediaType?: string;
    readonly responseHeader?: string;
    readonly errors?: Record<number, string>;
};

```

## File: ApiResult.ts
```ts
/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type ApiResult = {
    readonly url: string;
    readonly ok: boolean;
    readonly status: number;
    readonly statusText: string;
    readonly body: any;
};

```

## File: CancelablePromise.ts
```ts
/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export class CancelError extends Error {

    constructor(message: string) {
        super(message);
        this.name = 'CancelError';
    }

    public get isCancelled(): boolean {
        return true;
    }
}

export interface OnCancel {
    readonly isResolved: boolean;
    readonly isRejected: boolean;
    readonly isCancelled: boolean;

    (cancelHandler: () => void): void;
}

export class CancelablePromise<T> implements Promise<T> {
    #isResolved: boolean;
    #isRejected: boolean;
    #isCancelled: boolean;
    readonly #cancelHandlers: (() => void)[];
    readonly #promise: Promise<T>;
    #resolve?: (value: T | PromiseLike<T>) => void;
    #reject?: (reason?: any) => void;

    constructor(
        executor: (
            resolve: (value: T | PromiseLike<T>) => void,
            reject: (reason?: any) => void,
            onCancel: OnCancel
        ) => void
    ) {
        this.#isResolved = false;
        this.#isRejected = false;
        this.#isCancelled = false;
        this.#cancelHandlers = [];
        this.#promise = new Promise<T>((resolve, reject) => {
            this.#resolve = resolve;
            this.#reject = reject;

            const onResolve = (value: T | PromiseLike<T>): void => {
                if (this.#isResolved || this.#isRejected || this.#isCancelled) {
                    return;
                }
                this.#isResolved = true;
                if (this.#resolve) this.#resolve(value);
            };

            const onReject = (reason?: any): void => {
                if (this.#isResolved || this.#isRejected || this.#isCancelled) {
                    return;
                }
                this.#isRejected = true;
                if (this.#reject) this.#reject(reason);
            };

            const onCancel = (cancelHandler: () => void): void => {
                if (this.#isResolved || this.#isRejected || this.#isCancelled) {
                    return;
                }
                this.#cancelHandlers.push(cancelHandler);
            };

            Object.defineProperty(onCancel, 'isResolved', {
                get: (): boolean => this.#isResolved,
            });

            Object.defineProperty(onCancel, 'isRejected', {
                get: (): boolean => this.#isRejected,
            });

            Object.defineProperty(onCancel, 'isCancelled', {
                get: (): boolean => this.#isCancelled,
            });

            return executor(onResolve, onReject, onCancel as OnCancel);
        });
    }

    get [Symbol.toStringTag]() {
        return "Cancellable Promise";
    }

    public then<TResult1 = T, TResult2 = never>(
        onFulfilled?: ((value: T) => TResult1 | PromiseLike<TResult1>) | null,
        onRejected?: ((reason: any) => TResult2 | PromiseLike<TResult2>) | null
    ): Promise<TResult1 | TResult2> {
        return this.#promise.then(onFulfilled, onRejected);
    }

    public catch<TResult = never>(
        onRejected?: ((reason: any) => TResult | PromiseLike<TResult>) | null
    ): Promise<T | TResult> {
        return this.#promise.catch(onRejected);
    }

    public finally(onFinally?: (() => void) | null): Promise<T> {
        return this.#promise.finally(onFinally);
    }

    public cancel(): void {
        if (this.#isResolved || this.#isRejected || this.#isCancelled) {
            return;
        }
        this.#isCancelled = true;
        if (this.#cancelHandlers.length) {
            try {
                for (const cancelHandler of this.#cancelHandlers) {
                    cancelHandler();
                }
            } catch (error) {
                console.warn('Cancellation threw an error', error);
                return;
            }
        }
        this.#cancelHandlers.length = 0;
        if (this.#reject) this.#reject(new CancelError('Request aborted'));
    }

    public get isCancelled(): boolean {
        return this.#isCancelled;
    }
}

```

## File: OpenAPI.ts
```ts
/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ApiRequestOptions } from './ApiRequestOptions';

type Resolver<T> = (options: ApiRequestOptions) => Promise<T>;
type Headers = Record<string, string>;

export type OpenAPIConfig = {
    BASE: string;
    VERSION: string;
    WITH_CREDENTIALS: boolean;
    CREDENTIALS: 'include' | 'omit' | 'same-origin';
    TOKEN?: string | Resolver<string> | undefined;
    USERNAME?: string | Resolver<string> | undefined;
    PASSWORD?: string | Resolver<string> | undefined;
    HEADERS?: Headers | Resolver<Headers> | undefined;
    ENCODE_PATH?: ((path: string) => string) | undefined;
};

export const OpenAPI: OpenAPIConfig = {
    BASE: '',
    VERSION: '0.1.0',
    WITH_CREDENTIALS: false,
    CREDENTIALS: 'include',
    TOKEN: undefined,
    USERNAME: undefined,
    PASSWORD: undefined,
    HEADERS: undefined,
    ENCODE_PATH: undefined,
};

```

## File: request.ts
```ts
/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import axios from 'axios';
import type { AxiosError, AxiosRequestConfig, AxiosResponse, AxiosInstance } from 'axios';
import FormData from 'form-data';

import { ApiError } from './ApiError';
import type { ApiRequestOptions } from './ApiRequestOptions';
import type { ApiResult } from './ApiResult';
import { CancelablePromise } from './CancelablePromise';
import type { OnCancel } from './CancelablePromise';
import type { OpenAPIConfig } from './OpenAPI';

export const isDefined = <T>(value: T | null | undefined): value is Exclude<T, null | undefined> => {
    return value !== undefined && value !== null;
};

export const isString = (value: any): value is string => {
    return typeof value === 'string';
};

export const isStringWithValue = (value: any): value is string => {
    return isString(value) && value !== '';
};

export const isBlob = (value: any): value is Blob => {
    return (
        typeof value === 'object' &&
        typeof value.type === 'string' &&
        typeof value.stream === 'function' &&
        typeof value.arrayBuffer === 'function' &&
        typeof value.constructor === 'function' &&
        typeof value.constructor.name === 'string' &&
        /^(Blob|File)$/.test(value.constructor.name) &&
        /^(Blob|File)$/.test(value[Symbol.toStringTag])
    );
};

export const isFormData = (value: any): value is FormData => {
    return value instanceof FormData;
};

export const isSuccess = (status: number): boolean => {
    return status >= 200 && status < 300;
};

export const base64 = (str: string): string => {
    try {
        return btoa(str);
    } catch (err) {
        // @ts-ignore
        return Buffer.from(str).toString('base64');
    }
};

export const getQueryString = (params: Record<string, any>): string => {
    const qs: string[] = [];

    const append = (key: string, value: any) => {
        qs.push(`${encodeURIComponent(key)}=${encodeURIComponent(String(value))}`);
    };

    const process = (key: string, value: any) => {
        if (isDefined(value)) {
            if (Array.isArray(value)) {
                value.forEach(v => {
                    process(key, v);
                });
            } else if (typeof value === 'object') {
                Object.entries(value).forEach(([k, v]) => {
                    process(`${key}[${k}]`, v);
                });
            } else {
                append(key, value);
            }
        }
    };

    Object.entries(params).forEach(([key, value]) => {
        process(key, value);
    });

    if (qs.length > 0) {
        return `?${qs.join('&')}`;
    }

    return '';
};

const getUrl = (config: OpenAPIConfig, options: ApiRequestOptions): string => {
    const encoder = config.ENCODE_PATH || encodeURI;

    const path = options.url
        .replace('{api-version}', config.VERSION)
        .replace(/{(.*?)}/g, (substring: string, group: string) => {
            if (options.path?.hasOwnProperty(group)) {
                return encoder(String(options.path[group]));
            }
            return substring;
        });

    const url = `${config.BASE}${path}`;
    if (options.query) {
        return `${url}${getQueryString(options.query)}`;
    }
    return url;
};

export const getFormData = (options: ApiRequestOptions): FormData | undefined => {
    if (options.formData) {
        const formData = new FormData();

        const process = (key: string, value: any) => {
            if (isString(value) || isBlob(value)) {
                formData.append(key, value);
            } else {
                formData.append(key, JSON.stringify(value));
            }
        };

        Object.entries(options.formData)
            .filter(([_, value]) => isDefined(value))
            .forEach(([key, value]) => {
                if (Array.isArray(value)) {
                    value.forEach(v => process(key, v));
                } else {
                    process(key, value);
                }
            });

        return formData;
    }
    return undefined;
};

type Resolver<T> = (options: ApiRequestOptions) => Promise<T>;

export const resolve = async <T>(options: ApiRequestOptions, resolver?: T | Resolver<T>): Promise<T | undefined> => {
    if (typeof resolver === 'function') {
        return (resolver as Resolver<T>)(options);
    }
    return resolver;
};

export const getHeaders = async (config: OpenAPIConfig, options: ApiRequestOptions, formData?: FormData): Promise<Record<string, string>> => {
    const [token, username, password, additionalHeaders] = await Promise.all([
        resolve(options, config.TOKEN),
        resolve(options, config.USERNAME),
        resolve(options, config.PASSWORD),
        resolve(options, config.HEADERS),
    ]);

    const formHeaders = typeof formData?.getHeaders === 'function' && formData?.getHeaders() || {}

    const headers = Object.entries({
        Accept: 'application/json',
        ...additionalHeaders,
        ...options.headers,
        ...formHeaders,
    })
    .filter(([_, value]) => isDefined(value))
    .reduce((headers, [key, value]) => ({
        ...headers,
        [key]: String(value),
    }), {} as Record<string, string>);

    if (isStringWithValue(token)) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    if (isStringWithValue(username) && isStringWithValue(password)) {
        const credentials = base64(`${username}:${password}`);
        headers['Authorization'] = `Basic ${credentials}`;
    }

    if (options.body !== undefined) {
        if (options.mediaType) {
            headers['Content-Type'] = options.mediaType;
        } else if (isBlob(options.body)) {
            headers['Content-Type'] = options.body.type || 'application/octet-stream';
        } else if (isString(options.body)) {
            headers['Content-Type'] = 'text/plain';
        } else if (!isFormData(options.body)) {
            headers['Content-Type'] = 'application/json';
        }
    }

    return headers;
};

export const getRequestBody = (options: ApiRequestOptions): any => {
    if (options.body) {
        return options.body;
    }
    return undefined;
};

export const sendRequest = async <T>(
    config: OpenAPIConfig,
    options: ApiRequestOptions,
    url: string,
    body: any,
    formData: FormData | undefined,
    headers: Record<string, string>,
    onCancel: OnCancel,
    axiosClient: AxiosInstance
): Promise<AxiosResponse<T>> => {
    const source = axios.CancelToken.source();

    const requestConfig: AxiosRequestConfig = {
        url,
        headers,
        data: body ?? formData,
        method: options.method,
        withCredentials: config.WITH_CREDENTIALS,
        withXSRFToken: config.CREDENTIALS === 'include' ? config.WITH_CREDENTIALS : false,
        cancelToken: source.token,
    };

    onCancel(() => source.cancel('The user aborted a request.'));

    try {
        return await axiosClient.request(requestConfig);
    } catch (error) {
        const axiosError = error as AxiosError<T>;
        if (axiosError.response) {
            return axiosError.response;
        }
        throw error;
    }
};

export const getResponseHeader = (response: AxiosResponse<any>, responseHeader?: string): string | undefined => {
    if (responseHeader) {
        const content = response.headers[responseHeader];
        if (isString(content)) {
            return content;
        }
    }
    return undefined;
};

export const getResponseBody = (response: AxiosResponse<any>): any => {
    if (response.status !== 204) {
        return response.data;
    }
    return undefined;
};

export const catchErrorCodes = (options: ApiRequestOptions, result: ApiResult): void => {
    const errors: Record<number, string> = {
        400: 'Bad Request',
        401: 'Unauthorized',
        403: 'Forbidden',
        404: 'Not Found',
        500: 'Internal Server Error',
        502: 'Bad Gateway',
        503: 'Service Unavailable',
        ...options.errors,
    }

    const error = errors[result.status];
    if (error) {
        throw new ApiError(options, result, error);
    }

    if (!result.ok) {
        const errorStatus = result.status ?? 'unknown';
        const errorStatusText = result.statusText ?? 'unknown';
        const errorBody = (() => {
            try {
                return JSON.stringify(result.body, null, 2);
            } catch (e) {
                return undefined;
            }
        })();

        throw new ApiError(options, result,
            `Generic Error: status: ${errorStatus}; status text: ${errorStatusText}; body: ${errorBody}`
        );
    }
};

/**
 * Request method
 * @param config The OpenAPI configuration object
 * @param options The request options from the service
 * @param axiosClient The axios client instance to use
 * @returns CancelablePromise<T>
 * @throws ApiError
 */
export const request = <T>(config: OpenAPIConfig, options: ApiRequestOptions, axiosClient: AxiosInstance = axios): CancelablePromise<T> => {
    return new CancelablePromise(async (resolve, reject, onCancel) => {
        try {
            const url = getUrl(config, options);
            const formData = getFormData(options);
            const body = getRequestBody(options);
            const headers = await getHeaders(config, options, formData);

            if (!onCancel.isCancelled) {
                const response = await sendRequest<T>(config, options, url, body, formData, headers, onCancel, axiosClient);
                const responseBody = getResponseBody(response);
                const responseHeader = getResponseHeader(response, options.responseHeader);

                const result: ApiResult = {
                    url,
                    ok: isSuccess(response.status),
                    status: response.status,
                    statusText: response.statusText,
                    body: responseHeader ?? responseBody,
                };

                catchErrorCodes(options, result);

                resolve(result.body);
            }
        } catch (error) {
            reject(error);
        }
    });
};

```

# Directory: /code/quiz-app/quiz-app-frontend/src/components

## File: Layout.tsx
```tsx
import React, { ReactNode } from 'react';
import Link from 'next/link';

type LayoutProps = {
  children: ReactNode;
};

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-blue-600 text-white p-4">
        <nav>
          <ul className="flex space-x-4">
            <li><Link href="/">Home</Link></li>
            <li><Link href="/quizzes">Quizzes</Link></li>
            <li><Link href="/leaderboard">Leaderboard</Link></li>
          </ul>
        </nav>
      </header>
      <main className="flex-grow container mx-auto px-4 py-8">
        {children}
      </main>
      <footer className="bg-gray-200 p-4 text-center">
        © 2023 Quiz App
      </footer>
    </div>
  );
};

export default Layout;
```

## File: NavBar.tsx
```tsx
'use client';

import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';

const NavBar = () => {
  const { isAuthenticated, logout } = useAuth();

  return (
    <header className="bg-blue-600 text-white p-4">
      <nav className="container mx-auto">
        <ul className="flex space-x-4">
          <li><Link href="/" className="hover:underline">Home</Link></li>
          <li><Link href="/quizzes" className="hover:underline">Quizzes</Link></li>
          <li><Link href="/leaderboard" className="hover:underline">Leaderboard</Link></li>
          {isAuthenticated ? (
            <li><button onClick={logout} className="hover:underline">Logout</button></li>
          ) : (
            <>
              <li><Link href="/login" className="hover:underline">Login</Link></li>
              <li><Link href="/register" className="hover:underline">Register</Link></li>
            </>
          )}
        </ul>
      </nav>
    </header>
  );
};

export default NavBar;
```

## File: ProtectedRoute.tsx
```tsx
'use client';

import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, router]);

  return isAuthenticated ? <>{children}</> : null;
};

export default ProtectedRoute;
```

## File: QuizList.tsx
```tsx
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
```
