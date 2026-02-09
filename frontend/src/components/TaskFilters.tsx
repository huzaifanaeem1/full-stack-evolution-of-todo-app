'use client';

import { useState, useEffect } from 'react';
import { PriorityLevel } from '@/src/types';

interface TaskFiltersProps {
  onFiltersChange: (filters: {
    search?: string;
    status?: string;
    priority?: string;
    tags?: string[];
    sort_by?: string;
    sort_order?: string;
  }) => void;
  availableTags: string[];
}

// T087: Create TaskFilters component
export const TaskFilters = ({ onFiltersChange, availableTags }: TaskFiltersProps) => {
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState('all');
  const [priority, setPriority] = useState('');
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [sortBy, setSortBy] = useState('created_at');
  const [sortOrder, setSortOrder] = useState('desc');

  // T088: Add search input with debounce (300ms)
  useEffect(() => {
    const timer = setTimeout(() => {
      emitFilters();
    }, 300);

    return () => clearTimeout(timer);
  }, [search]);

  // Emit filters whenever any filter changes (except search which is debounced)
  useEffect(() => {
    emitFilters();
  }, [status, priority, selectedTags, sortBy, sortOrder]);

  const emitFilters = () => {
    onFiltersChange({
      search: search.trim() || undefined,
      status: status !== 'all' ? status : undefined,
      priority: priority || undefined,
      tags: selectedTags.length > 0 ? selectedTags : undefined,
      sort_by: sortBy,
      sort_order: sortOrder,
    });
  };

  const handleTagToggle = (tag: string) => {
    if (selectedTags.includes(tag)) {
      setSelectedTags(selectedTags.filter(t => t !== tag));
    } else {
      setSelectedTags([...selectedTags, tag]);
    }
  };

  const handleClearFilters = () => {
    setSearch('');
    setStatus('all');
    setPriority('');
    setSelectedTags([]);
    setSortBy('created_at');
    setSortOrder('desc');
  };

  return (
    <div className="bg-gradient-to-br from-purple-900/10 to-black/30 backdrop-blur-sm border border-purple-500/30 rounded-xl p-6 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">Filters & Sort</h3>
        <button
          onClick={handleClearFilters}
          className="text-sm text-purple-400 hover:text-purple-300 transition-colors"
        >
          Clear All
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* T088: Search input with debounce */}
        <div>
          <label htmlFor="search" className="block text-sm font-medium text-gray-300 mb-1">
            Search
          </label>
          <input
            id="search"
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search tasks..."
            className="w-full px-4 py-2 bg-black/30 border border-purple-500/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent text-white placeholder-gray-500"
          />
        </div>

        {/* T089: Status filter dropdown */}
        <div>
          <label htmlFor="status" className="block text-sm font-medium text-gray-300 mb-1">
            Status
          </label>
          <select
            id="status"
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            className="w-full px-4 py-2 bg-black/30 border border-purple-500/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent text-white"
          >
            <option value="all" className="bg-gray-900">All Tasks</option>
            <option value="active" className="bg-gray-900">Active</option>
            <option value="completed" className="bg-gray-900">Completed</option>
          </select>
        </div>

        {/* T090: Priority filter dropdown */}
        <div>
          <label htmlFor="priority" className="block text-sm font-medium text-gray-300 mb-1">
            Priority
          </label>
          <select
            id="priority"
            value={priority}
            onChange={(e) => setPriority(e.target.value)}
            className="w-full px-4 py-2 bg-black/30 border border-purple-500/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent text-white"
          >
            <option value="" className="bg-gray-900">All Priorities</option>
            <option value="high" className="bg-gray-900">High Priority</option>
            <option value="medium" className="bg-gray-900">Medium Priority</option>
            <option value="low" className="bg-gray-900">Low Priority</option>
          </select>
        </div>

        {/* T092: Sort by dropdown */}
        <div>
          <label htmlFor="sortBy" className="block text-sm font-medium text-gray-300 mb-1">
            Sort By
          </label>
          <select
            id="sortBy"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="w-full px-4 py-2 bg-black/30 border border-purple-500/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent text-white"
          >
            <option value="created_at" className="bg-gray-900">Created Date</option>
            <option value="updated_at" className="bg-gray-900">Updated Date</option>
            <option value="due_date" className="bg-gray-900">Due Date</option>
            <option value="priority" className="bg-gray-900">Priority</option>
            <option value="title" className="bg-gray-900">Title</option>
          </select>
        </div>

        {/* T093: Sort order toggle */}
        <div>
          <label htmlFor="sortOrder" className="block text-sm font-medium text-gray-300 mb-1">
            Sort Order
          </label>
          <select
            id="sortOrder"
            value={sortOrder}
            onChange={(e) => setSortOrder(e.target.value)}
            className="w-full px-4 py-2 bg-black/30 border border-purple-500/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent text-white"
          >
            <option value="desc" className="bg-gray-900">Descending</option>
            <option value="asc" className="bg-gray-900">Ascending</option>
          </select>
        </div>
      </div>

      {/* T091: Tag multi-select */}
      {availableTags.length > 0 && (
        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Filter by Tags
          </label>
          <div className="flex flex-wrap gap-2">
            {availableTags.map((tag) => (
              <button
                key={tag}
                onClick={() => handleTagToggle(tag)}
                className={`px-3 py-1 rounded-full text-xs font-medium transition-all duration-200 ${
                  selectedTags.includes(tag)
                    ? 'bg-purple-600 text-white border border-purple-500'
                    : 'bg-purple-900/30 text-purple-300 border border-purple-500/30 hover:bg-purple-900/50'
                }`}
              >
                {tag}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
