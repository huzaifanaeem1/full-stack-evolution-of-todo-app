'use client';

import { useState } from 'react';
import { Task, PriorityLevel, RecurrenceFrequency } from '@/src/types';
import { taskAPI } from '@/src/services/api';
import { getUserId } from '@/src/services/auth';

interface TaskFormProps {
  onTaskCreated: (task: Task) => void;
}

export const TaskForm = ({ onTaskCreated }: TaskFormProps) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<PriorityLevel>('medium'); // T032: Add priority state
  const [dueDate, setDueDate] = useState(''); // T046: Add due_date state
  const [tags, setTags] = useState<string[]>([]); // T070: Add tags state
  const [tagInput, setTagInput] = useState(''); // T070: Add tag input state
  const [isRecurring, setIsRecurring] = useState(false); // T114: Add recurring state
  const [recurrenceFrequency, setRecurrenceFrequency] = useState<RecurrenceFrequency>('daily'); // T115: Add recurrence frequency state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // T070: Add tag handling functions
  const handleAddTag = () => {
    const trimmedTag = tagInput.trim().toLowerCase();
    if (trimmedTag && !tags.includes(trimmedTag)) {
      setTags([...tags, trimmedTag]);
      setTagInput('');
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setTags(tags.filter(tag => tag !== tagToRemove));
  };

  const handleTagInputKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddTag();
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!title.trim()) {
      setError('Title is required');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const userId = getUserId();
      if (!userId) {
        throw new Error('User not authenticated');
      }

      const newTask = await taskAPI.createTask(userId, {
        title: title.trim(),
        description: description.trim(),
        priority, // T032: Include priority in task creation
        due_date: dueDate || undefined, // T046: Include due_date in task creation
        tags: tags.length > 0 ? tags : undefined, // T070: Include tags in task creation
        is_recurring: isRecurring, // T114: Include is_recurring in task creation
        recurrence_frequency: isRecurring ? recurrenceFrequency : undefined, // T115: Include recurrence_frequency in task creation
      });

      // Optimistic update - immediately update UI with new task
      onTaskCreated(newTask);

      // Reset form
      setTitle('');
      setDescription('');
      setPriority('medium'); // T032: Reset priority to default
      setDueDate(''); // T046: Reset due_date to default
      setTags([]); // T070: Reset tags to default
      setTagInput(''); // T070: Reset tag input to default
      setIsRecurring(false); // T114: Reset recurring to default
      setRecurrenceFrequency('daily'); // T115: Reset recurrence frequency to default
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to create task');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="task-title" className="block text-sm font-medium text-gray-300 mb-1">
          Task Title *
        </label>
        <input
          id="task-title"
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Enter task title..."
          className="w-full px-4 py-3 bg-black/30 border border-purple-500/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent text-white placeholder-gray-500"
          disabled={loading}
        />
      </div>

      <div>
        <label htmlFor="task-description" className="block text-sm font-medium text-gray-300 mb-1">
          Description (Optional)
        </label>
        <textarea
          id="task-description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Enter task description..."
          rows={3}
          className="w-full px-4 py-3 bg-black/30 border border-purple-500/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent text-white placeholder-gray-500"
          disabled={loading}
        />
      </div>

      {/* T032: Add priority dropdown to TaskForm */}
      <div>
        <label htmlFor="task-priority" className="block text-sm font-medium text-gray-300 mb-1">
          Priority
        </label>
        <select
          id="task-priority"
          value={priority}
          onChange={(e) => setPriority(e.target.value as PriorityLevel)}
          className="w-full px-4 py-3 bg-black/30 border border-purple-500/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent text-white"
          disabled={loading}
        >
          <option value="high" className="bg-gray-900">High Priority</option>
          <option value="medium" className="bg-gray-900">Medium Priority</option>
          <option value="low" className="bg-gray-900">Low Priority</option>
        </select>
      </div>

      {/* T046: Add date picker to TaskForm component */}
      <div>
        <label htmlFor="task-due-date" className="block text-sm font-medium text-gray-300 mb-1">
          Due Date (Optional)
        </label>
        <input
          id="task-due-date"
          type="date"
          value={dueDate}
          onChange={(e) => setDueDate(e.target.value)}
          className="w-full px-4 py-3 bg-black/30 border border-purple-500/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent text-white"
          disabled={loading}
        />
      </div>

      {/* T070: Add tag input component to TaskForm */}
      <div>
        <label htmlFor="task-tags" className="block text-sm font-medium text-gray-300 mb-1">
          Tags (Optional)
        </label>
        <div className="flex gap-2">
          <input
            id="task-tags"
            type="text"
            value={tagInput}
            onChange={(e) => setTagInput(e.target.value)}
            onKeyDown={handleTagInputKeyDown}
            placeholder="Enter tag and press Enter..."
            className="flex-1 px-4 py-3 bg-black/30 border border-purple-500/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent text-white placeholder-gray-500"
            disabled={loading}
          />
          <button
            type="button"
            onClick={handleAddTag}
            disabled={loading || !tagInput.trim()}
            className="px-4 py-3 bg-purple-600/30 border border-purple-500/30 rounded-lg hover:bg-purple-600/50 disabled:opacity-50 disabled:cursor-not-allowed text-white transition-all duration-200"
          >
            Add
          </button>
        </div>
        {tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-2">
            {tags.map((tag) => (
              <span
                key={tag}
                className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-purple-900/30 text-purple-300 border border-purple-500/30"
              >
                {tag}
                <button
                  type="button"
                  onClick={() => handleRemoveTag(tag)}
                  disabled={loading}
                  className="ml-2 text-purple-400 hover:text-purple-200 disabled:opacity-50"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        )}
      </div>

      {/* T114: Add recurring checkbox to TaskForm */}
      <div>
        <label className="flex items-center space-x-2 cursor-pointer">
          <input
            type="checkbox"
            checked={isRecurring}
            onChange={(e) => setIsRecurring(e.target.checked)}
            disabled={loading}
            className="h-4 w-4 text-purple-600 rounded focus:ring-purple-500 bg-black/30 border-purple-500/30"
          />
          <span className="text-sm font-medium text-gray-300">Make this a recurring task</span>
        </label>
      </div>

      {/* T115, T116: Add recurrence frequency dropdown, show/hide based on recurring checkbox */}
      {isRecurring && (
        <div>
          <label htmlFor="task-recurrence" className="block text-sm font-medium text-gray-300 mb-1">
            Recurrence Frequency
          </label>
          <select
            id="task-recurrence"
            value={recurrenceFrequency}
            onChange={(e) => setRecurrenceFrequency(e.target.value as RecurrenceFrequency)}
            className="w-full px-4 py-3 bg-black/30 border border-purple-500/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent text-white"
            disabled={loading}
          >
            <option value="daily" className="bg-gray-900">Daily</option>
            <option value="weekly" className="bg-gray-900">Weekly</option>
            <option value="monthly" className="bg-gray-900">Monthly</option>
          </select>
        </div>
      )}

      {error && (
        <div className="bg-red-900/30 border border-red-500/30 text-red-400 px-4 py-3 rounded-lg text-sm">
          {error}
        </div>
      )}

      <div className="flex justify-end pt-2">
        <button
          type="submit"
          disabled={loading}
          className={`px-6 py-3 rounded-lg font-medium transition-all duration-200 ${
            loading
              ? 'bg-gray-600 cursor-not-allowed text-gray-400'
              : 'bg-gradient-to-r from-purple-600 to-yellow-600 text-white hover:from-purple-700 hover:to-yellow-700 shadow-lg hover:shadow-purple-500/25 transform hover:scale-105'
          }`}
        >
          {loading ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Creating...
            </span>
          ) : (
            <span className="flex items-center justify-center">
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              Add Task
            </span>
          )}
        </button>
      </div>
    </form>
  );
};