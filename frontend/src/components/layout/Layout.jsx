import { useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(() => window.innerWidth >= 1024);
  const location = useLocation();
  const isFullScreenPage = location.pathname.startsWith('/messages');

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900 transition-colors overflow-x-hidden">
      {/* Sidebar - Desktop */}
      <div className={`hidden lg:block transition-all duration-300 ${sidebarOpen ? 'w-64' : 'w-0 overflow-hidden'}`}>
        <Sidebar />
      </div>

      {/* Sidebar - Mobile (Overlay) */}
      {sidebarOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />

          {/* Sidebar */}
          <div className="fixed inset-y-0 left-0 z-50 lg:hidden">
            <Sidebar onClose={() => setSidebarOpen(false)} />
          </div>
        </>
      )}

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header onMenuClick={() => setSidebarOpen(!sidebarOpen)} />

        <main className={`flex-1 bg-gray-50 dark:bg-gray-900 ${isFullScreenPage
            ? 'overflow-hidden flex flex-col'
            : 'overflow-y-auto'
          }`}>
          <div className={`${isFullScreenPage
              ? 'h-full flex-1'
              : 'max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8'
            }`}>
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}