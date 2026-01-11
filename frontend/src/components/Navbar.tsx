'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

const Navbar = () => {
  const [scrolled, setScrolled] = useState(false);
  const pathname = usePathname();

  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 10) {
        setScrolled(true);
      } else {
        setScrolled(false);
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const isActive = (path: string) => pathname === path;

  return (
    <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
      scrolled
        ? 'bg-black/90 backdrop-blur-md border-b border-purple-500/20 shadow-lg'
        : 'bg-black/80 backdrop-blur-sm'
    }`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link href="/" className="flex-shrink-0">
            <span className="text-2xl font-bold bg-gradient-to-r from-purple-400 via-yellow-400 to-red-500 bg-clip-text text-transparent">
              TodoApp
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:block">
            <div className="ml-10 flex items-baseline space-x-4">
              <Link
                href="/"
                className={`px-3 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
                  isActive('/')
                    ? 'bg-purple-600 text-white'
                    : 'text-gray-300 hover:bg-purple-600 hover:text-white'
                }`}
              >
                Home
              </Link>
              <Link
                href="/tasks"
                className={`px-3 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
                  isActive('/tasks')
                    ? 'bg-purple-600 text-white'
                    : 'text-gray-300 hover:bg-purple-600 hover:text-white'
                }`}
              >
                My Tasks
              </Link>
              {pathname.startsWith('/tasks/') && pathname !== '/tasks' ? null : (
                <Link
                  href="/tasks"
                  className="px-3 py-2 rounded-md text-sm font-medium text-gray-300 hover:bg-purple-600 hover:text-white transition-all duration-200"
                >
                  Add Task
                </Link>
              )}
              {!pathname.includes('/login') && !pathname.includes('/register') && (
                <>
                  <Link
                    href="/login"
                    className="px-3 py-2 rounded-md text-sm font-medium text-gray-300 hover:bg-purple-600 hover:text-white transition-all duration-200"
                  >
                    Login
                  </Link>
                  <Link
                    href="/register"
                    className="px-3 py-2 rounded-md text-sm font-medium text-gray-300 hover:bg-purple-600 hover:text-white transition-all duration-200"
                  >
                    Register
                  </Link>
                </>
              )}
            </div>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center">
            <MobileMenu />
          </div>
        </div>
      </div>
    </nav>
  );
};

const MobileMenu = () => {
  const [isOpen, setIsOpen] = useState(false);
  const pathname = usePathname();

  const isActive = (path: string) => pathname === path;

  return (
    <>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="text-gray-300 hover:text-white focus:outline-none"
      >
        <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          {isOpen ? (
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          ) : (
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          )}
        </svg>
      </button>

      {isOpen && (
        <div className="absolute top-16 left-0 right-0 bg-black/95 backdrop-blur-md border-b border-purple-500/20 md:hidden z-50">
          <div className="px-2 pt-2 pb-3 space-y-1">
            <Link
              href="/"
              className={`block px-3 py-2 rounded-md text-base font-medium ${
                isActive('/')
                  ? 'bg-purple-600 text-white'
                  : 'text-gray-300 hover:bg-purple-600 hover:text-white'
              }`}
              onClick={() => setIsOpen(false)}
            >
              Home
            </Link>
            <Link
              href="/tasks"
              className={`block px-3 py-2 rounded-md text-base font-medium ${
                isActive('/tasks')
                  ? 'bg-purple-600 text-white'
                  : 'text-gray-300 hover:bg-purple-600 hover:text-white'
              }`}
              onClick={() => setIsOpen(false)}
            >
              My Tasks
            </Link>
            {pathname.startsWith('/tasks/') && pathname !== '/tasks' ? null : (
              <Link
                href="/tasks"
                className="block px-3 py-2 rounded-md text-base font-medium text-gray-300 hover:bg-purple-600 hover:text-white"
                onClick={() => setIsOpen(false)}
              >
                Add Task
              </Link>
            )}
            {!pathname.includes('/login') && !pathname.includes('/register') && (
              <>
                <Link
                  href="/login"
                  className="block px-3 py-2 rounded-md text-base font-medium text-gray-300 hover:bg-purple-600 hover:text-white"
                  onClick={() => setIsOpen(false)}
                >
                  Login
                </Link>
                <Link
                  href="/register"
                  className="block px-3 py-2 rounded-md text-base font-medium text-gray-300 hover:bg-purple-600 hover:text-white"
                  onClick={() => setIsOpen(false)}
                >
                  Register
                </Link>
              </>
            )}
          </div>
        </div>
      )}
    </>
  );
};

export default Navbar;