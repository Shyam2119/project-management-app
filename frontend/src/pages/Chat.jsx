import { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import ChatSidebar from '../components/chat/ChatSidebar';
import ChatWindow from '../components/chat/ChatWindow';
import CreateGroupModal from '../components/modals/CreateGroupModal';
import { chatAPI } from '../services/api';

export default function Chat() {
    const [conversations, setConversations] = useState({ groups: [], users: [] });
    const [activeChat, setActiveChat] = useState(null);
    const [showCreateGroup, setShowCreateGroup] = useState(false);
    const [loading, setLoading] = useState(true);

    const location = useLocation();

    useEffect(() => {
        fetchConversations();
    }, []);

    // Handle incoming navigation from notifications
    useEffect(() => {
        if (!loading && location.state?.selectedChat && conversations) {
            const { id, type } = location.state.selectedChat;
            let chatToSelect = null;
            if (type === 'group') {
                chatToSelect = conversations.groups.find(g => g.id === id);
            } else {
                chatToSelect = conversations.users.find(u => u.id === id);
            }

            if (chatToSelect) {
                handleSelectChat({ type, ...chatToSelect });
                // Clear state to prevent re-selection on refresh
                window.history.replaceState({}, document.title);
            }
        }
    }, [loading, location.state, conversations]);

    const fetchConversations = async () => {
        try {
            const response = await chatAPI.getConversations();
            if (response.data.status === 'success') {
                setConversations(response.data.data);
            }
        } catch (error) {
            console.error('Failed to fetch conversations:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleSelectChat = (chat) => {
        setActiveChat(chat);
        // Optimistically clear unread count in UI
        setConversations(prev => {
            if (chat.type === 'group') {
                return {
                    ...prev,
                    groups: prev.groups.map(g => g.id === chat.id ? { ...g, unread_count: 0 } : g)
                };
            } else {
                return {
                    ...prev,
                    users: prev.users.map(u => u.id === chat.id ? { ...u, unread_count: 0 } : u)
                };
            }
        });
    };

    const handleGroupCreated = (newGroup) => {
        setConversations(prev => ({
            ...prev,
            groups: [newGroup, ...prev.groups]
        }));
        handleSelectChat({ type: 'group', ...newGroup });
    };

    if (loading) {
        return (
            <div className="flex-1 flex items-center justify-center h-full">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    return (
        <div className="flex h-full bg-white dark:bg-gray-900 overflow-hidden transition-colors">
            <ChatSidebar
                conversations={conversations}
                activeChat={activeChat}
                onSelectChat={handleSelectChat}
                onCreateGroup={() => setShowCreateGroup(true)}
            />

            <ChatWindow
                activeChat={activeChat}
                conversations={conversations}
            />

            <CreateGroupModal
                isOpen={showCreateGroup}
                onClose={() => setShowCreateGroup(false)}
                onGroupCreated={handleGroupCreated}
            />
        </div>
    );
}
