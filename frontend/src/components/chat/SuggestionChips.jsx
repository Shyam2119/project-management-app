import { Lightbulb, ListTodo, Activity, AlertCircle } from 'lucide-react';

export default function SuggestionChips({ onSelect }) {
    const suggestions = [
        { label: "Check pending tasks", icon: ListTodo, query: "Show me my pending tasks" },
        { label: "My project status", icon: Activity, query: "What is the current status of my projects?" },
        { label: "Upcoming deadlines", icon: AlertCircle, query: "List my upcoming deadlines for this week" },
        { label: "Productivity report", icon: Lightbulb, query: "Give me a summary of my productivity" },
    ];

    return (
        <div className="flex flex-wrap gap-2 px-6 py-3 bg-gray-50 dark:bg-gray-800 border-b border-gray-100 dark:border-gray-700 transition-colors">
            <span className="text-xs font-semibold text-gray-400 dark:text-gray-500 flex items-center gap-1 uppercase tracking-wider mr-2">
                <Lightbulb className="w-3 h-3" /> Suggested:
            </span>
            {suggestions.map((item, index) => {
                const Icon = item.icon;
                return (
                    <button
                        key={index}
                        onClick={() => onSelect(item.query)}
                        className="flex items-center gap-1.5 px-3 py-1.5 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-full text-xs text-gray-600 dark:text-gray-200 hover:bg-blue-50 dark:hover:bg-blue-900/30 hover:border-blue-200 dark:hover:border-blue-700 hover:text-blue-600 dark:hover:text-blue-300 transition-all shadow-sm"
                    >
                        <Icon className="w-3 h-3 opacity-70" />
                        {item.label}
                    </button>
                );
            })}
        </div>
    );
}
