
import { useState } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { MessageList } from "./chat/MessageList";
import { ChatInput } from "./chat/ChatInput";
import { ChatHeader } from "./chat/ChatHeader";
import { WelcomeSection } from "./chat/WelcomeSection";
import { useStreamingChat } from "@/hooks/useStreamingChat";
import { useAuth } from "@/contexts/AuthContext";

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  responseTime?: number;
}

interface ChatInterfaceProps {
  messages: Message[];
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>;
  isLoading: boolean;
  setIsLoading: React.Dispatch<React.SetStateAction<boolean>>;
  currentConversationId?: string | null;
  onConversationCreated?: (title: string) => void;
  refreshConversations?: () => Promise<void>;
}

export const ChatInterface = ({ 
  messages, 
  setMessages, 
  isLoading, 
  setIsLoading,
  currentConversationId,
  onConversationCreated,
  refreshConversations
}: ChatInterfaceProps) => {
  const [input, setInput] = useState("");
  const [searchMode, setSearchMode] = useState(true);
  const { isAuthenticated, isLoading: authLoading } = useAuth();

  const { sendStreamingMessage, streamingMessageId } = useStreamingChat({
    messages,
    setMessages,
    setIsLoading,
    currentConversationTitle: currentConversationId,
    onConversationCreated,
    refreshConversations
  });

  const clearChat = () => {
    setMessages([]);
    setIsLoading(false);
  };

  const handleSendMessage = async (messageContent: string, files: File[], isDeepResearch: boolean) => {
    await sendStreamingMessage(messageContent, files, isDeepResearch);
  };

  const handlePromptClick = (promptText: string) => {
    setInput(promptText);
    setSearchMode(true);
  };

  // Show loading state while authentication is being checked
  if (authLoading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-sm text-muted-foreground">Checking authentication...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full max-w-none mx-auto bg-gradient-to-br from-gray-50/20 to-white/40 dark:from-gray-900/20 dark:to-gray-800/20">
      {/* Header - only show when there are messages */}
      {messages.length > 0 && <ChatHeader onClearChat={clearChat} />}

      {/* Main content area - always scrollable and full height */}
      <div className="flex-1 flex flex-col min-h-0">
        <ScrollArea className="flex-1">
          <div className="max-w-4xl mx-auto px-6 py-6">
            {messages.length === 0 ? (
              <WelcomeSection 
                onPromptClick={handlePromptClick}
                isAuthenticated={isAuthenticated}
              />
            ) : (
              <MessageList 
                messages={messages} 
                isLoading={isLoading} 
                isDeepResearch={false}
                streamingMessageId={streamingMessageId}
              />
            )}
          </div>
        </ScrollArea>

        {/* Fixed input at bottom - full width when chatting */}
        <div className="border-t border-gray-200/30 dark:border-gray-700/30 bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl">
          <div className={`mx-auto px-6 py-3 ${messages.length === 0 ? 'max-w-4xl' : 'max-w-full'}`}>
            <ChatInput
              input={input}
              setInput={setInput}
              isLoading={isLoading}
              onSendMessage={handleSendMessage}
              searchMode={searchMode}
              onSearchModeChange={setSearchMode}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
