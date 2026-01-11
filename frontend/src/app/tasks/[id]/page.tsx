'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Task } from '../../../types/index';
import { TaskItem } from '../../../components/TaskItem';
import { taskAPI } from '../../../services/api';
import { isAuthenticated, getUserId } from '../../../services/auth';

export default function TaskDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [task, setTask] = useState<Task | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Check authentication on initial load
  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login');
      return;
    }

    fetchTask();
  }, [id]);

  const fetchTask = async () => {
    try {
      setLoading(true);
      const userId = getUserId();
      if (!userId) {
        throw new Error('User not authenticated');
      }

      const task = await taskAPI.getTask(userId, id);
      setTask(task);
      setError(null);
    } catch (err: any) {
      if (err.response?.status === 401) {
        // Token might be expired, redirect to login
        router.push('/login');
      } else if (err.response?.status === 404) {
        setError('Task not found');
      } else {
        setError(err.message || 'Failed to fetch task');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleTaskUpdated = (updatedTask: Task) => {
    setTask(updatedTask);
  };

  const handleTaskDeleted = () => {
    router.push('/tasks'); // Redirect to task list after deletion
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-2xl mx-auto px-4">
          <div className="bg-white shadow rounded-lg p-6">
            <h1 className="text-2xl font-bold text-gray-800 mb-6">Loading task...</h1>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-2xl mx-auto px-4">
          <div className="bg-white shadow rounded-lg p-6">
            <h1 className="text-2xl font-bold text-gray-800 mb-4">Task not found</h1>
            <p className="text-gray-600 mb-4">{error}</p>
            <button
              onClick={() => router.push('/tasks')}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Back to Tasks
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-4 sm:py-8">
      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center mb-4 sm:mb-6">
          <h1 className="text-xl sm:text-2xl font-bold text-gray-800">Task Details</h1>
          <button
            onClick={() => router.push('/tasks')}
            className="text-blue-600 hover:text-blue-800 text-sm sm:text-base"
          >
            Back to Tasks
          </button>
        </div>

        {task && (
          <div className="bg-white shadow rounded-lg overflow-hidden">
            <div className="p-4 sm:p-6">
              <TaskItem
                task={task}
                onTaskUpdated={handleTaskUpdated}
                onTaskDeleted={handleTaskDeleted}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}