import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { PlusCircle, MessageCircle, X, Trash2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { ScrollArea } from '@/components/ui/scroll-area';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  onDeleteChat?: (chatId: string) => void;
}

export function Sidebar({ isOpen, onClose, onDeleteChat }: SidebarProps) {
  const [chats, setChats] = useState<{ id: string; name: string; active: boolean }[]>([]);
  const [activeChat, setActiveChat] = useState<string | null>(null);

  const createNewChat = () => {
    const newChat = {
      id: Date.now().toString(),
      name: `Chat ${chats.length + 1}`,
      active: false,
    };
    setChats([...chats, newChat]);
  };

  const selectChat = (chatId: string) => {
    setActiveChat(chatId);
    setChats(chats.map(chat => ({
      ...chat,
      active: chat.id === chatId,
    })));
  };

  const handleDeleteChat = (e: React.MouseEvent, chatId: string) => {
    e.stopPropagation();
    if (onDeleteChat) {
      onDeleteChat(chatId);
      setChats(chats.filter(chat => chat.id !== chatId));
      if (activeChat === chatId) {
        setActiveChat(null);
      }
    }
  };

  return (
    <div
      className={cn(
        "fixed inset-y-0 left-0 w-64 bg-gradient-to-br from-yellow-50 to-amber-50 border-r border-amber-200 transform transition-transform duration-200 ease-in-out z-50 shadow-lg",
        isOpen ? "translate-x-0" : "-translate-x-full"
      )}
    >
      <div className="flex flex-col h-full p-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold text-amber-800">Chats</h2>
          <Button variant="ghost" size="icon" onClick={onClose} className="hover:bg-amber-100 text-amber-600 hover:text-amber-800">
            <X className="h-4 w-4" />
          </Button>
        </div>

        <Button
          onClick={createNewChat}
          className="mb-4 flex items-center gap-2 bg-gradient-to-r from-amber-500 to-yellow-500 hover:from-amber-600 hover:to-yellow-600 text-white border-0"
          variant="outline"
        >
          <PlusCircle className="h-4 w-4" />
          New Chat
        </Button>

        <ScrollArea className="flex-1">
          <div className="space-y-2">
            {chats.map((chat) => (
              <div
                key={chat.id}
                className="group relative"
              >
                <Button
                  variant={chat.active ? "secondary" : "ghost"}
                  className={`w-full justify-start gap-2 pr-8 ${
                    chat.active 
                      ? "bg-amber-200 text-amber-800 hover:bg-amber-300" 
                      : "text-amber-700 hover:bg-amber-100 hover:text-amber-800"
                  }`}
                  onClick={() => selectChat(chat.id)}
                >
                  <MessageCircle className="h-4 w-4" />
                  {chat.name}
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  className="absolute right-1 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity hover:bg-amber-100 text-amber-600 hover:text-amber-800"
                  onClick={(e) => handleDeleteChat(e, chat.id)}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </div>
        </ScrollArea>
      </div>
    </div>
  );
}
