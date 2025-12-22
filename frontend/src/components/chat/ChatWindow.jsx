import { useState, useEffect, useRef } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { chatAPI, uploadAPI } from '../../services/api';
import SuggestionChips from './SuggestionChips';
import ForwardModal from './ForwardModal';
import {
    MessageCircle, Phone, Video, MoreVertical, Trash2,
    CornerUpRight, Paperclip, Send, Mic, Copy, LogOut
} from 'lucide-react';

export default function ChatWindow({ activeChat, conversations }) {
    const { user } = useAuth();
    const [messages, setMessages] = useState([]);
    const [newMessage, setNewMessage] = useState('');
    const [showMenu, setShowMenu] = useState(false);
    const [contextMenu, setContextMenu] = useState({ visible: false, x: 0, y: 0, message: null });
    const [showForwardModal, setShowForwardModal] = useState(false);
    const [selectedMessage, setSelectedMessage] = useState(null);
    const [isRecording, setIsRecording] = useState(false);

    const messagesEndRef = useRef(null);
    const fileInputRef = useRef(null);
    const mediaRecorderRef = useRef(null);

    useEffect(() => {
        if (activeChat) {
            fetchMessages();
            setNewMessage('');
            setShowMenu(false);
        }
    }, [activeChat]);

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    const fetchMessages = async () => {
        try {
            const params = activeChat.type === 'group'
                ? { group_id: activeChat.id }
                : { user_id: activeChat.id };
            const response = await chatAPI.getMessages(params);
            if (response.data.status === 'success') {
                setMessages(response.data.data);
                // Trigger notification update (header badge)
                window.dispatchEvent(new Event('notification-update'));
            }
        } catch (error) {
            console.error('Failed to fetch messages:', error);
        }
    };

    const handleFileUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        try {
            const formData = new FormData();
            formData.append('file', file);

            // Upload file
            const response = await uploadAPI.upload(formData);

            if (response.data.status === 'success') {
                const fileUrl = response.data.data.url;
                const type = file.type.startsWith('image/') ? 'image' : 'file';
                handleSend(null, fileUrl, type);
            }
        } catch (error) {
            console.error('File upload failed:', error);
            alert('Failed to upload file');
        }
    };

    const startRecording = () => {
        setIsRecording(true);
        // Placeholder for actual recording logic
    };

    const stopRecording = () => {
        setIsRecording(false);
        // Placeholder for stop recording and send voice
        handleSend(null, 'voice-url-placeholder', 'voice');
    };

    const clearChat = async () => {
        if (!window.confirm('Are you sure? This will clear your view of the chat conversation.')) return;
        try {
            const params = activeChat.type === 'group'
                ? { group_id: activeChat.id }
                : { user_id: activeChat.id };
            await chatAPI.clearChat(params);
            setMessages([]);
            setShowMenu(false);
        } catch (error) {
            console.error('Failed to clear chat:', error);
        }
    };

    const deleteMessage = async (mode) => {
        if (!contextMenu.message) return;
        try {
            await chatAPI.deleteMessage(contextMenu.message.id, mode);
            setMessages(messages.map(m =>
                m.id === contextMenu.message.id
                    ? { ...m, is_deleted_globally: true, content: 'Starting transition to deleted state...' } // Optimistic update
                    : m
            ));
            // Re-fetch to get clean state
            fetchMessages();
            setContextMenu({ ...contextMenu, visible: false });
        } catch (error) {
            console.error('Failed to delete message:', error);
        }
    };

    const handleRenameGroup = async (newName) => {
        try {
            await chatAPI.renameGroup(activeChat.id, newName);
            // Refresh logic: ideally we should bubble this up to Chat.jsx to refresh sidebar, 
            // but for now let's just update local state if we could, 
            // or trigger a reload. To keep it simple and effective:
            window.location.reload();
        } catch (error) {
            console.error('Failed to rename group:', error);
            alert('Failed to rename group');
        }
    };

    const handleLeaveGroup = async () => {
        try {
            await chatAPI.leaveGroup(activeChat.id);
            window.location.reload(); // Refresh to remove from list
        } catch (error) {
            console.error('Failed to leave group:', error);
            alert('Failed to leave group');
        }
    };

    const handleContextMenu = (e, msg) => {
        e.preventDefault();
        // Prevent menu from going off-screen (approx width 176px/11rem = 176px + padding)
        const menuWidth = 200;
        const x = e.clientX + menuWidth > window.innerWidth ? window.innerWidth - menuWidth - 20 : e.clientX;

        setContextMenu({
            visible: true,
            x: x,
            y: e.clientY,
            message: msg
        });
    };

    const copyMessage = () => {
        if (contextMenu.message?.content) {
            navigator.clipboard.writeText(contextMenu.message.content);
            setContextMenu({ ...contextMenu, visible: false });
        }
    };

    const openForwardModal = (msg) => {
        setSelectedMessage(msg);
        setShowForwardModal(true);
    };
    const handleSuggestion = (query) => {
        setNewMessage(query);
        // Optional: auto-send? Let's just fill input for now, user clicks send.
        // Or better, auto-send as it's a "chip"
        handleSend(null, null, 'text', query);
    };

    // Modified handleSend to accept direct content override
    const handleSend = async (e, attachment = null, type = 'text', contentOverride = null) => {
        if (e) e.preventDefault();

        let content = contentOverride || newMessage;
        if (attachment) {
            content = type === 'voice' ? 'Voice Message' : (type === 'image' ? 'Image' : 'File Attachment');
        }

        if (!content.trim() && !attachment) return;

        if (!attachment && !contentOverride) {
            setNewMessage('');
        }

        try {
            const data = {
                content: content,
                ...(activeChat.type === 'group' ? { group_id: activeChat.id } : { recipient_id: activeChat.id }),
                attachment_url: attachment,
                message_type: type
            };

            const response = await chatAPI.sendMessage(data);
            if (response.data.status === 'success') {
                setMessages(prev => [...prev, response.data.data]);
                scrollToBottom();
            }
        } catch (error) {
            console.error('Failed to send message:', error);
        }
    };

    const renderMessageContent = (msg) => {
        if (msg.message_type === 'image') {
            return (
                <div className="mt-1">
                    <img
                        src={msg.attachment_url.startsWith('blob:') ? msg.attachment_url : `http://localhost:5000${msg.attachment_url}`}
                        alt="Attachment"
                        className="max-w-full rounded-lg cursor-pointer hover:opacity-90 transition-opacity"
                        style={{ maxHeight: '200px' }}
                        onClick={() => window.open(msg.attachment_url, '_blank')}
                    />
                    {msg.content && msg.content !== 'Image' && <p className="mt-1">{msg.content}</p>}
                </div>
            );
        }
        if (msg.message_type === 'file') {
            return (
                <div className="flex items-center gap-2 mt-1 bg-gray-100 dark:bg-gray-700/50 p-2 rounded-lg">
                    <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                        <Paperclip className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">Attachment</p>
                        <a
                            href={msg.attachment_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs text-blue-600 dark:text-blue-400 hover:underline"
                            onClick={(e) => e.stopPropagation()}
                        >
                            Download
                        </a>
                    </div>
                </div>
            );
        }
        return <p className="text-sm whitespace-pre-wrap break-words">{msg.content}</p>;
    };

    // ... (rest of logic)

    if (!activeChat) {
        return (
            <div className="flex-1 flex items-center justify-center bg-gray-50 dark:bg-gray-900 h-full transition-colors">
                <div className="text-center text-gray-400 dark:text-gray-500">
                    <MessageCircle className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>Select a conversation to start messaging</p>
                </div>
            </div>
        );
    }

    const isAI = activeChat.type === 'user' && (activeChat.is_bot || activeChat.full_name === 'AI Assistant' || activeChat.name === 'AI Assistant');

    return (
        <div className="flex-1 flex flex-col h-full bg-white dark:bg-gray-900 relative transition-colors">
            {/* Header */}
            <div className="h-16 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between px-6 bg-white dark:bg-gray-800 z-10 transition-colors">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-indigo-100 dark:bg-indigo-900/50 rounded-full flex items-center justify-center overflow-hidden">
                        {activeChat.type === 'user' && activeChat.profile_picture ? (
                            <img src={`http://localhost:5000${activeChat.profile_picture}`} className="w-full h-full object-cover" />
                        ) : (
                            <span className="text-indigo-600 dark:text-indigo-400 font-semibold">
                                {activeChat.name?.[0] || activeChat.first_name?.[0]}
                            </span>
                        )}
                    </div>
                    <div>
                        <h3 className="font-semibold text-gray-900 dark:text-white">
                            {activeChat.type === 'group' ? activeChat.name : activeChat.full_name}
                            {isAI && <span className="ml-2 px-1.5 py-0.5 bg-purple-100 dark:bg-purple-900/50 text-purple-600 dark:text-purple-300 text-[10px] rounded border border-purple-200 dark:border-purple-700 uppercase tracking-wide font-bold">AI</span>}
                        </h3>
                        {activeChat.type === 'user' && (
                            <span className="text-xs text-green-500 flex items-center gap-1">
                                ● Online
                            </span>
                        )}
                    </div>
                </div>
                <div className="flex items-center gap-2 text-gray-400 dark:text-gray-500 relative">
                    <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full transition"><Phone className="w-5 h-5" /></button>
                    <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full transition"><Video className="w-5 h-5" /></button>
                    <button
                        onClick={(e) => { e.stopPropagation(); setShowMenu(!showMenu); }}
                        className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full transition"
                    >
                        <MoreVertical className="w-5 h-5" />
                    </button>
                    {/* Header Menu */}
                    {showMenu && (
                        <div className="absolute right-0 top-12 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-100 dark:border-gray-700 w-48 py-1 z-20">
                            <button onClick={clearChat} className="w-full text-left px-4 py-2 hover:bg-red-50 dark:hover:bg-red-900/20 text-red-600 dark:text-red-400 text-sm flex items-center gap-2">
                                <Trash2 className="w-4 h-4" /> Clear Chat
                            </button>
                            {activeChat.type === 'group' && (
                                <>
                                    <hr className="my-1 border-gray-100 dark:border-gray-700" />
                                    <button
                                        onClick={() => {
                                            setShowMenu(false);
                                            const newName = window.prompt("Enter new group name:", activeChat.name);
                                            if (newName) handleRenameGroup(newName);
                                        }}
                                        className="w-full text-left px-4 py-2 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-200 text-sm flex items-center gap-2"
                                    >
                                        <MoreVertical className="w-4 h-4" /> Rename Group
                                    </button>
                                    <button
                                        onClick={() => {
                                            setShowMenu(false);
                                            if (window.confirm("Are you sure you want to leave this group?")) handleLeaveGroup();
                                        }}
                                        className="w-full text-left px-4 py-2 hover:bg-red-50 dark:hover:bg-red-900/20 text-red-600 dark:text-red-400 text-sm flex items-center gap-2"
                                    >
                                        <LogOut className="w-4 h-4" /> Leave Group
                                    </button>
                                </>
                            )}
                        </div>
                    )}
                </div>
            </div>

            {/* AI Suggestions (Only for AI chat) */}
            {isAI && <SuggestionChips onSelect={(q) => handleSend(null, null, 'text', q)} />}

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-gray-50 dark:bg-gray-900 scrollbar-thin scrollbar-thumb-gray-300 dark:scrollbar-thumb-gray-600" onClick={() => setContextMenu({ ...contextMenu, visible: false })}>
                {messages.map((msg) => {
                    const isOwn = msg.sender_id === user?.id;
                    const isDeleted = msg.is_deleted_globally;

                    return (
                        <div key={msg.id} className={`flex ${isOwn ? 'justify-end' : 'justify-start'} group relative`}>
                            {/* Message Bubble */}
                            <div
                                onContextMenu={(e) => !isDeleted && handleContextMenu(e, msg)}
                                className={`max-w-[70%] rounded-2xl px-4 py-2 shadow-sm cursor-pointer relative 
                                    ${isOwn
                                        ? 'bg-blue-600 dark:bg-blue-700 text-white rounded-br-none'
                                        : 'bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-bl-none border border-gray-100 dark:border-gray-700'}
                                    ${isDeleted ? 'bg-gray-200 dark:bg-gray-800/50 text-gray-500 dark:text-gray-500 italic' : ''}
                                `}
                            >
                                {!isOwn && activeChat.type === 'group' && !isDeleted && (
                                    <p className="text-xs font-semibold mb-1 opacity-75">{msg.sender_name}</p>
                                )}
                                {renderMessageContent(msg)}
                                <div className={`text-[10px] mt-1 text-right ${isOwn && !isDeleted ? 'text-blue-200' : 'text-gray-400 dark:text-gray-500'}`}>
                                    {new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                </div>

                                {/* Hover Action (Quick Forward) only if not deleted */}
                                {!isDeleted && (
                                    <button
                                        onClick={(e) => { e.stopPropagation(); openForwardModal(msg); }}
                                        className="absolute top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity p-1 bg-gray-100 dark:bg-gray-700 rounded-full shadow-md text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-blue-50 dark:hover:bg-gray-600 -right-8 z-10"
                                        title="Forward"
                                        style={isOwn ? { left: '-32px', right: 'auto' } : { right: '-32px' }}
                                    >
                                        <CornerUpRight className="w-4 h-4" />
                                    </button>
                                )}
                            </div>
                        </div>
                    );
                })}
                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="p-4 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 transition-colors">
                <form onSubmit={handleSend} className="flex items-center gap-3">
                    <button type="button" onClick={() => fileInputRef.current?.click()} className="p-2 text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full transition">
                        <Paperclip className="w-5 h-5" />
                    </button>
                    <input type="file" ref={fileInputRef} className="hidden" onChange={handleFileUpload} />
                    <input
                        type="text"
                        value={newMessage}
                        onChange={(e) => setNewMessage(e.target.value)}
                        placeholder={isAI ? "Ask me about projects, tasks, or deadlines..." : "Type your message..."}
                        className="flex-1 px-4 py-2 border border-gray-200 dark:border-gray-700 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 transition-colors"
                    />
                    {newMessage.trim() ? (
                        <button type="submit" className="p-2 bg-blue-600 hover:bg-blue-700 text-white rounded-full transition shadow-lg shadow-blue-600/20"><Send className="w-5 h-5" /></button>
                    ) : (
                        <button type="button" onClick={isRecording ? stopRecording : startRecording} className={`p-2 rounded-full transition ${isRecording ? 'bg-red-500 text-white animate-pulse' : 'bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600'}`}><Mic className="w-5 h-5" /></button>
                    )}
                </form>
            </div>

            {/* Context Menu */}
            {contextMenu.visible && (
                <div
                    className="fixed bg-white dark:bg-gray-800 shadow-xl rounded-lg border border-gray-100 dark:border-gray-700 py-1 z-50 w-44"
                    style={{ top: contextMenu.y, left: contextMenu.x }}
                >
                    <button onClick={copyMessage} className="w-full text-left px-4 py-2 hover:bg-gray-50 dark:hover:bg-gray-700 text-sm flex items-center gap-2 text-gray-700 dark:text-gray-200">
                        <Copy className="w-4 h-4" /> Copy
                    </button>
                    <button onClick={() => { openForwardModal(contextMenu.message); setContextMenu({ ...contextMenu, visible: false }); }} className="w-full text-left px-4 py-2 hover:bg-gray-50 dark:hover:bg-gray-700 text-sm flex items-center gap-2 text-gray-700 dark:text-gray-200">
                        <CornerUpRight className="w-4 h-4" /> Forward
                    </button>
                    <hr className="my-1 border-gray-100 dark:border-gray-700" />
                    <button onClick={() => deleteMessage('me')} className="w-full text-left px-4 py-2 hover:bg-gray-50 dark:hover:bg-gray-700 text-sm flex items-center gap-2 text-gray-700 dark:text-gray-200">
                        <Trash2 className="w-4 h-4" /> Delete For Me
                    </button>
                    {contextMenu.message.sender_id === user?.id && (
                        <button onClick={() => deleteMessage('everyone')} className="w-full text-left px-4 py-2 hover:bg-red-50 dark:hover:bg-red-900/20 text-sm flex items-center gap-2 text-red-600 dark:text-red-400">
                            <Trash2 className="w-4 h-4" /> Delete For Everyone
                        </button>
                    )}
                </div>
            )}

            {/* Forward Modal */}
            <ForwardModal
                isOpen={showForwardModal}
                onClose={() => setShowForwardModal(false)}
                message={selectedMessage}
                conversations={conversations}
            />
        </div>
    );
}
