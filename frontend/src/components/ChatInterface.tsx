
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Bot, Sparkles, TrendingUp, Globe, Cpu, Heart, Bitcoin, Microscope, User } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { MessageList } from "./chat/MessageList";
import { ChatInput } from "./chat/ChatInput";
import { useStreamingChat } from "@/hooks/useStreamingChat";

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  responseTime?: number;
}

interface ChatInterfaceProps {
  agents: string[];
  messages: Message[];
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>;
  isLoading: boolean;
  setIsLoading: React.Dispatch<React.SetStateAction<boolean>>;
  currentConversationId?: string | null;
  onConversationCreated?: (title: string) => void;
  refreshConversations?: () => Promise<void>;
}

export const ChatInterface = ({ 
  agents, 
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

  const promptSuggestions = [
    { text: "Latest technology breakthroughs", icon: Cpu },
    { text: "Climate change recent developments", icon: Globe },
    { text: "Stock market analysis today", icon: TrendingUp },
    { text: "AI developments and news", icon: Bot },
    { text: "Space exploration updates", icon: Sparkles },
    { text: "Health and wellness trends", icon: Heart },
    { text: "Cryptocurrency market movements", icon: Bitcoin },
    { text: "Recent scientific discoveries", icon: Microscope }
  ];

  return (
    <div className="flex flex-col h-full max-w-none mx-auto bg-gradient-to-br from-gray-50/20 to-white/40 dark:from-gray-900/20 dark:to-gray-800/20">
      {messages.length === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center px-6 py-4 overflow-hidden">
          <div className="w-full max-w-4xl mx-auto text-center">
            {/* Hero Section */}
            <div className="mb-6">
              <div className="inline-flex items-center justify-center w-12 h-12 bg-gradient-to-br from-primary/90 via-blue-500/90 to-purple-500/90 rounded-2xl mb-3 shadow-lg shadow-primary/15">
                <Sparkles className="h-5 w-5 text-white" />
              </div>
              
              <h1 className="text-2xl font-light text-gray-900 dark:text-white mb-3 tracking-tight leading-tight">
                What would you like to
                <span className="block bg-gradient-to-r from-primary/90 via-blue-500/90 to-purple-500/90 bg-clip-text text-transparent font-light">
                  discover?
                </span>
              </h1>
              
              <p className="text-sm text-gray-600 dark:text-gray-300 font-light max-w-xl mx-auto leading-relaxed">
                Generate comprehensive intelligence reports with AI-powered research
              </p>
            </div>
            
            {/* Chat Input */}
            <div className="mb-6">
              <ChatInput
                input={input}
                setInput={setInput}
                isLoading={isLoading}
                agents={agents}
                onSendMessage={handleSendMessage}
                searchMode={searchMode}
                onSearchModeChange={setSearchMode}
              />
            </div>

            {/* Popular Topics Grid - Removed Coming Soon */}
            <div className="max-w-4xl mx-auto">
              <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-3 uppercase tracking-wider">
                Popular Topics
              </p>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 justify-items-center">
                {promptSuggestions.map((prompt, index) => (
                  <Button
                    key={prompt.text}
                    variant="ghost"
                    onClick={() => handlePromptClick(prompt.text)}
                    className="group h-auto p-3 rounded-xl border border-gray-200/40 dark:border-gray-700/40 bg-white/50 dark:bg-gray-800/30 backdrop-blur-sm hover:bg-white/70 dark:hover:bg-gray-800/50 hover:shadow-md hover:scale-[1.01] transition-all duration-200 text-left justify-start w-full max-w-[180px]"
                  >
                    <div className="flex flex-col items-center gap-2 w-full">
                      <div className="p-2 rounded-lg bg-gradient-to-br from-primary/8 to-blue-500/8 group-hover:from-primary/12 group-hover:to-blue-500/12 transition-all duration-200">
                        <prompt.icon className="h-3.5 w-3.5 text-primary/80 group-hover:scale-105 transition-transform duration-200" />
                      </div>
                      <span className="text-xs font-medium text-gray-700 dark:text-gray-200 group-hover:text-primary/90 transition-colors leading-tight text-center">
                        {prompt.text}
                      </span>
                    </div>
                  </Button>
                ))}
              </div>
            </div>
          </div>
        </div>
      ) : (
        <>
          <div className="flex justify-between items-center p-4 border-b border-gray-200/30 dark:border-gray-700/30 bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-gradient-to-br from-primary/90 to-blue-500/90 shadow-md">
                <Bot className="h-4 w-4 text-white" />
              </div>
              <div>
                <h2 className="text-base font-semibold text-gray-900 dark:text-white">Intelligence Assistant</h2>
                <p className="text-xs text-gray-500 dark:text-gray-400">AI-powered research</p>
              </div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={clearChat}
              className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 rounded-lg px-3 py-1.5 hover:bg-gray-100/40 dark:hover:bg-gray-800/40"
            >
              New Chat
            </Button>
          </div>

          <div className="flex-1 flex flex-col min-h-0">
            <ScrollArea className="flex-1 px-6">
              <div className="max-w-4xl mx-auto py-6">
                <MessageList 
                  messages={messages} 
                  isLoading={isLoading} 
                  isDeepResearch={false}
                  streamingMessageId={streamingMessageId}
                />
              </div>
            </ScrollArea>

            <div className="border-t border-gray-200/30 dark:border-gray-700/30 bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl">
              <div className="max-w-4xl mx-auto px-6 py-4">
                <ChatInput
                  input={input}
                  setInput={setInput}
                  isLoading={isLoading}
                  agents={agents}
                  onSendMessage={handleSendMessage}
                  searchMode={searchMode}
                  onSearchModeChange={setSearchMode}
                />
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default ChatInterface;
