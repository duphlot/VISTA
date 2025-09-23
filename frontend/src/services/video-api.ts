export interface ChatMessage {
    id: string;
    content: string;
    role: 'user' | 'assistant';
    parts?: MessagePart[];
}

export interface MessagePart {
    type: 'thought' | 'text' | 'function';
    content: string;
    author?: string;
    data?: unknown;
}

export interface VideoAnalysisRequest {
    question: string;
    session_id?: string;
}

export interface VideoAnalysisResponse {
    session_id: string;
    answer: string;
    keyframes_count: number;
    output_dir: string;
    relations: Record<string, string[]>;
    scene_graph: string[];
}

export interface SessionInfo {
    session_id: string;
    video_path?: string;
    status: string;
    created_at: string;
    analysis_results?: {
        keyframes_count: number;
        scene_graph_relations: number;
        video_duration?: number;
    };
}

export interface ChatRequest {
    message: string;
    session_id?: string;
}

export interface StreamChunk {
    parts: MessagePart[];
}

const API_BASE_URL = 'http://localhost:8000/api';

export class VideoAnalysisAPI {
    private static currentSessionId: string | null = null;

    static async createSession(): Promise<SessionInfo> {
        try {
            console.log('Creating session...');
            const response = await fetch(`${API_BASE_URL}/sessions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            console.log('Session response status:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const session = await response.json();
            console.log('Session created:', session);
            this.currentSessionId = session.session_id;
            return session;
        } catch (error) {
            console.error('Error creating session:', error);
            throw error;
        }
    }

    static async uploadVideo(file: File, sessionId?: string): Promise<{message: string, video_path: string, session_id: string}> {
        const session_id = sessionId || this.currentSessionId;
        if (!session_id) {
            throw new Error('No active session. Please create a session first.');
        }

        const formData = new FormData();
        formData.append('file', file);

        try {
            console.log('Uploading video to session:', session_id);
            const response = await fetch(`${API_BASE_URL}/sessions/${session_id}/upload`, {
                method: 'POST',
                body: formData,
            });

            console.log('Upload response status:', response.status);
            if (!response.ok) {
                const errorText = await response.text();
                console.error('Upload error response:', errorText);
                throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
            }

            const result = await response.json();
            console.log('Upload successful:', result);
            return result;
        } catch (error) {
            console.error('Error uploading video:', error);
            throw error;
        }
    }

    static async sendChatMessage(sessionId: string, message: string): Promise<any> {
        console.log('📤 Sending chat message:', { sessionId, message });
        
        const response = await fetch(`${API_BASE_URL}/sessions/${sessionId}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message }),
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('❌ Chat API error:', response.status, errorText);
            throw new Error(`Chat API error: ${response.status} ${errorText}`);
        }

        const result = await response.json();
        console.log('📥 Chat response:', result);
        return result;
    }
    
    static async getSessionStatus(sessionId: string): Promise<SessionInfo> {
        try {
            console.log('Getting session status:', sessionId);
            const response = await fetch(`${API_BASE_URL}/sessions/${sessionId}/status`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const status = await response.json();
            console.log('Session status:', status);
            return status;
        } catch (error) {
            console.error('Error getting session status:', error);
            throw error;
        }
    }

    static async analyzeVideo(question: string, sessionId?: string): Promise<VideoAnalysisResponse> {
        const session_id = sessionId || this.currentSessionId;
        if (!session_id) {
            throw new Error('No active session. Please create a session first.');
        }

        try {
            const response = await fetch(`${API_BASE_URL}/sessions/${session_id}/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question,
                    session_id
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error analyzing video:', error);
            throw error;
        }
    }

    static async chatWithVideo(message: string, sessionId?: string): Promise<ChatMessage> {
        const session_id = sessionId || this.currentSessionId;
        if (!session_id) {
            throw new Error('No active session. Please create a session first.');
        }

        try {
            const response = await fetch(`${API_BASE_URL}/sessions/${session_id}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message,
                    session_id
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error in chat:', error);
            throw error;
        }
    }

    static async getMessages(sessionId?: string): Promise<ChatMessage[]> {
        const session_id = sessionId || this.currentSessionId;
        if (!session_id) {
            throw new Error('No active session. Please create a session first.');
        }

        try {
            const response = await fetch(`${API_BASE_URL}/sessions/${session_id}/messages`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data.messages;
        } catch (error) {
            console.error('Error getting messages:', error);
            throw error;
        }
    }

    static async getSession(sessionId?: string): Promise<SessionInfo> {
        const session_id = sessionId || this.currentSessionId;
        if (!session_id) {
            throw new Error('No active session. Please create a session first.');
        }

        try {
            const response = await fetch(`${API_BASE_URL}/sessions/${session_id}`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error getting session:', error);
            throw error;
        }
    }

    static async deleteSession(sessionId?: string): Promise<void> {
        const session_id = sessionId || this.currentSessionId;
        if (!session_id) {
            throw new Error('No active session. Please create a session first.');
        }

        try {
            const response = await fetch(`${API_BASE_URL}/sessions/${session_id}`, {
                method: 'DELETE',
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            if (session_id === this.currentSessionId) {
                this.currentSessionId = null;
            }
        } catch (error) {
            console.error('Error deleting session:', error);
            throw error;
        }
    }

    static async listSessions(): Promise<SessionInfo[]> {
        try {
            const response = await fetch(`${API_BASE_URL}/sessions`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data.sessions;
        } catch (error) {
            console.error('Error listing sessions:', error);
            throw error;
        }
    }

    static getCurrentSessionId(): string | null {
        return this.currentSessionId;
    }

    static setCurrentSessionId(sessionId: string): void {
        this.currentSessionId = sessionId;
    }
}

// Legacy ChatAPI wrapper for backward compatibility
export class ChatAPI {
    static async sendMessage(
        message: string,
        sessionId: string,
        onChunk: (chunk: StreamChunk) => void
    ): Promise<any> {
        try {
            // Set current session
            VideoAnalysisAPI.setCurrentSessionId(sessionId);
            
            // Send chat message
            const response = await VideoAnalysisAPI.chatWithVideo(message, sessionId);
            
            // Simulate streaming by calling onChunk with the complete response
            if (response && response.parts) {
                onChunk({ parts: response.parts });
            } else {
                // Fallback for simple text response
                onChunk({
                    parts: [
                        {
                            type: 'text',
                            content: response.content || '',
                            author: 'Video Analyst'
                        }
                    ]
                });
            }

            return response;
        } catch (error) {
            console.error('Error in sendMessage:', error);
            throw error;
        }
    }

    static async createSession(userId: string): Promise<string> {
        try {
            const session = await VideoAnalysisAPI.createSession();
            return session.session_id;
        } catch (error) {
            console.error('Error creating session:', error);
            throw error;
        }
    }
}

export default VideoAnalysisAPI;