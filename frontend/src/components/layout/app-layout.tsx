import { useState, ReactNode } from "react";
import { Menu, X } from "lucide-react";
import { AgentCommunication } from "../custom/agent-communication";
import { RightSidebarTabs } from "../custom/right-sidebar-tabs";
import { useChatContext } from "../../context/ChatContext";

interface LayoutProps {
  children: ReactNode;
}

export function AppLayout({ children }: LayoutProps) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isRightSidebarOpen, setIsRightSidebarOpen] = useState(true);
  const { isLoading, messages } = useChatContext();

  // Check if we have thoughts/functions to show
  const hasThoughtsOrFunctions = messages.some(m => 
    m.role === 'assistant' && 
    m.parts && 
    m.parts.some(p => p.type === 'thought' || p.type === 'function')
  );

  return (
    <div className="relative h-screen bg-overlay dark:bg-overlay overflow-hidden">
      {/* Left Sidebar - Combined Toolbar + Storage - Fixed */}
      <div className={`${isSidebarOpen ? 'w-64' : 'w-14'} bg-gradient-to-br from-yellow-50 to-amber-50 shadow-lg rounded-r-2xl transition-all duration-300 ease-in-out flex flex-col overflow-hidden border border-amber-200 fixed top-0 left-0 h-screen z-20`}>
        {/* Header with Logo and Toggle */}
        <div className="p-3 flex items-center justify-between">
          <div className="w-8 flex justify-center">
            <img 
              src="/favicon.png" 
              alt="Logo" 
              className="w-8 h-8 cursor-pointer hover:opacity-80 transition-opacity"
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            />
          </div>
          <div className={`transition-all duration-300 ${isSidebarOpen ? 'opacity-100 w-6' : 'opacity-0 w-0'} overflow-hidden`}>
            <button 
              onClick={() => setIsSidebarOpen(false)}
              className="p-1 hover:bg-amber-100 transition-colors rounded text-amber-600"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
          </div>
        </div>

        {/* Tools */}
        <div className="flex flex-col space-y-2 px-2 border-b border-amber-200 pb-4">
          {/* New Chat */}
          <button className="flex items-center gap-3 p-2 hover:bg-amber-100 transition-colors rounded-lg">
            <div className="w-5 flex justify-center flex-shrink-0">
              <svg className="w-5 h-5 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
            </div>
            <span className={`text-sm text-amber-700 whitespace-nowrap transition-all duration-300 ${isSidebarOpen ? 'opacity-100 w-auto' : 'opacity-0 w-0'} overflow-hidden`}>
              Chat mới
            </span>
          </button>

          {/* Search */}
          <button className="flex items-center gap-3 p-2 hover:bg-amber-100 transition-colors rounded-lg">
            <div className="w-5 flex justify-center flex-shrink-0">
              <svg className="w-5 h-5 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <span className={`text-sm text-amber-700 whitespace-nowrap transition-all duration-300 ${isSidebarOpen ? 'opacity-100 w-auto' : 'opacity-0 w-0'} overflow-hidden`}>
              Tìm kiếm
            </span>
          </button>

          {/* Settings */}
          <button className="flex items-center gap-3 p-2 hover:bg-amber-100 transition-colors rounded-lg">
            <div className="w-5 flex justify-center flex-shrink-0">
              <svg className="w-5 h-5 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            <span className={`text-sm text-amber-700 whitespace-nowrap transition-all duration-300 ${isSidebarOpen ? 'opacity-100 w-auto' : 'opacity-0 w-0'} overflow-hidden`}>
              Cài đặt
            </span>
          </button>

          {/* Help */}
          <button className="flex items-center gap-3 p-2 hover:bg-amber-100 transition-colors rounded-lg">
            <div className="w-5 flex justify-center flex-shrink-0">
              <svg className="w-5 h-5 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <span className={`text-sm text-amber-700 whitespace-nowrap transition-all duration-300 ${isSidebarOpen ? 'opacity-100 w-auto' : 'opacity-0 w-0'} overflow-hidden`}>
              Trợ giúp
            </span>
          </button>
        </div>

        {/* Chat History Section - Only show when expanded */}
        {isSidebarOpen && (
          <>
            <div className="p-4">
              <h3 className="text-sm font-semibold text-amber-800 mb-3">
                Lưu trữ section
              </h3>
              
              <div className="relative mb-4">
                <input 
                  type="text" 
                  placeholder="Tìm kiếm đoạn chat..."
                  className="w-full p-2 border border-amber-300 rounded-lg bg-amber-50 text-amber-800 placeholder-amber-600 text-sm focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
                />
                <svg className="absolute right-2 top-2 w-4 h-4 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
            </div>

            {/* Chat History List */}
            <div className="flex-1 overflow-y-auto px-4 pb-4">
              <div className="space-y-2">
                <div className="text-xs text-amber-600 mb-2">Hôm nay</div>
                
                <div className="p-2 hover:bg-amber-100 rounded-lg cursor-pointer transition-colors">
                  <div className="text-sm font-medium text-amber-800 truncate">
                    Video phân tích về con nít chơi đồ chơi
                  </div>
                  <div className="text-xs text-amber-600 mt-1">
                    2 giờ trước
                  </div>
                </div>
                
                <div className="p-2 hover:bg-amber-100 rounded-lg cursor-pointer transition-colors">
                  <div className="text-sm font-medium text-amber-800 truncate">
                    Phân tích video bãi biển
                  </div>
                  <div className="text-xs text-amber-600 mt-1">
                    1 ngày trước
                  </div>
                </div>
              </div>
            </div>
          </>
        )}

        {/* Avatar at bottom */}
        <div className="p-3 border-t border-amber-300 mt-auto">
          <div className="w-8 h-8 bg-gradient-to-br from-amber-400 to-yellow-500 rounded-full flex items-center justify-center cursor-pointer hover:bg-amber-600 transition-colors">
            <span className="text-sm text-white">U</span>
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className={`h-screen overflow-hidden ${isSidebarOpen ? 'pl-64' : 'pl-14'} ${isRightSidebarOpen ? 'pr-80' : 'pr-12'} transition-all duration-300`}>
        {children}
      </div>

      {/* Right Sidebar - Fixed */}
      <div className={`${isRightSidebarOpen ? 'w-80' : 'w-12'} bg-gradient-to-br from-yellow-50 to-amber-50 backdrop-blur-sm shadow-lg border-l border-amber-300 rounded-l-lg transition-all duration-300 ease-in-out flex flex-col fixed top-0 right-0 h-screen z-20`}>
        {/* Toggle Button */}
        <div className="p-3 border-b border-amber-300 flex justify-between items-center">
          {isRightSidebarOpen && (
            <h2 className="text-sm font-medium text-amber-800">
              Hệ thống AI
            </h2>
          )}
          <button
            onClick={() => setIsRightSidebarOpen(!isRightSidebarOpen)}
            className="p-1.5 hover:bg-amber-100 rounded-md transition-colors"
          >
            {isRightSidebarOpen ? (
              <X className="w-4 h-4 text-amber-600" />
            ) : (
              <Menu className="w-4 h-4 text-amber-600" />
            )}
          </button>
        </div>

        {/* Content - Only show when open */}
        {isRightSidebarOpen && (
          <div className="flex-1 flex flex-col overflow-hidden">
            {/* Sidebar Content with Tabs */}
            <div className="flex-1 overflow-hidden">
              {hasThoughtsOrFunctions || messages.some(m => m.role === 'user') ? (
                /* Show Tabs when we have content */
                <RightSidebarTabs messages={messages} />
              ) : (
                /* Show Agent Communication when no thoughts */
                <AgentCommunication isActive={isLoading} />
              )}
            </div>
          </div>
        )}

        {/* Collapsed State - Show minimal info */}
        {!isRightSidebarOpen && (
          <div className="flex-1 p-2 flex flex-col items-center space-y-4 mt-4">
            <div className="w-8 h-8 bg-amber-100 rounded-full overflow-hidden border-2 border-amber-200 flex items-center justify-center">
              <img src="/icons/1ea04601-d485-402a-bc34-a96100f40737.jpeg" alt="AI" className="w-full h-full object-cover" />
            </div>
            <div className={`w-2 h-2 rounded-full ${isLoading ? 'bg-amber-500 animate-pulse' : 'bg-gray-400'}`}></div>
          </div>
        )}
      </div>
    </div>
  );
}
