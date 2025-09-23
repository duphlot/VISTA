import { ChatInput } from "@/components/custom/chatinput";
import { PreviewMessage } from "../../components/custom/message";
import { LoadingAnimation } from "../../components/custom/loading-animation";
import { VideoUpload } from "../../components/custom/video-upload";
import { useScrollToBottom } from '@/components/custom/use-scroll-to-bottom';
import { useState } from "react";
import { Overview } from "@/components/custom/overview";
// import { Header } from "@/components/custom/header";
import {v4 as uuidv4} from 'uuid';
import { VideoAnalysisAPI, ChatAPI, StreamChunk } from '../../services/video-api';
import { useChatContext } from "../../context/ChatContext";

export function Chat() {
  const [messagesContainerRef, messagesEndRef] = useScrollToBottom<HTMLDivElement>();
  const [question, setQuestion] = useState<string>("");
  const [sessionId, setSessionId] = useState<string>("");
  const [hasVideo, setHasVideo] = useState<boolean>(false);
  const [videoFileName, setVideoFileName] = useState<string>("");
  const { isLoading, setIsLoading, messages, setMessages } = useChatContext();

  const handleVideoUploaded = (newSessionId: string, fileName: string) => {
    setSessionId(newSessionId);
    setHasVideo(true);
    setVideoFileName(fileName);
    
    // Add system message about video upload
    const videoUploadMessage = {
      content: `Video "${fileName}" đã được upload thành công! Bạn có thể đặt câu hỏi về video này.`,
      role: "assistant" as const,
      id: uuidv4(),
      parts: [
        {
          type: "text" as const,
          content: `Video "${fileName}" đã được upload thành công! Bạn có thể đặt câu hỏi về video này.`,
          author: "System"
        }
      ]
    };
    
    setMessages([videoUploadMessage]);
  };

  async function handleSubmit(text?: string) {
    if (isLoading) return;

    const messageText = text || question;
    if (!messageText.trim()) return;

    if (!hasVideo || !sessionId) {
      // Show error message
      const errorMessage = {
        content: "Vui lòng upload video trước khi đặt câu hỏi.",
        role: "assistant" as const,
        id: uuidv4()
      };
      setMessages(prev => [...prev, errorMessage]);
      return;
    }

    console.log('Before clear:', question);
    setQuestion("");
    console.log('After clear:', question);
    setIsLoading(true);
    
    const userMessageId = uuidv4();
    const assistantMessageId = uuidv4();
    
    // Add user message
    setMessages(prev => [...prev, { 
      content: messageText, 
      role: "user", 
      id: userMessageId 
    }]);

    try {
      // Initialize assistant message
      setMessages(prev => [...prev, { 
        content: "", 
        role: "assistant", 
        id: assistantMessageId 
      }]);

      // Determine if this is the first question (video analysis) or follow-up chat
      const isFirstQuestion = messages.length <= 1; // Only system message exists

      let result;
      if (isFirstQuestion) {
        // First question - analyze video
        result = await VideoAnalysisAPI.analyzeVideo(messageText, sessionId);
        
        // Update messages with analysis result
        setMessages(prev => {
          const newMessages = [...prev];
          const lastMessageIndex = newMessages.length - 1;
          if (newMessages[lastMessageIndex]?.role === "assistant") {
            newMessages[lastMessageIndex] = {
              ...newMessages[lastMessageIndex],
              content: result.answer,
              parts: [
                {
                  type: 'text',
                  content: result.answer,
                  author: 'Video Analyst'
                }
              ]
            };
          }
          return newMessages;
        });
      } else {
        // Follow-up chat about the video
        result = await VideoAnalysisAPI.chatWithVideo(messageText, sessionId);
        
        // Update messages with chat result
        setMessages(prev => {
          const newMessages = [...prev];
          const lastMessageIndex = newMessages.length - 1;
          if (newMessages[lastMessageIndex]?.role === "assistant") {
            newMessages[lastMessageIndex] = {
              ...newMessages[lastMessageIndex],
              content: result.content,
              parts: result.parts || [
                {
                  type: 'text',
                  content: result.content,
                  author: 'Video Analyst'
                }
              ]
            };
          }
          return newMessages;
        });
      }

    } catch (error) {
      console.error("API error:", error);
      // Show error message
      setMessages(prev => [...prev.slice(0, -1), { 
        content: "Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại.", 
        role: "assistant", 
        id: assistantMessageId 
      }]);
    } finally {
      setIsLoading(false);
    }
  }

      // Update session ID if it's a new one
      if (result.sessionId && result.sessionId !== sessionId) {
        setSessionId(result.sessionId);
      }
    } catch (error) {
      console.error("API error:", error);
      // Show error message
      setMessages(prev => [...prev.slice(0, -1), { 
        content: "Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại.", 
        role: "assistant", 
        id: assistantMessageId 
      }]);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="flex flex-col min-w-0 h-dvh bg-transparent">
      {/* <Header/> */}
      <div className="flex flex-col min-w-0 gap-6 flex-1 overflow-y-scroll pt-4" ref={messagesContainerRef}>
        {messages.length == 0 && <Overview />}
        {messages.map((message, index) => (
          <PreviewMessage 
            key={index} 
            message={message} 
            hideActions={isLoading && index === messages.length - 1}
          />
        ))}
        {isLoading && <LoadingAnimation />}
        <div ref={messagesEndRef} className="shrink-0 min-w-[24px] min-h-[24px]"/>
      </div>
      <div className="flex mx-auto px-4 bg-transparent pb-4 md:pb-6 gap-2 w-full md:max-w-3xl">
        <ChatInput  
          question={question}
          setQuestion={setQuestion}
          onSubmit={handleSubmit}
          isLoading={isLoading}
        />
      </div>
    </div>
  );
}