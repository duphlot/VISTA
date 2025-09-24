import { useState } from 'react';
import { VideoUpload } from '@/components/custom/video-upload';
import { ChatInterface } from '@/components/custom/chat-interface';
import { SessionInfo } from '@/services/video-api';

export function Chat() {
    const [sessionInfo, setSessionInfo] = useState<SessionInfo | null>(null);

    const handleVideoUploaded = (session: SessionInfo) => {
        console.log('🎯 Video analysis completed:', session);
        setSessionInfo(session);
    };

    const handleBackToUpload = () => {
        setSessionInfo(null);
    };

    // If we have session info, render ChatInterface without extra containers
    if (sessionInfo) {
        return (
            <ChatInterface 
                sessionInfo={sessionInfo} 
                onBack={handleBackToUpload}
            />
        );
    }

    // Upload page with containers
    return (
        <div className="min-h-screen bg-gray-50 p-4">
            <div className="max-w-6xl mx-auto">
                {/* Header when uploading */}
                <div className="mb-8 text-center">
                    <h1 className="text-4xl font-bold text-gray-800 mb-4">
                        VISTA
                    </h1>
                    <p className="text-xl text-gray-600 mb-2">
                        Video Scene Graph Reasoning with Agents
                    </p>
                    <p className="text-gray-500">
                        for Vietnamese Video Understanding
                    </p>
                </div>

                <VideoUpload onVideoUploaded={handleVideoUploaded} />
            </div>
        </div>
    );
}
