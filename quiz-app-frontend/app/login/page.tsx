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