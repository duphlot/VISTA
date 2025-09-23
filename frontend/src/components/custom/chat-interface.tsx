import React, { useState, useRef, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send, Bot, User, Video, BarChart3 } from "lucide-react";
import { SessionInfo, VideoAnalysisAPI } from '@/services/video-api';
import { useChatContext } from '@/context/ChatContext';

interface Message {
    id: string;
    text: string;
    isUser: boolean;
    timestamp: Date;
    videoPath?: string;
    hasVideo?: boolean;
}

interface ChatInterfaceProps {
    sessionInfo: SessionInfo;
    onBack: () => void;
}

export function ChatInterface({ sessionInfo, onBack }: ChatInterfaceProps) {
    const [messages, setMessages] = useState<Message[]>([]);
    const [inputText, setInputText] = useState('');
    const { isLoading, setIsLoading } = useChatContext();
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    useEffect(() => {
        const welcomeMessage: Message = {
            id: 'welcome',
            text: `Xin chào! Tôi đã phân tích video của bạn và tìm thấy ${sessionInfo.analysis_results?.keyframes_count || 0} khung hình quan trọng với ${sessionInfo.analysis_results?.scene_graph_relations || 0} mối quan hệ. Bạn có thể hỏi tôi bất kỳ câu hỏi nào về nội dung video!`,
            isUser: false,
            timestamp: new Date()
        };

        const messages = [welcomeMessage];
        if (sessionInfo.video_path) {
            const videoMessage: Message = {
                id: 'uploaded-video',
                text: 'Video đã tải lên:',
                isUser: true,
                timestamp: new Date(new Date().getTime() - 1000), 
                videoPath: sessionInfo.video_path,
                hasVideo: true
            };
            messages.unshift(videoMessage); 
        }

        setMessages(messages);
    }, [sessionInfo]);

    const handleSendMessage = async () => {
        if (!inputText.trim() || isLoading) return;

        const userMessage: Message = {
            id: Date.now().toString(),
            text: inputText,
            isUser: true,
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMessage]);
        const currentInput = inputText;
        setInputText('');
        setIsLoading(true);

        try {
            const response = await VideoAnalysisAPI.sendChatMessage(sessionInfo.session_id, currentInput);
            
            const botResponse: Message = {
                id: (Date.now() + 1).toString(),
                text: response.answer || 'Không thể tạo câu trả lời.',
                isUser: false,
                timestamp: new Date()
            };

            setMessages(prev => [...prev, botResponse]);
        } catch (error) {
            console.error('Error sending message:', error);
            const errorMessage: Message = {
                id: (Date.now() + 1).toString(),
                text: 'Xin lỗi, có lỗi xảy ra khi xử lý tin nhắn của bạn. Vui lòng thử lại.',
                isUser: false,
                timestamp: new Date()
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    };

    return (
        <div className="w-full max-w-6xl mx-auto relative bg-gradient-to-br from-yellow-50/20 via-white/40 to-amber-50/30">
            {/* Header Section */}
            <div className="bg-gradient-to-r from-white/80 to-yellow-50/80 backdrop-blur-md border border-amber-200/50 rounded-2xl p-5 m-4 shadow-lg">
                <div className="flex items-center justify-between mb-3">
                    <div>
                        <h1 className="text-xl font-bold text-amber-800 mb-1">
                            VISTA: Video Scene Graph Reasoning
                        </h1>
                        <p className="text-amber-700 text-xs">
                            Video Scene Graph Reasoning with Agents for Vietnamese Video Understanding
                        </p>
                    </div>
                    <Button 
                        variant="outline" 
                        onClick={onBack}
                        className="border-amber-300 text-amber-700 hover:bg-amber-100 text-sm px-3 py-1"
                    >
                        Quay lại
                    </Button>
                </div>
                
                {/* Analysis Summary */}
                <div className="flex gap-4 text-xs text-amber-800 bg-white/60 backdrop-blur-sm rounded-xl p-3 border border-amber-200/40">
                    <div className="flex items-center gap-2">
                        <BarChart3 className="h-3 w-3 text-amber-700" />
                        <span className="font-semibold">{sessionInfo.analysis_results?.keyframes_count || 0}</span>
                        <span>khung hình phân tích</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <Video className="h-3 w-3 text-amber-700" />
                        <span className="font-semibold">{sessionInfo.analysis_results?.scene_graph_relations || 0}</span>
                        <span>mối quan hệ cảnh</span>
                    </div>
                </div>
            </div>

            {/* Chat Messages */}
            <div className="px-4 pb-32">
                <div className="space-y-4">
                        {messages.map((message) => (
                            <div key={message.id}>
                                {/* Video message - display video outside message bubble */}
                                {message.hasVideo && message.videoPath && (
                                    <div className={`flex gap-2 mb-3 ${message.isUser ? 'justify-end' : 'justify-start'}`}>
                                        {!message.isUser && (
                                            <div className={`flex-shrink-0 w-7 h-7 ${message.hasVideo ? 'bg-gradient-to-br from-purple-400 to-blue-500' : 'bg-gradient-to-br from-gray-100 to-gray-200'} rounded-full flex items-center justify-center border ${message.hasVideo ? 'border-purple-300' : 'border-gray-300'}`}>
                                                <Video className="h-3 w-3 text-white" />
                                            </div>
                                        )}
                                        
                                        <div className="max-w-[80%]">
                                            <video 
                                                className="w-full max-w-sm rounded-lg shadow-lg"
                                                controls
                                                preload="metadata"
                                            >
                                                <source src={`http://localhost:8000/static/videos/${message.videoPath?.includes('/') ? message.videoPath.split('/').pop() : message.videoPath}`} type="video/mp4" />
                                                Trình duyệt của bạn không hỗ trợ video.
                                            </video>
                                            <p className="text-xs text-amber-600 mt-1">
                                                {message.timestamp.toLocaleTimeString('vi-VN')}
                                            </p>
                                        </div>

                                        {message.isUser && (
                                            <div className={`flex-shrink-0 w-7 h-7 ${message.hasVideo ? 'bg-gradient-to-br from-purple-400 to-blue-500' : 'bg-gradient-to-br from-gray-100 to-gray-200'} rounded-full flex items-center justify-center border ${message.hasVideo ? 'border-purple-300' : 'border-gray-300'}`}>
                                                <Video className="h-3 w-3 text-white" />
                                            </div>
                                        )}
                                    </div>
                                )}

                                {/* Text message - display in message bubble */}
                                {(!message.hasVideo || message.text !== 'Video đã tải lên:') && (
                                    <div className={`flex gap-2 ${message.isUser ? 'justify-end' : 'justify-start'}`}>
                                        {!message.isUser && (
                                            <div className="flex-shrink-0 w-7 h-7 bg-gradient-to-br from-amber-100 to-yellow-100 rounded-full flex items-center justify-center border border-amber-200">
                                                <Bot className="h-3 w-3 text-amber-700" />
                                            </div>
                                        )}
                                        
                                        <div
                                            className={`max-w-[80%] rounded-lg px-3 py-2 shadow-sm ${
                                                message.isUser
                                                    ? 'bg-gradient-to-r from-amber-500 to-yellow-500 text-white'
                                                    : 'bg-gradient-to-r from-yellow-50 to-amber-50 border border-amber-200 text-gray-800'
                                            }`}
                                        >
                                            <p className="text-sm leading-relaxed">{message.text}</p>
                                            <p className={`text-xs mt-1 ${
                                                message.isUser ? 'text-amber-100' : 'text-amber-600'
                                            }`}>
                                                {message.timestamp.toLocaleTimeString('vi-VN')}
                                            </p>
                                        </div>

                                        {message.isUser && !message.hasVideo && (
                                            <div className="flex-shrink-0 w-7 h-7 bg-gradient-to-br from-gray-100 to-gray-200 rounded-full flex items-center justify-center border border-gray-300">
                                                <User className="h-3 w-3 text-gray-600" />
                                            </div>
                                        )}
                                    </div>
                                )}
                            </div>
                        ))}
                        
                        {isLoading && (
                            <div className="flex gap-2 justify-start">
                                <div className="flex-shrink-0 w-7 h-7 bg-gradient-to-br from-amber-100 to-yellow-100 rounded-full flex items-center justify-center border border-amber-200">
                                    <Bot className="h-3 w-3 text-amber-700" />
                                </div>
                                <div className="bg-gradient-to-r from-yellow-50 to-amber-50 border border-amber-200 rounded-lg px-3 py-2 shadow-sm">
                                    <div className="flex space-x-1">
                                        <div className="w-2 h-2 bg-amber-400 rounded-full animate-bounce"></div>
                                        <div className="w-2 h-2 bg-amber-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                                        <div className="w-2 h-2 bg-amber-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                    <div ref={messagesEndRef} />
                </div>

            <div className="fixed bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-amber-50/80 via-yellow-50/60 to-transparent backdrop-blur-sm">
                <div className="w-full max-w-4xl mx-auto">
                    <div className="bg-gradient-to-r from-yellow-50 to-amber-100 border-2 border-amber-200 rounded-2xl p-4 shadow-xl backdrop-blur-sm">
                        <div className="flex gap-3">
                            <Input
                                value={inputText}
                                onChange={(e) => setInputText(e.target.value)}
                                onKeyPress={handleKeyPress}
                                placeholder="Hỏi VISTA về nội dung video..."
                                disabled={isLoading}
                                className="flex-1 border-2 border-amber-200 focus:ring-amber-400 focus:border-amber-400 text-sm bg-white/80 backdrop-blur-sm hover:bg-white transition-all duration-200 rounded-xl"
                            />
                            <Button 
                                onClick={handleSendMessage} 
                                disabled={!inputText.trim() || isLoading}
                                className="bg-gradient-to-r from-amber-500 to-yellow-500 hover:from-amber-600 hover:to-yellow-600 text-white border-0 px-5 shadow-lg hover:shadow-xl transition-all duration-200"
                                size="sm"
                            >
                                <Send className="h-4 w-4" />
                            </Button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}