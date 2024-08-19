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