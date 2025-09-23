import React, { useState } from 'react';
import { Brain, History } from 'lucide-react';
import { ThoughtBox } from './thought-box';
import { motion } from 'framer-motion';

interface MessagePart {
  type: 'thought' | 'text' | 'function';
  content: string;
  author?: string;
  data?: unknown;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  parts?: MessagePart[];
}

interface RightSidebarTabsProps {
  messages: Message[];
}

type TabType = 'history' | 'thoughts';

export const RightSidebarTabs: React.FC<RightSidebarTabsProps> = ({ messages }) => {
  const [activeTab, setActiveTab] = useState<TabType>('history');
  const [selectedQuestionIndex, setSelectedQuestionIndex] = useState<number | undefined>(undefined);

  // Get all assistant messages with thoughts/functions
  const assistantMessages = messages.filter(m => m.role === 'assistant' && m.parts && m.parts.length > 0);
  
  // Get thoughts for selected question or latest if none selected
  const getThoughtsForQuestion = (questionIndex?: number) => {
    if (questionIndex === undefined) {
      // Return latest thoughts
      const latestAssistant = assistantMessages[assistantMessages.length - 1];
      return latestAssistant?.parts?.filter(
        part => part.type === 'thought' || part.type === 'function'
      ) || [];
    } else {
      // Find the assistant message that corresponds to this question
      // This is more complex as we need to find the right assistant response for the question
      const userQuestions = messages.filter(m => m.role === 'user');
      const userQuestion = userQuestions[questionIndex];
      
      if (!userQuestion) return [];
      
      // Find the assistant message that comes after this user question
      const userQuestionIndex = messages.findIndex(m => m.id === userQuestion.id);
      const nextAssistantMessage = messages
        .slice(userQuestionIndex + 1)
        .find(m => m.role === 'assistant' && m.parts && m.parts.length > 0);
        
      return nextAssistantMessage?.parts?.filter(
        part => part.type === 'thought' || part.type === 'function'
      ) || [];
    }
  };

  const allThoughtsAndFunctions = getThoughtsForQuestion(selectedQuestionIndex);
  
  // Deduplicate function calls and responses
  const thoughtsAndFunctions = (() => {
    const seen = new Set<string>();
    return allThoughtsAndFunctions.filter(item => {
      if (item.type === 'function') {
        // Create a unique key for function calls/responses
        const key = `${item.content}-${item.author}`;
        if (seen.has(key)) {
          return false; // Skip duplicate
        }
        seen.add(key);
      }
      return true;
    });
  })();


  const tabs = [
    {
      id: 'history' as TabType,
      label: 'Lịch sử',
      icon: History,
      count: messages.filter(m => m.role === 'user').length
    },
    {
      id: 'thoughts' as TabType,
      label: 'Suy nghĩ',
      icon: Brain,
      count: thoughtsAndFunctions.length
    }
  ];

  return (
    <div className="flex flex-col h-full">
      {/* Tab Headers */}
      <div className="flex border-b border-amber-200 bg-gradient-to-r from-yellow-50 to-amber-50">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 text-sm font-medium transition-colors relative ${
                isActive
                  ? 'text-amber-700 bg-amber-100 border border-amber-300'
                  : 'text-amber-600 hover:text-amber-800 hover:bg-amber-50'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
              {tab.count > 0 && (
                <span className={`ml-1 px-1.5 py-0.5 text-xs rounded-full ${
                  isActive 
                    ? 'bg-amber-600 text-white' 
                    : 'bg-amber-200 text-amber-700'
                }`}>
                  {tab.count}
                </span>
              )}
              
              {/* Active indicator */}
              {isActive && (
                <motion.div
                  layoutId="activeTab"
                  className="absolute bottom-0 left-0 right-0 h-0.5 bg-amber-600"
                  initial={false}
                  transition={{ type: "spring", stiffness: 500, damping: 30 }}
                />
              )}
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-hidden">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2 }}
          className="h-full"
        >
          
          {activeTab === 'thoughts' && (
            <div className="p-4 h-full overflow-y-auto bg-gradient-to-br from-yellow-50/30 to-amber-50/30">
              {thoughtsAndFunctions.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-32 text-center">
                  <Brain className="w-8 h-8 text-amber-400 mb-2" />
                  <p className="text-sm text-amber-600">
                    Chưa có suy nghĩ nào...
                  </p>
                  <p className="text-xs text-amber-500 mt-1">
                    {selectedQuestionIndex !== undefined 
                      ? 'Câu hỏi này chưa có suy nghĩ' 
                      : 'Hãy đặt câu hỏi để xem AI suy nghĩ'
                    }
                  </p>
                </div>
              ) : (
                <div className="space-y-3">
                  <div className="text-center mb-4">
                    <h3 className="text-sm font-medium text-amber-700 mb-1">
                      {selectedQuestionIndex !== undefined 
                        ? `Suy nghĩ cho câu #${selectedQuestionIndex + 1}`
                        : 'Quá trình suy nghĩ AI (Mới nhất)'
                      }
                    </h3>
                    <p className="text-xs text-amber-600">
                      Theo dõi cách AI phân tích câu hỏi
                    </p>
                    {selectedQuestionIndex !== undefined && (
                      <button
                        onClick={() => setSelectedQuestionIndex(undefined)}
                        className="mt-2 text-xs text-amber-600 hover:text-amber-800 transition-colors"
                      >
                        ← Quay lại suy nghĩ mới nhất
                      </button>
                    )}
                  </div>
                  
                  {thoughtsAndFunctions.map((thought, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                    >
                      <ThoughtBox 
                        author={thought.author || 'AI'}
                        content={thought.content} 
                        type={thought.type as 'thought' | 'function'}
                        compact={true}
                      />
                    </motion.div>
                  ))}
                </div>
              )}
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
};
