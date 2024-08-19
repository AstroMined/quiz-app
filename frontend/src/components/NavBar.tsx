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