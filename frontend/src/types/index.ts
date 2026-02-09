// T031: Add priority, due_date, and recurrence fields to Task type definition
// T068: Add tags field to Task type definition
export type PriorityLevel = 'high' | 'medium' | 'low';
export type RecurrenceFrequency = 'daily' | 'weekly' | 'monthly';

export interface Task {
  id: string;
  title: string;
  description?: string;
  is_completed: boolean;
  priority: PriorityLevel;
  due_date?: string;
  is_recurring: boolean;
  recurrence_frequency?: RecurrenceFrequency;
  tags: string[];
  user_id: string;
  created_at: string;
  updated_at: string;
}

export interface User {
  id: string;
  email: string;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
  is_completed?: boolean;
  priority?: PriorityLevel;
  due_date?: string;
  is_recurring?: boolean;
  recurrence_frequency?: RecurrenceFrequency;
  tags?: string[];
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  is_completed?: boolean;
  priority?: PriorityLevel;
  due_date?: string;
  is_recurring?: boolean;
  recurrence_frequency?: RecurrenceFrequency;
  tags?: string[];
}

export interface TaskPatch {
  is_completed?: boolean;
}

export interface UserCreate {
  email: string;
  password: string;
}

export interface UserLogin {
  email: string;
  password: string;
}