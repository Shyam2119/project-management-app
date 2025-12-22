import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { notificationAPI, chatAPI } from '../../services/api';
import { Bell, Search, User, LogOut, Settings, Menu, Trash2, Check } from 'lucide-react';

export default function Header({ onMenuClick }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [showDropdown, setShowDropdown] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);

  // Notification State
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loadingNotifs, setLoadingNotifs] = useState(false);
  const notifRef = useRef(null);

  useEffect(() => {
    // Initial fetch of unread count
    fetchUnreadCount();

    // Poll every minute
    const interval = setInterval(fetchUnreadCount, 60000);

    // Listen for custom events to refresh count
    const handleUpdate = () => fetchUnreadCount();
    window.addEventListener('notification-update', handleUpdate);
    window.addEventListener('focus', handleUpdate);

    return () => {
      clearInterval(interval);
      window.removeEventListener('notification-update', handleUpdate);
      window.removeEventListener('focus', handleUpdate);
    };
  }, []);

  // Close dropdowns when clicking outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (notifRef.current && !notifRef.current.contains(event.target)) {
        setShowNotifications(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const fetchUnreadCount = async () => {
    try {
      const [notifRes, chatRes] = await Promise.all([
        notificationAPI.getUnreadCount(),
        chatAPI.getConversations()
      ]);

      let total = 0;

      // System Notifications
      if (notifRes.data.status === 'success') {
        total += notifRes.data.data.unread_count;
      }

      // Chat Notifications
      if (chatRes.data.status === 'success') {
        const { groups, users } = chatRes.data.data;
        const groupUnread = groups.reduce((acc, g) => acc + (g.unread_count || 0), 0);
        const userUnread = users.reduce((acc, u) => acc + (u.unread_count || 0), 0);
        total += groupUnread + userUnread;
      }

      setUnreadCount(total);
    } catch (error) {
      console.error('Failed to fetch unread count:', error);
    }
  };

  const fetchNotifications = async () => {
    setLoadingNotifs(true);
    try {
      const [notifRes, chatRes] = await Promise.all([
        notificationAPI.getAll({ page: 1, per_page: 10 }),
        chatAPI.getConversations()
      ]);

      let combinedNotifications = [];

      // Process Chat "Notifications"
      if (chatRes.data.status === 'success') {
        const { groups, users } = chatRes.data.data;

        // Add Groups with unread messages
        groups.forEach(g => {
          if (g.unread_count > 0) {
            combinedNotifications.push({
              id: `chat-group-${g.id}`,
              type: 'chat',
              data: { id: g.id, type: 'group' },
              message: `You have ${g.unread_count} new message(s) in ${g.name}`,
              created_at: new Date().toISOString(), // Mock time or use last_message_at
              is_read: false
            });
          }
        });

        // Add Users with unread messages
        users.forEach(u => {
          if (u.unread_count > 0) {
            combinedNotifications.push({
              id: `chat-user-${u.id}`,
              type: 'chat',
              data: { id: u.id, type: 'user' },
              message: `You have ${u.unread_count} new message(s) from ${u.full_name}`,
              created_at: new Date().toISOString(),
              is_read: false
            });
          }
        });
      }

      // Process System Notifications
      if (notifRes.data.status === 'success') {
        combinedNotifications = [...combinedNotifications, ...notifRes.data.data];
      }

      setNotifications(combinedNotifications);
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
    } finally {
      setLoadingNotifs(false);
    }
  };

  const handleNotificationClick = () => {
    if (!showNotifications) {
      fetchNotifications();
    }
    setShowNotifications(!showNotifications);
  };

  const markAsRead = async (id) => {
    try {
      await notificationAPI.markAsRead(id);
      setNotifications(notifications.map(n =>
        n.id === id ? { ...n, is_read: true } : n
      ));
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (error) {
      console.error('Failed to mark as read:', error);
    }
  };

  const markAllRead = async () => {
    try {
      await notificationAPI.markAllAsRead();
      setNotifications(notifications.map(n => ({ ...n, is_read: true })));
      setUnreadCount(0);
    } catch (error) {
      console.error('Failed to mark all read:', error);
    }
  };

  const clearAll = async () => {
    try {
      await notificationAPI.delete('clear-all'); // Using special endpoint if available or loop
      // Based on API: delete takes ID, not 'clear-all' usually, but noticed route /clear-all
      // Let's verify route... yes @notifications_bp.route('/clear-all', methods=['DELETE'])
      // Wait, api.js might need update to support clear-all if delete(id) expects int.
      // Let's check api.js... delete: (id) => api.delete(`/notifications/${id}`)
      // So passing 'clear-all' works: DELETE /notifications/clear-all
      setNotifications([]);
    } catch (error) {
      console.error('Failed to clear notifications:', error);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="h-16 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between px-6 z-30 relative transition-colors">
      {/* Left: Hamburger Menu (Mobile) */}
      <button
        onClick={onMenuClick}
        className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition"
      >
        <Menu className="w-6 h-6 text-gray-600 dark:text-gray-300" />
      </button>

      {/* Search Bar */}
      <div className="flex-1 max-w-lg mx-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search projects, tasks..."
            className="w-full pl-11 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500"
          />
        </div>
      </div>

      {/* Right Section */}
      <div className="flex items-center gap-4">
        {/* Notifications */}
        <div className="relative" ref={notifRef}>
          <button
            onClick={handleNotificationClick}
            className="relative p-2 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition"
          >
            <Bell className="w-5 h-5" />
            {unreadCount > 0 && (
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
            )}
          </button>

          {/* Notification Dropdown */}
          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 z-50 overflow-hidden">
              <div className="p-3 border-b border-gray-100 dark:border-gray-700 flex justify-between items-center bg-gray-50 dark:bg-gray-900">
                <h3 className="font-semibold text-gray-700 dark:text-gray-200">Notifications</h3>
                <div className="flex gap-2">
                  <button onClick={markAllRead} className="text-xs text-blue-600 hover:text-blue-800" title="Mark all read">
                    <Check className="w-4 h-4" />
                  </button>
                  <button onClick={clearAll} className="text-xs text-red-600 hover:text-red-800" title="Clear all">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>

              <div className="max-h-96 overflow-y-auto">
                {loadingNotifs ? (
                  <div className="p-4 text-center text-gray-500 text-sm">Loading...</div>
                ) : notifications.length === 0 ? (
                  <div className="p-4 text-center text-gray-400 text-sm">No notifications</div>
                ) : (
                  notifications.map(notif => (
                    <div
                      key={notif.id}
                      onClick={() => {
                        if (notif.type === 'chat') {
                          navigate('/messages', { state: { selectedChat: notif.data } });
                          setShowNotifications(false);
                        } else {
                          // Allow expanding system notifications if needed, or just do nothing/mark read
                          // For now, let's just mark read if clicked? Or leave button.
                        }
                      }}
                      className={`p-3 border-b border-gray-50 hover:bg-gray-50 transition-colors cursor-pointer ${!notif.is_read ? 'bg-blue-50/50' : ''}`}
                    >
                      <p className="text-sm text-gray-800 mb-1 font-medium">{notif.message}</p>
                      <div className="flex justify-between items-center">
                        <span className="text-xs text-gray-400">
                          {notif.type === 'chat' ? 'Chat' : new Date(notif.created_at).toLocaleDateString()}
                        </span>
                        {!notif.is_read && notif.type !== 'chat' && (
                          <button
                            onClick={(e) => { e.stopPropagation(); markAsRead(notif.id); }}
                            className="text-xs text-blue-600 hover:underline"
                          >
                            Mark Read
                          </button>
                        )}
                        {notif.type === 'chat' && (
                          <span className="text-xs text-blue-600">View</span>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* User Menu */}
        <div className="relative">
          <button
            onClick={() => setShowDropdown(!showDropdown)}
            className="flex items-center gap-3 p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition"
          >
            <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
              <span className="text-white font-semibold text-sm">
                {user?.first_name?.charAt(0)}{user?.last_name?.charAt(0)}
              </span>
            </div>
            <div className="text-left hidden md:block">
              <p className="text-sm font-medium text-gray-900 dark:text-white">{user?.full_name}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400 capitalize">{user?.role}</p>
            </div>
          </button>

          {/* Dropdown Menu */}
          {showDropdown && (
            <>
              <div
                className="fixed inset-0 z-10"
                onClick={() => setShowDropdown(false)}
              ></div>
              <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-1 z-20">
                <button
                  onClick={() => {
                    navigate('/profile');
                    setShowDropdown(false);
                  }}
                  className="w-full flex items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  <User className="w-4 h-4" />
                  Profile
                </button>
                <button
                  onClick={() => {
                    navigate('/settings');
                    setShowDropdown(false);
                  }}
                  className="w-full flex items-center gap-3 px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  <Settings className="w-4 h-4" />
                  Settings
                </button>
                <hr className="my-1 border-gray-200 dark:border-gray-700" />
                <button
                  onClick={handleLogout}
                  className="w-full flex items-center gap-3 px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                >
                  <LogOut className="w-4 h-4" />
                  Logout
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </header>
  );
}