import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { taskAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import {
  ArrowLeft,
  Calendar,
  Clock,
  Users,
  MessageSquare,
  Send,
  Edit,
  Trash2
} from 'lucide-react';

export default function TaskDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [task, setTask] = useState(null);
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTaskDetails();
  }, [id]);

  const fetchTaskDetails = async () => {
    try {
      setLoading(true);
      const response = await taskAPI.getById(id);
      const taskData = response.data.data.task;
      setTask(taskData);
      setComments(taskData.comments || []);
    } catch (error) {
      console.error('Error fetching task:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddComment = async (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    try {
      await taskAPI.addComment(id, { content: newComment });
      setNewComment('');
      fetchTaskDetails(); // Refresh to get new comment
    } catch (error) {
      console.error('Error adding comment:', error);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      todo: 'bg-gray-100 text-gray-800',
      in_progress: 'bg-blue-100 text-blue-800',
      review: 'bg-purple-100 text-purple-800',
      completed: 'bg-green-100 text-green-800',
      blocked: 'bg-red-100 text-red-800'
    };
    return colors[status] || colors.todo;
  };

  const getPriorityColor = (priority) => {
    const colors = {
      low: 'bg-gray-100 text-gray-800',
      medium: 'bg-blue-100 text-blue-800',
      high: 'bg-orange-100 text-orange-800',
      critical: 'bg-red-100 text-red-800'
    };
    return colors[priority] || colors.low;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading task details...</div>
      </div>
    );
  }

  if (!task) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-gray-900">Task not found</h2>
        <button onClick={() => navigate('/my-tasks')} className="mt-4 btn btn-primary">
          Back to Tasks
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate(-1)}
            className="p-2 hover:bg-gray-100 rounded-lg"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold text-gray-900">{task.title}</h1>
              <span className={`badge ${getStatusColor(task.status)}`}>
                {task.status.replace('_', ' ')}
              </span>
              <span className={`badge ${getPriorityColor(task.priority)}`}>
                {task.priority}
              </span>
            </div>
            <p className="text-gray-500 text-sm mt-1">{task.task_number}</p>
          </div>
        </div>
        <button className="btn btn-secondary">
          <Edit className="w-4 h-4 mr-2" />
          Edit Task
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Description */}
          <div className="card p-6">
            <h3 className="text-lg font-semibold mb-4">Description</h3>
            <p className="text-gray-600">{task.description || 'No description provided'}</p>
          </div>

          {/* Comments */}
          <div className="card p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <MessageSquare className="w-5 h-5" />
              Comments ({comments.length})
            </h3>

            {/* Comments List */}
            <div className="space-y-4 mb-6">
              {comments.length === 0 ? (
                <p className="text-gray-500 text-center py-8">No comments yet</p>
              ) : (
                comments.map((comment) => (
                  <div key={comment.id} className="flex gap-3">
                    <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white font-semibold flex-shrink-0">
                      {comment.author?.first_name?.charAt(0)}
                      {comment.author?.last_name?.charAt(0)}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{comment.author?.full_name}</span>
                        <span className="text-sm text-gray-500">
                          {new Date(comment.created_at).toLocaleDateString()}
                        </span>
                      </div>
                      <p className="text-gray-600 mt-1">{comment.content}</p>
                    </div>
                  </div>
                ))
              )}
            </div>

            {/* Add Comment Form */}
            <form onSubmit={handleAddComment} className="flex gap-3">
              <input
                type="text"
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                placeholder="Add a comment..."
                className="input flex-1"
              />
              <button type="submit" className="btn btn-primary">
                <Send className="w-4 h-4" />
              </button>
            </form>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Task Info */}
          <div className="card p-6">
            <h3 className="text-lg font-semibold mb-4">Task Details</h3>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-500">Project</p>
                <Link
                  to={`/projects/${task.project_id}`}
                  className="font-medium text-blue-600 hover:text-blue-700"
                >
                  {task.project?.title}
                </Link>
              </div>

              <div>
                <p className="text-sm text-gray-500">Due Date</p>
                <div className="flex items-center gap-2 font-medium">
                  <Calendar className="w-4 h-4 text-gray-400" />
                  {new Date(task.due_date).toLocaleDateString()}
                </div>
              </div>

              <div>
                <p className="text-sm text-gray-500">Estimated Hours</p>
                <div className="flex items-center gap-2 font-medium">
                  <Clock className="w-4 h-4 text-gray-400" />
                  {task.estimated_hours}h
                </div>
              </div>

              {task.actual_hours && (
                <div>
                  <p className="text-sm text-gray-500">Actual Hours</p>
                  <div className="flex items-center gap-2 font-medium">
                    <Clock className="w-4 h-4 text-gray-400" />
                    {task.actual_hours}h
                  </div>
                </div>
              )}

              <div>
                <p className="text-sm text-gray-500">Created By</p>
                <p className="font-medium">{task.creator?.full_name}</p>
              </div>
            </div>
          </div>

          {/* Assigned Users */}
          <div className="card p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Users className="w-5 h-5" />
              Assigned To ({task.assigned_users?.length || 0})
            </h3>
            <div className="space-y-3">
              {task.assigned_users?.length === 0 ? (
                <p className="text-gray-500 text-sm">No one assigned</p>
              ) : (
                task.assigned_users?.map((assignedUser) => (
                  <div key={assignedUser.id} className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white font-semibold">
                      {assignedUser.first_name?.charAt(0)}
                      {assignedUser.last_name?.charAt(0)}
                    </div>
                    <div className="flex-1">
                      <p className="font-medium">{assignedUser.full_name}</p>
                      <p className="text-sm text-gray-500">{assignedUser.role}</p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}