import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { analyticsAPI, projectAPI } from '../services/api';
import {
  FolderKanban,
  CheckCircle2,
  Clock,
  AlertCircle,
  TrendingUp,
  Users
} from 'lucide-react';

export default function Dashboard() {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [recentProjects, setRecentProjects] = useState([]);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [overviewRes, dashboardRes] = await Promise.all([
        analyticsAPI.getOverview(),
        projectAPI.getDashboard()
      ]);

      setStats(overviewRes.data.data);
      setRecentProjects(dashboardRes.data.data.projects);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const statCards = [
    {
      title: 'Total Projects',
      value: stats?.projects?.total || 0,
      icon: FolderKanban,
      color: 'bg-blue-500',
      bgColor: 'bg-blue-50',
      textColor: 'text-blue-600'
    },
    {
      title: 'Active Projects',
      value: stats?.projects?.active || 0,
      icon: Clock,
      color: 'bg-green-500',
      bgColor: 'bg-green-50',
      textColor: 'text-green-600'
    },
    {
      title: 'Completed Tasks',
      value: stats?.tasks?.completed || 0,
      icon: CheckCircle2,
      color: 'bg-purple-500',
      bgColor: 'bg-purple-50',
      textColor: 'text-purple-600'
    },
    {
      title: 'Overdue Tasks',
      value: stats?.tasks?.overdue || 0,
      icon: AlertCircle,
      color: 'bg-red-500',
      bgColor: 'bg-red-50',
      textColor: 'text-red-600'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Welcome back, {user?.first_name}! 👋
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Here's what's happening with your projects today
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <div key={index} className="card p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">{stat.title}</p>
                  <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">{stat.value}</p>
                </div>
                <div className={`w-12 h-12 ${stat.bgColor} dark:bg-opacity-10 rounded-lg flex items-center justify-center`}>
                  <Icon className={`w-6 h-6 ${stat.textColor} dark:text-opacity-90`} />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Projects */}
        <div className="card p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Recent Projects</h2>
            <button className="text-sm text-primary-600 hover:text-primary-700 dark:text-blue-400 dark:hover:text-blue-300 font-medium">
              View All
            </button>
          </div>
          <div className="space-y-3">
            {recentProjects.length === 0 ? (
              <p className="text-gray-500 dark:text-gray-400 text-sm text-center py-8">No projects yet</p>
            ) : (
              recentProjects.map((project) => (
                <div
                  key={project.id}
                  className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition cursor-pointer"
                >
                  <div className="flex-1">
                    <p className="font-medium text-gray-900 dark:text-white">{project.title}</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">{project.code}</p>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className={`badge ${project.status === 'completed' ? 'badge-success' :
                        project.status === 'in_progress' ? 'badge-primary' :
                          'badge-gray'
                      }`}>
                      {project.status?.replace('_', ' ')}
                    </span>
                    <div className="text-right">
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        {project.completion_percentage}%
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">Complete</p>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Team Performance */}
        <div className="card p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Team Overview</h2>
          </div>
          <div className="space-y-4">
            {/* Team Stats */}
            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <Users className="w-8 h-8 text-blue-600 dark:text-blue-400 mb-2" />
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats?.users?.total || 0}</p>
                <p className="text-sm text-gray-600 dark:text-gray-400">Team Members</p>
              </div>
              <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <TrendingUp className="w-8 h-8 text-green-600 dark:text-green-400 mb-2" />
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {stats?.team?.utilization_rate?.toFixed(0) || 0}%
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">Utilization</p>
              </div>
            </div>

            {/* Progress Bar */}
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-600 dark:text-gray-400">Task Completion Rate</span>
                <span className="font-medium text-gray-900 dark:text-white">
                  {stats?.tasks?.completion_rate?.toFixed(0) || 0}%
                </span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div
                  className="bg-blue-600 dark:bg-blue-500 h-2 rounded-full transition-all"
                  style={{ width: `${stats?.tasks?.completion_rate || 0}%` }}
                ></div>
              </div>
            </div>

            {/* Hours Stats */}
            <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
              <div className="flex justify-between items-center text-sm">
                <span className="text-gray-600 dark:text-gray-400">Estimated Hours</span>
                <span className="font-medium text-gray-900 dark:text-white">{stats?.hours?.estimated || 0}h</span>
              </div>
              <div className="flex justify-between items-center text-sm mt-2">
                <span className="text-gray-600 dark:text-gray-400">Actual Hours</span>
                <span className="font-medium text-gray-900 dark:text-white">{stats?.hours?.actual || 0}h</span>
              </div>
              <div className="flex justify-between items-center text-sm mt-2">
                <span className="text-gray-600 dark:text-gray-400">Efficiency</span>
                <span className={`font-medium ${stats?.hours?.efficiency > 100 ? 'text-green-600 dark:text-green-400' : 'text-orange-600 dark:text-orange-400'
                  }`}>
                  {stats?.hours?.efficiency?.toFixed(0) || 0}%
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}