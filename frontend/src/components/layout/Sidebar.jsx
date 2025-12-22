import { NavLink } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import {
  LayoutDashboard,
  FolderKanban,
  CheckSquare,
  Users,
  Briefcase,
  UserPlus,
  MessageCircle
} from 'lucide-react';

export default function Sidebar({ onClose }) {
  const { user } = useAuth();

  const handleNavClick = () => {
    if (onClose) onClose(); // Close sidebar on mobile
  };

  const navItems = [
    {
      name: 'Dashboard',
      path: '/dashboard',
      icon: LayoutDashboard,
      roles: ['admin', 'teamleader', 'employee']
    },
    {
      name: 'Projects',
      path: '/projects',
      icon: FolderKanban,
      roles: ['admin', 'teamleader', 'employee']
    },
    {
      name: 'Team',
      path: '/team',
      icon: Users,
      roles: ['admin', 'teamleader']
    },

    {
      name: 'Messages',
      path: '/messages',
      icon: MessageCircle,
      roles: ['admin', 'teamleader', 'employee']
    },
    {
      name: 'My Tasks',
      path: '/my-tasks',
      icon: CheckSquare,
      roles: ['employee']
    },
    {
      name: 'All Tasks',
      path: '/tasks',
      icon: CheckSquare,
      roles: ['admin', 'teamleader']
    }
  ];

  // Filter nav items based on user role
  const filteredNavItems = navItems.filter(item =>
    item.roles.includes(user?.role?.toLowerCase())
  );

  return (
    <aside className="w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 h-full flex flex-col transition-colors">
      {/* Logo */}
      <div className="h-16 flex items-center px-6 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <Briefcase className="w-5 h-5 text-white" />
          </div>
          <span className="font-bold text-gray-900 dark:text-white">PM System</span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {filteredNavItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              onClick={handleNavClick}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors ${isActive
                  ? 'bg-blue-50 dark:bg-blue-900/50 text-blue-700 dark:text-blue-400'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                }`
              }
            >
              <Icon className="w-5 h-5" />
              <span className="font-medium">{item.name}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* User Info */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
            <span className="text-blue-700 dark:text-blue-300 font-semibold text-sm">
              {user?.first_name?.charAt(0)}{user?.last_name?.charAt(0)}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
              {user?.full_name}
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400 capitalize">{user?.role}</p>
          </div>
        </div>
      </div>
    </aside>
  );
}