'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Task } from '../../types/index';
import { TaskList } from '../../components/TaskList';
import { TaskForm } from '../../components/TaskForm';
import { taskAPI } from '../../services/api';
import { isAuthenticated, getUserId } from '../../services/auth';

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  // Check authentication on initial load
  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login');
      return;
    }

    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const userId = getUserId();
      if (!userId) {
        throw new Error('User not authenticated');
      }
      const tasks = await taskAPI.getTasks(userId);
      setTasks(tasks);
      setError(null);
    } catch (err: any) {
      if (err.response?.status === 401) {
        // Token might be expired, redirect to login
        router.push('/login');
      } else {
        setError(err.message || 'Failed to fetch tasks');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleTaskCreated = (newTask: Task) => {
    setTasks(prev => [newTask, ...prev]);
  };

  const handleTaskUpdated = (updatedTask: Task) => {
    setTasks(prev => prev.map(task => task.id === updatedTask.id ? updatedTask : task));
  };

  const handleTaskDeleted = (taskId: string) => {
    setTasks(prev => prev.filter(task => task.id !== taskId));
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-4 sm:py-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-white shadow rounded-lg p-4 sm:p-6">
            <h1 className="text-xl sm:text-2xl font-bold text-gray-800 mb-4 sm:mb-6">Loading tasks...</h1>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-4 sm:py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-4 sm:mb-6 gap-2 sm:gap-0">
          <h1 className="text-xl sm:text-2xl font-bold text-gray-800">My Tasks</h1>
          <button
            onClick={() => router.push('/')}
            className="text-blue-600 hover:text-blue-800 text-sm sm:text-base"
          >
            Home
          </button>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <div className="bg-white shadow rounded-lg p-4 sm:p-6 mb-6">
          <TaskForm onTaskCreated={handleTaskCreated} />
        </div>

        <div className="bg-white shadow rounded-lg overflow-hidden">
          <TaskList
            tasks={tasks}
            onTaskUpdated={handleTaskUpdated}
            onTaskDeleted={handleTaskDeleted}
          />
        </div>
      </div>
    </div>
  );
}