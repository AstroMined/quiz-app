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