import React from 'react';
import { X, BookOpen, CheckCircle } from 'lucide-react';

export default function DocumentationModal({ onClose }) {
    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
            <div className="bg-white dark:bg-gray-800 rounded-2xl w-full max-w-2xl max-h-[80vh] overflow-hidden flex flex-col shadow-2xl animate-in fade-in zoom-in duration-200">
                {/* Header */}
                <div className="p-4 border-b border-gray-100 dark:border-gray-700 flex justify-between items-center bg-gray-50 dark:bg-gray-900/50">
                    <div className="flex items-center gap-2">
                        <BookOpen className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">User Guide</h2>
                    </div>
                    <button onClick={onClose} className="p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-full transition-colors">
                        <X className="w-5 h-5 text-gray-500" />
                    </button>
                </div>

                {/* Content */}
                <div className="p-6 overflow-y-auto space-y-6">
                    <section>
                        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2 flex items-center gap-2">
                            <CheckCircle className="w-4 h-4 text-green-500" /> Getting Started
                        </h3>
                        <p className="text-gray-600 dark:text-gray-300 text-sm leading-relaxed">
                            Welcome to the Project Management System. Use the sidebar to navigate between your Projects, Tasks, and Messages.
                        </p>
                    </section>

                    <section>
                        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">🔔 Notifications</h3>
                        <ul className="list-disc list-inside text-gray-600 dark:text-gray-300 text-sm space-y-1">
                            <li>The <strong>Bell Icon</strong> in the header shows your alerts.</li>
                            <li>Click "Trash" to clear all notifications.</li>
                            <li>Toggle "Push Notifications" in Settings to stop receiving them.</li>
                        </ul>
                    </section>

                    <section>
                        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">💬 Chat & Support</h3>
                        <p className="text-gray-600 dark:text-gray-300 text-sm leading-relaxed mb-2">
                            Use the <strong>Messages</strong> tab to chat with team members or the AI Assistant.
                        </p>
                        <div className="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg border border-blue-100 dark:border-blue-800">
                            <p className="text-xs text-blue-800 dark:text-blue-300">
                                <strong>Tip:</strong> You can ask the AI Assistant about project status or help with tasks!
                            </p>
                        </div>
                    </section>

                    <section>
                        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">📞 Contact Support</h3>
                        <p className="text-gray-600 dark:text-gray-300 text-sm">
                            Need more help? Email us at <a href="mailto:support@example.com" className="text-blue-600 hover:underline">support@example.com</a>.
                        </p>
                    </section>
                </div>

                {/* Footer */}
                <div className="p-4 border-t border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50 text-right">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 bg-gray-900 dark:bg-white text-white dark:text-gray-900 rounded-lg text-sm font-medium hover:opacity-90 transition-opacity"
                    >
                        Close Guide
                    </button>
                </div>
            </div>
        </div>
    );
}
