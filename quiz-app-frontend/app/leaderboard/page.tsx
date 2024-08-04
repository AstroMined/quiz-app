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