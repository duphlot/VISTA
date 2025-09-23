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

    return (
        <div className="min-h-screen bg-gradient-to-br from-yellow-25 via-white to-amber-25 p-4">
            <div className="max-w-6xl mx-auto">
                {/* Header when uploading */}
                {!sessionInfo && (
                    <div className="mb-8 text-center">
                        <h1 className="text-4xl font-bold bg-gradient-to-r from-amber-600 to-yellow-600 bg-clip-text text-transparent mb-4">
                            VISTA
                        </h1>
                        <p className="text-xl text-amber-700 mb-2">
                            Video Scene Graph Reasoning with Agents
                        </p>
                        <p className="text-amber-600">
                            for Vietnamese Video Understanding
                        </p>
                    </div>
                )}

                {!sessionInfo ? (
                    <VideoUpload onVideoUploaded={handleVideoUploaded} />
                ) : (
                    <ChatInterface 
                        sessionInfo={sessionInfo} 
                        onBack={handleBackToUpload}
                    />
                )}
            </div>
        </div>
    );
}
