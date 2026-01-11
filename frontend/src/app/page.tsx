'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { isAuthenticated } from '../services/auth';

export default function HomePage() {
  const [isAuthenticatedUser, setIsAuthenticatedUser] = useState(false);
  const router = useRouter();

  useEffect(() => {
    setIsAuthenticatedUser(isAuthenticated());
  }, []);

  const handleGetStarted = () => {
    if (isAuthenticatedUser) {
      router.push('/tasks');
    } else {
      router.push('/login');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-purple-900 to-black">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-purple-600/10 to-yellow-600/10"></div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 sm:py-32">
          <div className="text-center">
            <h1 className="text-4xl sm:text-6xl lg:text-7xl font-bold text-white mb-6">
              <span className="bg-gradient-to-r from-purple-400 via-yellow-400 to-red-500 bg-clip-text text-transparent">
                Organize Your Life
              </span>
            </h1>
            <p className="text-xl sm:text-2xl text-gray-300 mb-8 max-w-3xl mx-auto">
              Transform the way you manage tasks with our secure, intuitive, and powerful todo application.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <button
                onClick={handleGetStarted}
                className="px-8 py-4 bg-gradient-to-r from-purple-600 to-yellow-600 text-white font-semibold rounded-lg hover:from-purple-700 hover:to-yellow-700 transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-purple-500/25"
              >
                {isAuthenticatedUser ? 'Go to Tasks' : 'Get Started'}
              </button>

              <Link
                href="/tasks"
                className="px-8 py-4 bg-transparent border-2 border-purple-600 text-purple-400 font-semibold rounded-lg hover:bg-purple-600 hover:text-white transition-all duration-300"
              >
                View Demo
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-black/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
              Powerful Features
            </h2>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto">
              Everything you need to stay organized and productive
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="bg-gradient-to-br from-purple-900/30 to-black/50 p-8 rounded-xl border border-purple-500/20 hover:border-purple-500/40 transition-all duration-300">
              <div className="w-12 h-12 bg-gradient-to-r from-purple-600 to-purple-800 rounded-lg flex items-center justify-center mb-6">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-white mb-4">Smart Task Management</h3>
              <p className="text-gray-300">
                Organize your tasks efficiently with smart categorization and priority levels.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="bg-gradient-to-br from-yellow-900/30 to-black/50 p-8 rounded-xl border border-yellow-500/20 hover:border-yellow-500/40 transition-all duration-300">
              <div className="w-12 h-12 bg-gradient-to-r from-yellow-600 to-yellow-800 rounded-lg flex items-center justify-center mb-6">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-white mb-4">Secure & Private</h3>
              <p className="text-gray-300">
                Your data is protected with industry-standard security and encryption.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="bg-gradient-to-br from-red-900/30 to-black/50 p-8 rounded-xl border border-red-500/20 hover:border-red-500/40 transition-all duration-300">
              <div className="w-12 h-12 bg-gradient-to-r from-red-600 to-red-800 rounded-lg flex items-center justify-center mb-6">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-white mb-4">Lightning Fast</h3>
              <p className="text-gray-300">
                Experience blazing fast performance with our optimized platform.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-4xl sm:text-5xl font-bold text-purple-400 mb-2">10K+</div>
              <div className="text-gray-300">Active Users</div>
            </div>
            <div>
              <div className="text-4xl sm:text-5xl font-bold text-yellow-400 mb-2">50K+</div>
              <div className="text-gray-300">Tasks Completed</div>
            </div>
            <div>
              <div className="text-4xl sm:text-5xl font-bold text-red-400 mb-2">99%</div>
              <div className="text-gray-300">Uptime</div>
            </div>
            <div>
              <div className="text-4xl sm:text-5xl font-bold text-white mb-2">24/7</div>
              <div className="text-gray-300">Support</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-purple-900/20 to-yellow-900/20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-6">
            Ready to Transform Your Productivity?
          </h2>
          <p className="text-xl text-gray-300 mb-8">
            Join thousands of users who trust our platform to manage their daily tasks and achieve their goals.
          </p>
          <button
            onClick={handleGetStarted}
            className="px-10 py-4 bg-gradient-to-r from-purple-600 to-yellow-600 text-white font-semibold rounded-lg hover:from-purple-700 hover:to-yellow-700 transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-purple-500/25"
          >
            {isAuthenticatedUser ? 'Go to Dashboard' : 'Start Free Trial'}
          </button>
        </div>
      </section>
    </div>
  );
}