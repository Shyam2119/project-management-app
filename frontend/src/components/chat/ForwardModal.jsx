import { useState, useEffect } from 'react';
import { Search, X, Check, User, Hash } from 'lucide-react';
import { chatAPI } from '../../services/api';

export default function ForwardModal({ isOpen, onClose, message, conversations }) {
    const [search, setSearch] = useState('');
    const [selectedUsers, setSelectedUsers] = useState([]);
    const [selectedGroups, setSelectedGroups] = useState([]);
    const [sending, setSending] = useState(false);

    if (!isOpen) return null;

    const filteredUsers = conversations?.users?.filter(u =>
        u.full_name?.toLowerCase().includes(search.toLowerCase())
    ) || [];

    const filteredGroups = conversations?.groups?.filter(g =>
        g.name.toLowerCase().includes(search.toLowerCase())
    ) || [];

    const toggleUser = (id) => {
        if (selectedUsers.includes(id)) {
            setSelectedUsers(selectedUsers.filter(uid => uid !== id));
        } else {
            setSelectedUsers([...selectedUsers, id]);
        }
    };

    const toggleGroup = (id) => {
        if (selectedGroups.includes(id)) {
            setSelectedGroups(selectedGroups.filter(gid => gid !== id));
        } else {
            setSelectedGroups([...selectedGroups, id]);
        }
    };

    const handleForward = async () => {
        if (selectedUsers.length === 0 && selectedGroups.length === 0) return;

        setSending(true);
        try {
            await chatAPI.post('/messages/forward', {
                message_id: message.id,
                recipient_ids: selectedUsers,
                group_ids: selectedGroups
            });
            onClose();
            // Optional: Show success toast
        } catch (error) {
            console.error("Forward failed:", error);
            alert("Failed to forward message");
        } finally {
            setSending(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4 backdrop-blur-sm">
            <div className="bg-white dark:bg-gray-800 rounded-xl w-full max-w-md max-h-[80vh] flex flex-col shadow-2xl overflow-hidden border border-gray-100 dark:border-gray-700">
                {/* Header */}
                <div className="p-4 border-b border-gray-100 dark:border-gray-700 flex justify-between items-center bg-gray-50 dark:bg-gray-900/50">
                    <h3 className="font-semibold text-gray-800 dark:text-white">Forward Message</h3>
                    <button onClick={onClose} className="p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors">
                        <X className="w-5 h-5 text-gray-500 dark:text-gray-400" />
                    </button>
                </div>

                {/* Search */}
                <div className="p-4 border-b border-gray-100 dark:border-gray-700 bg-white dark:bg-gray-800">
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 dark:text-gray-500" />
                        <input
                            type="text"
                            placeholder="Search people or groups..."
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            className="w-full pl-9 pr-4 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>
                </div>

                {/* List */}
                <div className="flex-1 overflow-y-auto p-2 bg-white dark:bg-gray-800 scrollbar-thin scrollbar-thumb-gray-200 dark:scrollbar-thumb-gray-600">
                    {/* Groups */}
                    {filteredGroups.length > 0 && (
                        <div className="mb-2">
                            <h4 className="px-3 py-1 text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase">Groups</h4>
                            {filteredGroups.map(g => (
                                <div
                                    key={`g-${g.id}`}
                                    onClick={() => toggleGroup(g.id)}
                                    className="flex items-center gap-3 p-2 hover:bg-gray-50 dark:hover:bg-gray-700/50 rounded-lg cursor-pointer transition-colors"
                                >
                                    <div className={`w-5 h-5 border-2 rounded ${selectedGroups.includes(g.id) ? 'bg-blue-600 border-blue-600' : 'border-gray-300 dark:border-gray-600'} flex items-center justify-center transition-colors`}>
                                        {selectedGroups.includes(g.id) && <Check className="w-3 h-3 text-white" />}
                                    </div>
                                    <div className="w-8 h-8 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center">
                                        <Hash className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                                    </div>
                                    <span className="text-sm font-medium text-gray-700 dark:text-gray-200">{g.name}</span>
                                </div>
                            ))}
                        </div>
                    )}

                    {/* Users */}
                    {filteredUsers.length > 0 && (
                        <div>
                            <h4 className="px-3 py-1 text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase">People</h4>
                            {filteredUsers.map(u => (
                                <div
                                    key={`u-${u.id}`}
                                    onClick={() => toggleUser(u.id)}
                                    className="flex items-center gap-3 p-2 hover:bg-gray-50 dark:hover:bg-gray-700/50 rounded-lg cursor-pointer transition-colors"
                                >
                                    <div className={`w-5 h-5 border-2 rounded ${selectedUsers.includes(u.id) ? 'bg-blue-600 border-blue-600' : 'border-gray-300 dark:border-gray-600'} flex items-center justify-center transition-colors`}>
                                        {selectedUsers.includes(u.id) && <Check className="w-3 h-3 text-white" />}
                                    </div>
                                    <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center">
                                        <span className="text-xs font-bold text-blue-600 dark:text-blue-400">{u.first_name?.[0]}</span>
                                    </div>
                                    <div className="flex-1 text-left">
                                        <p className="text-sm font-medium text-gray-700 dark:text-gray-200">{u.full_name}</p>
                                        <p className="text-xs text-gray-400 dark:text-gray-500">{u.role}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="p-4 border-t border-gray-100 dark:border-gray-700 flex justify-end gap-3 bg-gray-50 dark:bg-gray-900/50">
                    <span className="text-sm text-gray-500 dark:text-gray-400 self-center">
                        {selectedUsers.length + selectedGroups.length} selected
                    </span>
                    <button
                        onClick={handleForward}
                        disabled={sending || (selectedUsers.length === 0 && selectedGroups.length === 0)}
                        className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                        {sending ? 'Sending...' : 'Forward'}
                    </button>
                </div>
            </div>
        </div>
    );
}
