import React, { useState } from 'react';
import API from '../api/axios';

function Chatbot() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    const sendMessage = async () => {
        if (!input.trim()) return;

        const userMessage = { text: input, sender: 'user' };
        setMessages([...messages, userMessage]);
        setInput('');
        setLoading(true);

        try {
            const response = await API.post('chat/', { query: input });
            const botMessage = { text: response.data.response, sender: 'bot' };
            setMessages(prev => [...prev, botMessage]);
        } catch (error) {
            let errorMessage = 'Sorry, I encountered an error. Please try again.';
            
            if (error?.response?.status === 401) {
                errorMessage = 'You must be logged in to use the chatbot. Please log in first.';
            } else if (error?.response?.data?.error) {
                errorMessage = error.response.data.error;
            } else if (error?.response?.data?.detail) {
                errorMessage = error.response.data.detail;
            }
            
            const botMessage = { 
                text: errorMessage, 
                sender: 'bot' 
            };
            setMessages(prev => [...prev, botMessage]);
        } finally {
            setLoading(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    return (
        <div className="max-w-4xl mx-auto p-6">
            <h1 className="text-3xl font-bold mb-6">🤖 Library Assistant</h1>
            
            <div className="bg-white rounded-lg shadow-lg p-6">
                <div className="h-96 overflow-y-auto mb-4 p-4 bg-gray-50 rounded-lg">
                    {messages.length === 0 ? (
                        <div className="text-center text-gray-500 mt-20">
                            <p className="text-lg mb-2">👋 Hello! I'm your library assistant.</p>
                            <p>Ask me about books, authors, or request help with library operations.</p>
                        </div>
                    ) : (
                        messages.map((msg, index) => (
                            <div key={index} className={`mb-4 ${msg.sender === 'user' ? 'text-right' : 'text-left'}`}>
                                <div className={`inline-block p-3 rounded-lg max-w-xs ${
                                    msg.sender === 'user' 
                                        ? 'bg-blue-500 text-white' 
                                        : 'bg-gray-200 text-gray-800'
                                }`}>
                                    {msg.text}
                                </div>
                            </div>
                        ))
                    )}
                    {loading && (
                        <div className="text-left mb-4">
                            <div className="inline-block p-3 rounded-lg bg-gray-200 text-gray-800">
                                <div className="flex items-center">
                                    <div className="animate-spin mr-2">⚙️</div>
                                    Thinking...
                                </div>
                            </div>
                        </div>
                    )}
                </div>
                
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="Ask me about books, authors, or library operations..."
                        className="flex-1 p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        disabled={loading}
                    />
                    <button
                        onClick={sendMessage}
                        disabled={loading || !input.trim()}
                        className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {loading ? (
                            <div className="flex items-center">
                                <div className="animate-spin mr-2">⚙️</div>
                                Sending...
                            </div>
                        ) : (
                            'Send'
                        )}
                    </button>
                </div>
                
                <div className="mt-4 text-sm text-gray-500">
                    <p>💡 Try asking:</p>
                    <ul className="list-disc list-inside mt-1">
                        <li>"What books do you have about fantasy?"</li>
                        <li>"Create a book called 'The Great Adventure'"</li>
                        <li>"List all authors in the library"</li>
                        <li>"What's available for borrowing?"</li>
                    </ul>
                </div>
            </div>
        </div>
    );
}

export default Chatbot;
