import { useState, useRef } from 'react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Upload, Video, X, CheckCircle, AlertCircle, BarChart3, Clock, FileVideo, Loader2 } from 'lucide-react';
import { VideoAnalysisAPI, SessionInfo } from '../../services/video-api';

interface VideoUploadProps {
    onVideoUploaded: (sessionInfo: SessionInfo) => void;
    sessionId?: string;
}

export function VideoUpload({ onVideoUploaded, sessionId }: VideoUploadProps) {
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [isUploading, setIsUploading] = useState(false);
    const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'analyzing' | 'success' | 'error'>('idle');
    const [error, setError] = useState<string>('');
    const [analysisResults, setAnalysisResults] = useState<SessionInfo | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file) {
            // Validate file type
            if (!file.type.startsWith('video/')) {
                setError('Vui lòng chọn file video hợp lệ');
                return;
            }
            
            // Validate file size (max 100MB)
            const maxSize = 100 * 1024 * 1024; // 100MB
            if (file.size > maxSize) {
                setError('File video quá lớn. Vui lòng chọn file nhỏ hơn 100MB');
                return;
            }

            setSelectedFile(file);
            setError('');
            setUploadStatus('idle');
        }
    };

    const handleUpload = async () => {
        if (!selectedFile) return;

        setIsUploading(true);
        setUploadStatus('uploading');
        setError('');

        try {
            let currentSessionId = sessionId;
            
            // Create session if not provided
            if (!currentSessionId) {
                const session = await VideoAnalysisAPI.createSession();
                currentSessionId = session.session_id;
            }

            // Upload video
            await VideoAnalysisAPI.uploadVideo(selectedFile, currentSessionId);
            
            setUploadStatus('analyzing');
            
            // Poll for analysis completion
            let analysisComplete = false;
            let attempts = 0;
            const maxAttempts = 30; // 30 seconds timeout
            
            while (!analysisComplete && attempts < maxAttempts) {
                await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1 second
                
                try {
                    const sessionStatus = await VideoAnalysisAPI.getSessionStatus(currentSessionId);
                    console.log('Session status check:', sessionStatus);
                    
                    if (sessionStatus.status === 'completed') {
                        analysisComplete = true;
                        setAnalysisResults(sessionStatus);
                        setUploadStatus('success');
                        
                        console.log('✅ Analysis completed! Session:', sessionStatus);
                        // Call the callback with full session info
                        onVideoUploaded(sessionStatus);
                        return; // Exit the function completely
                    }
                } catch (statusError) {
                    console.warn('Status check failed:', statusError);
                }
                
                attempts++;
            }
            
            if (!analysisComplete) {
                throw new Error('Video analysis timeout. Please try again.');
            }
            
        } catch (error) {
            console.error('Error uploading video:', error);
            setError(error instanceof Error ? error.message : 'Lỗi khi upload video');
            setUploadStatus('error');
        } finally {
            setIsUploading(false);
        }
    };

    const handleRemoveFile = () => {
        setSelectedFile(null);
        setUploadStatus('idle');
        setError('');
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    };

    const triggerFileSelect = () => {
        fileInputRef.current?.click();
    };

    return (
        <Card className="w-full border-yellow-200 shadow-sm">
            <CardHeader className="bg-gradient-to-r from-yellow-50 to-amber-50 border-b border-yellow-200">
                <CardTitle className="flex items-center gap-2 text-amber-800">
                    <Video className="h-5 w-5 text-amber-600" />
                    VISTA: Video Analysis
                </CardTitle>
                <p className="text-sm text-amber-700">
                    Upload video để phân tích với Scene Graph Reasoning AI
                </p>
            </CardHeader>
            <CardContent className="p-6">
                {/* Hidden file input */}
                <Input
                    ref={fileInputRef}
                    type="file"
                    accept="video/*"
                    onChange={handleFileSelect}
                    className="hidden"
                />

                {/* Upload area */}
                {!selectedFile ? (
                    <div
                        onClick={triggerFileSelect}
                        className="border-2 border-dashed border-yellow-300 rounded-lg p-8 text-center cursor-pointer hover:border-amber-400 bg-gradient-to-br from-yellow-25 to-amber-25 hover:bg-amber-50 transition-colors"
                    >
                        <div className="flex flex-col items-center gap-4">
                            <div className="p-3 rounded-full bg-gradient-to-br from-amber-100 to-yellow-100 border border-amber-200">
                                <Upload className="h-8 w-8 text-amber-600" />
                            </div>
                            <div>
                                <p className="text-lg font-medium text-amber-800 mb-2">
                                    Kéo thả video hoặc click để chọn
                                </p>
                                <p className="text-sm text-amber-600">
                                    Hỗ trợ: MP4, AVI, MOV (tối đa 100MB)
                                </p>
                            </div>
                        </div>
                    </div>
                ) : (
                    <div className="space-y-3">
                        {/* Selected file info */}
                        <div className="flex items-center justify-between p-3 bg-gradient-to-r from-yellow-50 to-amber-50 border border-yellow-200 rounded-lg">
                            <div className="flex items-center gap-3">
                                <div className="p-2 rounded-lg bg-gradient-to-br from-amber-100 to-yellow-100 border border-amber-200">
                                    <Video className="h-6 w-6 text-amber-600" />
                                </div>
                                <div>
                                    <p className="font-medium text-sm text-amber-800">{selectedFile.name}</p>
                                    <p className="text-xs text-amber-600">
                                        {(selectedFile.size / (1024 * 1024)).toFixed(1)} MB
                                    </p>
                                </div>
                            </div>
                            <Button
                                variant="ghost"
                                size="sm"
                                onClick={handleRemoveFile}
                                className="text-amber-700 hover:bg-amber-100"
                                disabled={isUploading}
                            >
                                <X className="h-4 w-4" />
                            </Button>
                        </div>

                        {/* Upload button */}
                        <Button
                            onClick={handleUpload}
                            disabled={isUploading}
                            className="w-full bg-gradient-to-r from-amber-500 to-yellow-500 hover:from-amber-600 hover:to-yellow-600 text-white border-0"
                        >
                            {uploadStatus === 'uploading' && (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Đang upload...
                                </>
                            )}
                            {uploadStatus === 'analyzing' && (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Đang phân tích với VISTA...
                                </>
                            )}
                            {uploadStatus === 'idle' && 'Phân tích với VISTA'}
                            {uploadStatus === 'success' && (
                                <>
                                    <CheckCircle className="mr-2 h-4 w-4" />
                                    Phân tích hoàn thành!
                                </>
                            )}
                            {uploadStatus === 'error' && 'Thử lại'}
                        </Button>
                    </div>
                )}

                {/* Status messages */}
                {uploadStatus === 'success' && analysisResults && (
                    <div className="space-y-3">
                        <div className="flex items-center gap-2 text-green-600 dark:text-green-400 text-sm">
                            <CheckCircle className="h-4 w-4" />
                            Video đã được phân tích thành công!
                        </div>
                        
                        {analysisResults.analysis_results && (
                            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg border border-green-200 dark:border-green-800">
                                <h4 className="font-medium text-green-800 dark:text-green-200 mb-2 flex items-center gap-2">
                                    <BarChart3 className="h-4 w-4" />
                                    Kết quả phân tích
                                </h4>
                                <div className="space-y-2 text-sm text-green-700 dark:text-green-300">
                                    <div className="flex items-center gap-2">
                                        <FileVideo className="h-4 w-4" />
                                        <span>Keyframes: {analysisResults.analysis_results.keyframes_count}</span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <Clock className="h-4 w-4" />
                                        <span>Scene graph relations: {analysisResults.analysis_results.scene_graph_relations}</span>
                                    </div>
                                </div>
                                <p className="text-xs text-green-600 dark:text-green-400 mt-2">
                                    Bạn có thể bắt đầu đặt câu hỏi về video này!
                                </p>
                            </div>
                        )}
                    </div>
                )}

                {error && (
                    <div className="flex items-center gap-2 text-red-600 dark:text-red-400 text-sm">
                        <AlertCircle className="h-4 w-4" />
                        {error}
                    </div>
                )}

                {uploadStatus === 'uploading' && (
                    <div className="flex items-center gap-2 text-blue-600 dark:text-blue-400 text-sm">
                        <Upload className="h-4 w-4 animate-pulse" />
                        Đang upload video, vui lòng đợi...
                    </div>
                )}
                
                {uploadStatus === 'analyzing' && (
                    <div className="flex items-center gap-2 text-blue-600 dark:text-blue-400 text-sm">
                        <BarChart3 className="h-4 w-4 animate-spin" />
                        Đang phân tích video và tạo scene graph...
                    </div>
                )}
            </CardContent>
        </Card>
    );
}