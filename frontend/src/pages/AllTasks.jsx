import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { taskAPI } from '../services/api';
import { Plus, Calendar, Users, Search } from 'lucide-react';
import CreateTaskModal from '../components/modals/CreateTaskModal';

export default function AllTasks() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateTaskModal, setShowCreateTaskModal] = useState(false);
  const [filters, setFilters] = useState({
    status: '',
    priority: '',
    search: ''
  });

  useEffect(() => {
    fetchTasks();
  }, [filters]);

  const fetchTasks = async () => {
    try {
      const response = await taskAPI.getAll(filters);
      if (response.data.status === 'success') {
        setTasks(response.data.data);
      }
    } catch (error) {
      console.error('Error fetching tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      todo: 'bg-gray-100 text-gray-800 border-gray-300 dark:bg-gray-800 dark:text-gray-300 dark:border-gray-600',
      in_progress: 'bg-blue-100 text-blue-800 border-blue-300 dark:bg-blue-900/30 dark:text-blue-300 dark:border-blue-800',
      review: 'bg-yellow-100 text-yellow-800 border-yellow-300 dark:bg-yellow-900/30 dark:text-yellow-400 dark:border-yellow-800',
      completed: 'bg-green-100 text-green-800 border-green-300 dark:bg-green-900/30 dark:text-green-400 dark:border-green-800',
      blocked: 'bg-red-100 text-red-800 border-red-300 dark:bg-red-900/30 dark:text-red-400 dark:border-red-800'
    };
    return colors[status] || colors.todo;
  };

  const getPriorityColor = (priority) => {
    const colors = {
      low: 'text-gray-600 dark:text-gray-400',
      medium: 'text-blue-600 dark:text-blue-400',
      high: 'text-yellow-600 dark:text-yellow-400',
      critical: 'text-red-600 dark:text-red-400'
    };
    return colors[priority] || colors.medium;
  };

  // Group tasks by status for Kanban view
  const tasksByStatus = {
    todo: tasks.filter(t => t.status === 'todo'),
    in_progress: tasks.filter(t => t.status === 'in_progress'),
    review: tasks.filter(t => t.status === 'review'),
    completed: tasks.filter(t => t.status === 'completed')
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">All Tasks</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">{tasks.length} total tasks</p>
        </div>

        <button
          onClick={() => setShowCreateTaskModal(true)}
          className="btn btn-primary flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          New Task
        </button>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 dark:text-gray-500" />
            <input
              type="text"
              placeholder="Search tasks..."
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
              className="w-full pl-11 pr-4 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-800 dark:text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
            />
          </div>
        </div>

        <select
          value={filters.status}
          onChange={(e) => setFilters({ ...filters, status: e.target.value })}
          className="px-4 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-800 dark:text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
        >
          <option value="">All Status</option>
          <option value="todo">To Do</option>
          <option value="in_progress">In Progress</option>
          <option value="review">Review</option>
          <option value="completed">Completed</option>
        </select>

        <select
          value={filters.priority}
          onChange={(e) => setFilters({ ...filters, priority: e.target.value })}
          className="px-4 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-800 dark:text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
        >
          <option value="">All Priority</option>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="critical">Critical</option>
        </select>
      </div>

      {/* Kanban Board */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {Object.entries(tasksByStatus).map(([status, statusTasks]) => (
          <div key={status} className="space-y-4">
            {/* Column Header */}
            <div className={`card p-4 border-t-4 ${getStatusColor(status)} dark:bg-gray-800 dark:border-gray-700`}>
              <div className="flex items-center justify-between">
                <h3 className="font-semibold capitalize text-gray-900 dark:text-white">
                  {status.replace('_', ' ')}
                </h3>
                <span className="text-sm font-medium text-gray-900 dark:text-white">{statusTasks.length}</span>
              </div>
            </div>

            {/* Tasks */}
            <div className="space-y-3">
              {statusTasks.length === 0 ? (
                <div className="card p-4 text-center text-gray-500 dark:text-gray-400 text-sm">
                  No tasks
                </div>
              ) : (
                statusTasks.map(task => (
                  <Link
                    key={task.id}
                    to={`/tasks/${task.id}`}
                    className="block card p-4 hover:shadow-md dark:shadow-sm dark:bg-gray-800 transition"
                  >
                    {/* Priority Indicator */}
                    <div className="flex items-start gap-2 mb-2">
                      <div className={`w-2 h-2 rounded-full mt-2 ${getPriorityColor(task.priority).replace('text-', 'bg-')}`} />
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900 dark:text-white line-clamp-2">
                          {task.title}
                        </h4>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{task.task_number}</p>
                      </div>
                    </div>

                    {/* Project */}
                    {task.project && (
                      <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">
                        {task.project.code}
                      </p>
                    )}

                    {/* Due Date */}
                    {task.due_date && (
                      <div className="flex items-center gap-1 text-xs text-gray-600 dark:text-gray-400 mb-2">
                        <Calendar className="w-3 h-3" />
                        <span>{new Date(task.due_date).toLocaleDateString()}</span>
                      </div>
                    )}

                    {/* Assigned Users */}
                    {task.assigned_users && task.assigned_users.length > 0 && (
                      <div className="flex items-center gap-2 mt-3 pt-3 border-t border-gray-100 dark:border-gray-700">
                        <Users className="w-3 h-3 text-gray-400" />
                        <div className="flex -space-x-2">
                          {task.assigned_users.slice(0, 3).map((user, idx) => (
                            <div
                              key={idx}
                              className="w-6 h-6 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center border-2 border-white dark:border-gray-800"
                              title={user.full_name}
                            >
                              <span className="text-xs text-blue-700 dark:text-blue-300 font-semibold">
                                {user.first_name?.charAt(0)}{user.last_name?.charAt(0)}
                              </span>
                            </div>
                          ))}
                          {task.assigned_users.length > 3 && (
                            <div className="w-6 h-6 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center border-2 border-white dark:border-gray-800">
                              <span className="text-xs text-gray-600 dark:text-gray-300 font-semibold">
                                +{task.assigned_users.length - 3}
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </Link>
                ))
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Create Task Modal */}
      <CreateTaskModal
        isOpen={showCreateTaskModal}
        onClose={() => setShowCreateTaskModal(false)}
        onSuccess={fetchTasks}
      />
    </div>
  );
}