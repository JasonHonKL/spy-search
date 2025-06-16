
import { useRef, useEffect } from "react";
import { Bot, Loader2 } from "lucide-react";
import { MessageItem } from "./MessageItem";

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
  isDeepResearch: boolean;
  streamingMessageId?: string | null;
}

export const MessageList = ({ messages, isLoading, isDeepResearch, streamingMessageId }: MessageListProps) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="space-y-8">
      {messages.map((message) => (
        <MessageItem 
          key={message.id} 
          message={message}
          isStreaming={streamingMessageId === message.id}
        />
      ))}
      
      {isLoading && !streamingMessageId && (
        <div className="flex gap-6 justify-start">
          <div className="flex-shrink-0">
            <div className="w-10 h-10 rounded-full bg-muted flex items-center justify-center">
              <Bot className="h-5 w-5 text-muted-foreground" />
            </div>
          </div>
          <div className="flex-1 max-w-none">
            <div className="rounded-2xl px-6 py-4 bg-muted/50 border border-border/20">
              <div className="flex items-center gap-3">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-muted-foreground rounded-full animate-pulse"></div>
                  <div className="w-2 h-2 bg-muted-foreground rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-2 h-2 bg-muted-foreground rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                </div>
                <span className="text-sm text-muted-foreground">
                  Generating {isDeepResearch ? 'deep research' : 'response'}...
                </span>
              </div>
            </div>
          </div>
        </div>
      )}
      
      <div ref={messagesEndRef} />
    </div>
  );
};
