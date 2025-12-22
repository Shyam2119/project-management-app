import { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { chatAPI } from '../../services/api';
import { Search, Plus, Hash, User, MessageCircle } from 'lucide-react';

export default function ChatSidebar({
    conversations,
    activeChat,
    onSelectChat,
    onCreateGroup
}) {
    const { user } = useAuth();
    const [search, setSearch] = useState('');

    const bots = conversations.users.filter(u => u.is_bot || u.full_name === 'AI Assistant' || u.name === 'AI Assistant');
    const humans = conversations.users.filter(u => !u.is_bot && (
        u.full_name?.toLowerCase().includes(search.toLowerCase()) ||
        u.email.toLowerCase().includes(search.toLowerCase())
    ));

    // Filter groups only
    const filteredGroups = conversations.groups.filter(g =>
        g.name.toLowerCase().includes(search.toLowerCase())
    );

    return (
        <div className="w-80 border-r border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 flex flex-col h-full transition-colors">
            {/* Search & New Group */}
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-xl font-bold text-gray-800 dark:text-white">Messages</h2>
                    <button
                        onClick={onCreateGroup}
                        className="p-2 text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded-lg transition"
                        title="Create New Group"
                    >
                        <Plus className="w-5 h-5" />
                    </button>
                </div>
                <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 dark:text-gray-500" />
                    <input
                        type="text"
                        placeholder="Search people or groups..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="w-full pl-9 pr-4 py-2 bg-gray-50 dark:bg-gray-700/50 border border-gray-200 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
                    />
                </div>
            </div>

            {/* Lists */}
            <div className="flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-300 dark:scrollbar-thumb-gray-600">
                {/* AI Assistant (Pinned) */}
                {bots.length > 0 && (
                    <div className="p-2">
                        <h3 className="px-3 py-2 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider flex items-center gap-2">
                            AI Assistant
                        </h3>
                        {bots.map(bot => (
                            <button
                                key={`bot-${bot.id}`}
                                onClick={() => onSelectChat({ type: 'user', ...bot })}
                                className={`w-full flex items-center gap-3 px-3 py-3 rounded-lg transition-all border ${activeChat?.type === 'user' && activeChat.id === bot.id
                                    ? 'bg-purple-50 dark:bg-purple-900/20 border-purple-200 dark:border-purple-800 text-purple-900 dark:text-purple-100 shadow-sm'
                                    : 'hover:bg-gray-50 dark:hover:bg-gray-700/50 border-transparent text-gray-700 dark:text-gray-200'
                                    }`}
                            >
                                <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-full flex items-center justify-center shadow-md">
                                    <span className="text-white font-bold text-xs">AI</span>
                                </div>
                                <div className="text-left flex-1">
                                    <p className="font-bold text-sm">AI Assistant</p>
                                    <p className="text-xs text-gray-500 dark:text-gray-400">Always active</p>
                                </div>
                            </button>
                        ))}
                        <div className="my-2 border-b border-gray-100 dark:border-gray-700 mx-3"></div>
                    </div>
                )}

                {/* Groups */}
                {filteredGroups.length > 0 && (
                    <div className="p-2">
                        <h3 className="px-3 py-2 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                            Groups
                        </h3>
                        {filteredGroups.map(group => (
                            <button
                                key={`group-${group.id}`}
                                onClick={() => onSelectChat({ type: 'group', ...group })}
                                className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${activeChat?.type === 'group' && activeChat.id === group.id
                                    ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300'
                                    : 'hover:bg-gray-50 dark:hover:bg-gray-700/50 text-gray-700 dark:text-gray-200'
                                    }`}
                            >
                                <div className="p-2 bg-gray-100 dark:bg-gray-700 rounded-lg">
                                    <Hash className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                                </div>
                                <div className="text-left flex-1 truncate">
                                    <p className="font-medium text-sm">{group.name}</p>
                                    <div className="flex justify-between items-center">
                                        <p className="text-xs text-gray-500 dark:text-gray-400">{group.members_count} members</p>
                                        {group.unread_count > 0 && (
                                            <span className="bg-red-500 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full">
                                                {group.unread_count}
                                            </span>
                                        )}
                                    </div>
                                </div>
                            </button>
                        ))}
                    </div>
                )}

                {/* Direct Messages */}
                {humans.length > 0 && (
                    <div className="p-2">
                        <h3 className="px-3 py-2 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                            Direct Messages
                        </h3>
                        {humans.map(u => (
                            <button
                                key={`user-${u.id}`}
                                onClick={() => onSelectChat({ type: 'user', ...u })}
                                className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${activeChat?.type === 'user' && activeChat.id === u.id
                                    ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300'
                                    : 'hover:bg-gray-50 dark:hover:bg-gray-700/50 text-gray-700 dark:text-gray-200'
                                    }`}
                            >
                                <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900/50 rounded-full flex items-center justify-center">
                                    <span className="text-blue-600 dark:text-blue-400 font-medium text-xs">
                                        {u.first_name?.[0]}{u.last_name?.[0]}
                                    </span>
                                </div>
                                <div className="text-left flex-1 truncate">
                                    <p className="font-medium text-sm flex items-center gap-2">
                                        {u.full_name}
                                    </p>
                                    <div className="flex justify-between items-center">
                                        <p className="text-xs text-gray-500 dark:text-gray-400 capitalize">{u.role}</p>
                                        {u.unread_count > 0 && (
                                            <span className="bg-red-500 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full">
                                                {u.unread_count}
                                            </span>
                                        )}
                                    </div>
                                </div>
                            </button>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
