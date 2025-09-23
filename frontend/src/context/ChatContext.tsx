import React, { createContext, useContext, useState, ReactNode } from 'react';

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

interface ChatContextType {
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
  messages: Message[];
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const useChatContext = () => {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error('useChatContext must be used within a ChatProvider');
  }
  return context;
};

interface ChatProviderProps {
  children: ReactNode;
}

export const ChatProvider: React.FC<ChatProviderProps> = ({ children }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);

  return (
    <ChatContext.Provider value={{ isLoading, setIsLoading, messages, setMessages }}>
      {children}
    </ChatContext.Provider>
  );
};
