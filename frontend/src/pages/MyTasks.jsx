import { useState, useEffect } from 'react';
import { taskAPI } from '../services/api';
import { CheckCircle2, Clock, AlertCircle, ListTodo } from 'lucide-react';

export default function MyTasks() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchMyTasks();
  }, []);

  const fetchMyTasks = async () => {
    try {
      setLoading(true);
      const response = await taskAPI.getMyTasks();
      setTasks(response.data.data.tasks);
    } catch (error) {
      console.error('Failed to fetch tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredTasks = tasks.filter(task => {
    if (filter === 'all') return true;
    return task.status === filter;
  });

  const getStatusIcon = (status) => {
    const icons = {
      todo: <ListTodo className="w-5 h-5 text-gray-500" />,
      in_progress: <Clock className="w-5 h-5 text-blue-500" />,
      review: <AlertCircle className="w-5 h-5 text-yellow-500" />,
      completed: <CheckCircle2 className="w-5 h-5 text-green-500" />,
      blocked: <AlertCircle className="w-5 h-5 text-red-500" />
    };
    return icons[status] || icons.todo;
  };

  const getStatusColor = (status) => {
    const colors = {
      todo: 'bg-gray-100 text-gray-800',
      in_progress: 'bg-blue-100 text-blue-800',
      review: 'bg-yellow-100 text-yellow-800',
      completed: 'bg-green-100 text-green-800',
      blocked: 'bg-red-100 text-red-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getPriorityColor = (priority) => {
    const colors = {
      low: 'border-l-gray-400',
      medium: 'border-l-blue-500',
      high: 'border-l-orange-500',
      critical: 'border-l-red-500'
    };
    return colors[priority] || 'border-l-gray-400';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const statusCounts = {
    all: tasks.length,
    todo: tasks.filter(t => t.status === 'todo').length,
    in_progress: tasks.filter(t => t.status === 'in_progress').length,
    review: tasks.filter(t => t.status === 'review').length,
    completed: tasks.filter(t => t.status === 'completed').length
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">My Tasks</h1>
        <p className="text-gray-600 mt-1">Tasks assigned to you</p>
      </div>

      {/* Status Filters */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {[
          { key: 'all', label: 'All Tasks', count: statusCounts.all },
          { key: 'todo', label: 'To Do', count: statusCounts.todo },
          { key: 'in_progress', label: 'In Progress', count: statusCounts.in_progress },
          { key: 'review', label: 'Review', count: statusCounts.review },
          { key: 'completed', label: 'Completed', count: statusCounts.completed }
        ].map(({ key, label, count }) => (
          <button
            key={key}
            onClick={() => setFilter(key)}
            className={`card p-4 text-left transition-all ${
              filter === key
                ? 'ring-2 ring-blue-500 bg-blue-50'
                : 'hover:shadow-md'
            }`}
          >
            <p className="text-sm text-gray-600">{label}</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">{count}</p>
          </button>
        ))}
      </div>

      {/* Tasks List */}
      {filteredTasks.length === 0 ? (
        <div className="card p-12 text-center">
          <ListTodo className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No tasks found</h3>
          <p className="text-gray-600">You're all caught up!</p>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredTasks.map((task) => (
            <div
              key={task.id}
              className={`card p-4 border-l-4 ${getPriorityColor(task.priority)} hover:shadow-md transition-shadow cursor-pointer`}
            >
              <div className="flex items-start gap-4">
                {/* Status Icon */}
                <div className="mt-1">
                  {getStatusIcon(task.status)}
                </div>

                {/* Task Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-4 mb-2">
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900 mb-1">{task.title}</h3>
                      <p className="text-sm text-gray-500">{task.task_number}</p>
                    </div>
                    <span className={`badge ${getStatusColor(task.status)}`}>
                      {task.status.replace('_', ' ')}
                    </span>
                  </div>

                  {task.description && (
                    <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                      {task.description}
                    </p>
                  )}

                  {/* Task Meta */}
                  <div className="flex flex-wrap items-center gap-4 text-sm text-gray-500">
                    {task.assignment && (
                      <div className="flex items-center gap-2">
                        <Clock className="w-4 h-4" />
                        <span>
                          {task.assignment.assigned_hours}h allocated
                          {task.assignment.actual_hours > 0 && 
                            ` • ${task.assignment.actual_hours}h spent`
                          }
                        </span>
                      </div>
                    )}
                    {task.due_date && (
                      <div className={`flex items-center gap-1 ${task.is_overdue ? 'text-red-600' : ''}`}>
                        <AlertCircle className="w-4 h-4" />
                        <span>Due: {task.due_date}</span>
                      </div>
                    )}
                    <span className="capitalize">Priority: {task.priority}</span>
                  </div>

                  {/* Progress Bar */}
                  {task.assignment && task.assignment.assigned_hours > 0 && (
                    <div className="mt-3">
                      <div className="flex justify-between text-xs text-gray-600 mb-1">
                        <span>Progress</span>
                        <span>{task.assignment.completion_percentage}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            task.assignment.is_overallocated
                              ? 'bg-red-500'
                              : 'bg-blue-600'
                          }`}
                          style={{ width: `${Math.min(task.assignment.completion_percentage, 100)}%` }}
                        ></div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}