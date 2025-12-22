import { useState, useEffect } from 'react';
import { Moon, Sun, Monitor, Bell, HelpCircle, FileText, Mail, ChevronRight } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

import api, { userAPI, authAPI } from '../services/api'; // Import default (api) and named exports
import DocumentationModal from '../components/modals/DocumentationModal';



export default function Settings() {
    const { user, loading } = useAuth();
    const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'light');
    const [emailNotifs, setEmailNotifs] = useState(true);
    const [pushNotifs, setPushNotifs] = useState(true);
    const [showDocs, setShowDocs] = useState(false);

    // Initialize from DB
    useEffect(() => {
        if (user) {
            setEmailNotifs(user.email_notifications ?? true);
            setPushNotifs(user.push_notifications ?? true);
        }
    }, [user]);

    // Handle Theme Change
    useEffect(() => {
        const root = window.document.documentElement;
        root.classList.remove('light', 'dark');

        if (theme === 'system') {
            const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
            root.classList.add(systemTheme);
        } else {
            root.classList.add(theme);
        }
        localStorage.setItem('theme', theme);
    }, [theme]);

    const handleNotifChange = async (key, value) => {
        // Optimistic update
        if (key === 'email_notifications') setEmailNotifs(value);
        if (key === 'push_notifications') setPushNotifs(value);

        try {
            await userAPI.update(user.id, { [key]: value });
        } catch (error) {
            console.error('Failed to update settings:', error);
            // Revert on error (optional, simplified here)
        }
    };

    return (
        <div className="max-w-3xl mx-auto space-y-6">
            <div className="flex items-center gap-3 mb-6">
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Settings</h1>
            </div>

            {/* Appearance */}
            <div className="card overflow-hidden dark:bg-gray-800 dark:border-gray-700">
                <div className="p-4 border-b border-gray-100 bg-gray-50 dark:bg-gray-900 dark:border-gray-700">
                    <h2 className="font-semibold text-gray-700 dark:text-gray-200 flex items-center gap-2">
                        <Monitor className="w-5 h-5" />
                        Appearance
                    </h2>
                </div>
                <div className="p-6">
                    <div className="grid grid-cols-3 gap-4">
                        <button
                            onClick={() => setTheme('light')}
                            className={`p-4 rounded-xl border-2 flex flex-col items-center gap-3 transition-all ${theme === 'light'
                                ? 'border-blue-600 bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400'
                                : 'border-gray-200 hover:border-gray-300 text-gray-600 dark:border-gray-600 dark:text-gray-400 dark:hover:border-gray-500'
                                }`}
                        >
                            <Sun className="w-6 h-6" />
                            <span className="font-medium">Light</span>
                        </button>
                        <button
                            onClick={() => setTheme('dark')}
                            className={`p-4 rounded-xl border-2 flex flex-col items-center gap-3 transition-all ${theme === 'dark'
                                ? 'border-blue-600 bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400'
                                : 'border-gray-200 hover:border-gray-300 text-gray-600 dark:border-gray-600 dark:text-gray-400 dark:hover:border-gray-500'
                                }`}
                        >
                            <Moon className="w-6 h-6" />
                            <span className="font-medium">Dark</span>
                        </button>
                        <button
                            onClick={() => setTheme('system')}
                            className={`p-4 rounded-xl border-2 flex flex-col items-center gap-3 transition-all ${theme === 'system'
                                ? 'border-blue-600 bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400'
                                : 'border-gray-200 hover:border-gray-300 text-gray-600 dark:border-gray-600 dark:text-gray-400 dark:hover:border-gray-500'
                                }`}
                        >
                            <Monitor className="w-6 h-6" />
                            <span className="font-medium">System</span>
                        </button>
                    </div>
                </div>
            </div>

            {/* Notifications */}
            <div className="card overflow-hidden dark:bg-gray-800 dark:border-gray-700">
                <div className="p-4 border-b border-gray-100 bg-gray-50 dark:bg-gray-900 dark:border-gray-700">
                    <h2 className="font-semibold text-gray-700 dark:text-gray-200 flex items-center gap-2">
                        <Bell className="w-5 h-5" />
                        Notifications
                    </h2>
                </div>
                <div className="p-6 space-y-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="font-medium text-gray-900 dark:text-white">Email Notifications</p>
                            <p className="text-sm text-gray-500 dark:text-gray-400">Receive updates via email</p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                            <input
                                type="checkbox"
                                checked={emailNotifs}
                                onChange={() => handleNotifChange('email_notifications', !emailNotifs)}
                                className="sr-only peer"
                            />
                            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:bg-gray-700 peer-checked:bg-blue-600"></div>
                        </label>
                    </div>
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="font-medium text-gray-900 dark:text-white">Push Notifications</p>
                            <p className="text-sm text-gray-500 dark:text-gray-400">Receive popup notifications in-app</p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                            <input
                                type="checkbox"
                                checked={pushNotifs}
                                onChange={() => handleNotifChange('push_notifications', !pushNotifs)}
                                className="sr-only peer"
                            />
                            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:bg-gray-700 peer-checked:bg-blue-600"></div>
                        </label>
                    </div>
                </div>
            </div>

            {/* Help & Support */}
            <div className="card overflow-hidden dark:bg-gray-800 dark:border-gray-700">
                <div className="p-4 border-b border-gray-100 bg-gray-50 dark:bg-gray-900 dark:border-gray-700">
                    <h2 className="font-semibold text-gray-700 dark:text-gray-200 flex items-center gap-2">
                        <HelpCircle className="w-5 h-5" />
                        Help & Support
                    </h2>
                </div>
                <div className="divide-y divide-gray-100 dark:divide-gray-700">
                    <a
                        href="#"
                        onClick={(e) => { e.preventDefault(); setShowDocs(true); }}
                        className="w-full flex items-center justify-between p-4 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                    >
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-blue-50 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400 rounded-lg">
                                <FileText className="w-5 h-5" />
                            </div>
                            <div className="text-left">
                                <p className="font-medium text-gray-900 dark:text-white">Documentation</p>
                                <p className="text-sm text-gray-500 dark:text-gray-400">Read guides and tutorials</p>
                            </div>
                        </div>
                        <ChevronRight className="w-5 h-5 text-gray-400" />
                    </a>

                    <a
                        href="mailto:support@example.com"
                        className="w-full flex items-center justify-between p-4 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                    >
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-green-50 text-green-600 dark:bg-green-900/30 dark:text-green-400 rounded-lg">
                                <Mail className="w-5 h-5" />
                            </div>
                            <div className="text-left">
                                <p className="font-medium text-gray-900 dark:text-white">Contact Support</p>
                                <p className="text-sm text-gray-500 dark:text-gray-400">Get help with an issue</p>
                            </div>
                        </div>
                        <ChevronRight className="w-5 h-5 text-gray-400" />
                    </a>
                </div>
            </div>

            <div className="text-center pt-6">
                <p className="text-sm text-gray-400">PM System v1.0.0</p>
            </div>

            {showDocs && <DocumentationModal onClose={() => setShowDocs(false)} />}
        </div>
    );
}
