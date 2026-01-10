'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated } from '../services/auth';

export default function HomePage() {
  const router = useRouter();

  // Check authentication and redirect accordingly
  useEffect(() => {
    if (isAuthenticated()) {
      // If user is authenticated, redirect to tasks page
      router.push('/tasks');
    } else {
      // If not authenticated, redirect to login
      router.push('/login');
    }
  }, [router]);

  return (
    <div className="min-h-screen bg-gray-50 py-4 sm:py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white shadow rounded-lg p-4 sm:p-6">
          <h1 className="text-xl sm:text-2xl font-bold text-gray-800 mb-4 sm:mb-6">Loading...</h1>
          <p className="text-gray-600">Redirecting to appropriate page...</p>
        </div>
      </div>
    </div>
  );
}