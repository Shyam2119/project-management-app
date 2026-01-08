import { useState, useEffect } from 'react';
import { Moon, Sun, Monitor, Bell, HelpCircle, FileText, Mail, ChevronRight, Building2, Lock, Eye, EyeOff, CheckCircle, AlertCircle } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

import api, { userAPI, authAPI } from '../services/api'; // Import default (api) and named exports
import DocumentationModal from '../components/modals/DocumentationModal';



export default function Settings() {
    const { user, loading } = useAuth();
    const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'light');
    const [emailNotifs, setEmailNotifs] = useState(true);
    const [pushNotifs, setPushNotifs] = useState(true);
    const [showDocs, setShowDocs] = useState(false);
    
    // Company settings (admin only)
    const [companySettings, setCompanySettings] = useState(null);
    const [companyEmail, setCompanyEmail] = useState('');
    const [companyPassword, setCompanyPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [companyLoginEnabled, setCompanyLoginEnabled] = useState(false);
    const [companySettingsLoading, setCompanySettingsLoading] = useState(false);
    const [companySettingsError, setCompanySettingsError] = useState('');
    const [companySettingsSuccess, setCompanySettingsSuccess] = useState('');

    // Initialize from DB
    useEffect(() => {
        if (user) {
            setEmailNotifs(user.email_notifications ?? true);
            setPushNotifs(user.push_notifications ?? true);
            
            // Load company settings if admin
            if (user.role === 'admin') {
                loadCompanySettings();
            }
        }
    }, [user]);
    
    const loadCompanySettings = async () => {
        try {
            setCompanySettingsLoading(true);
            const response = await authAPI.getCompanySettings();
            if (response.data.status === 'success') {
                const settings = response.data.data;
                setCompanySettings(settings);
                setCompanyEmail(settings.company_email || '');
                setCompanyLoginEnabled(settings.company_login_enabled || false);
            }
        } catch (error) {
            console.error('Failed to load company settings:', error);
        } finally {
            setCompanySettingsLoading(false);
        }
    };
    
    const handleCompanySettingsSave = async () => {
        setCompanySettingsError('');
        setCompanySettingsSuccess('');
        setCompanySettingsLoading(true);
        
        try {
            const updateData = {
                company_email: companyEmail || null,
                company_password: companyPassword || null,
                company_login_enabled: companyLoginEnabled
            };
            
            const response = await authAPI.updateCompanySettings(updateData);
            if (response.data.status === 'success') {
                setCompanySettingsSuccess('Company settings updated successfully');
                setCompanyPassword(''); // Clear password field
                await loadCompanySettings(); // Reload to get updated data
                setTimeout(() => setCompanySettingsSuccess(''), 3000);
            }
        } catch (error) {
            setCompanySettingsError(
                error.response?.data?.message || 'Failed to update company settings'
            );
            setTimeout(() => setCompanySettingsError(''), 5000);
        } finally {
            setCompanySettingsLoading(false);
        }
    };

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

            {/* Company Settings - Admin Only */}
            {user?.role === 'admin' && (
                <div className="card overflow-hidden dark:bg-gray-800 dark:border-gray-700">
                    <div className="p-4 border-b border-gray-100 bg-gray-50 dark:bg-gray-900 dark:border-gray-700">
                        <h2 className="font-semibold text-gray-700 dark:text-gray-200 flex items-center gap-2">
                            <Building2 className="w-5 h-5" />
                            Company Settings
                        </h2>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                            Configure company-wide login credentials
                        </p>
                    </div>
                    <div className="p-6 space-y-6">
                        {companySettingsError && (
                            <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg flex items-start gap-3 dark:bg-red-900/20 dark:border-red-800 dark:text-red-400">
                                <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                                <span className="text-sm">{companySettingsError}</span>
                            </div>
                        )}
                        
                        {companySettingsSuccess && (
                            <div className="bg-green-50 border border-green-200 text-green-600 px-4 py-3 rounded-lg flex items-start gap-3 dark:bg-green-900/20 dark:border-green-800 dark:text-green-400">
                                <CheckCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                                <span className="text-sm">{companySettingsSuccess}</span>
                            </div>
                        )}
                        
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="font-medium text-gray-900 dark:text-white">Enable Company Login</p>
                                <p className="text-sm text-gray-500 dark:text-gray-400">
                                    Allow users to login with company credentials
                                </p>
                            </div>
                            <label className="relative inline-flex items-center cursor-pointer">
                                <input
                                    type="checkbox"
                                    checked={companyLoginEnabled}
                                    onChange={(e) => setCompanyLoginEnabled(e.target.checked)}
                                    className="sr-only peer"
                                />
                                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:bg-gray-700 peer-checked:bg-blue-600"></div>
                            </label>
                        </div>
                        
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                Company Email
                            </label>
                            <div className="relative">
                                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                                <input
                                    type="email"
                                    value={companyEmail}
                                    onChange={(e) => setCompanyEmail(e.target.value)}
                                    className="w-full pl-11 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                                    placeholder="company@example.com"
                                />
                            </div>
                            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                                Users can login with this email and company password
                            </p>
                        </div>
                        
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                Company Password
                            </label>
                            <div className="relative">
                                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                                <input
                                    type={showPassword ? 'text' : 'password'}
                                    value={companyPassword}
                                    onChange={(e) => setCompanyPassword(e.target.value)}
                                    className="w-full pl-11 pr-11 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                                    placeholder="Leave empty to keep current password"
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                                >
                                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                                </button>
                            </div>
                            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                                Leave empty to keep current password. Must be at least 8 characters.
                            </p>
                        </div>
                        
                        <button
                            onClick={handleCompanySettingsSave}
                            disabled={companySettingsLoading}
                            className="w-full bg-blue-600 text-white py-2 rounded-lg font-semibold hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition"
                        >
                            {companySettingsLoading ? 'Saving...' : 'Save Company Settings'}
                        </button>
                    </div>
                </div>
            )}

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
