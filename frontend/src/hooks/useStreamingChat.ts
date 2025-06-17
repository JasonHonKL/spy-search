
import { useState, useCallback } from 'react';
import { useToast } from '@/hooks/use-toast';
import { apiClient } from '@/services/apiClient';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  responseTime?: number;
}

interface UseStreamingChatProps {
  messages: Message[];
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>;
  setIsLoading: React.Dispatch<React.SetStateAction<boolean>>;
  currentConversationTitle?: string | null;
  onConversationCreated?: (title: string) => void;
  refreshConversations?: () => Promise<void>;
}

export const useStreamingChat = ({
  messages,
  setMessages,
  setIsLoading,
  currentConversationTitle,
  onConversationCreated,
  refreshConversations
}: UseStreamingChatProps) => {
  const [streamingMessageId, setStreamingMessageId] = useState<string | null>(null);
  const { toast } = useToast();

  const sendStreamingMessage = useCallback(async (
    messageContent: string,
    files: File[] = [],
    isDeepResearch: boolean = false
  ) => {
    // Check token status before making request
    try {
      const tokenStatus = await apiClient.getTokenStatus();
      const tokensNeeded = isDeepResearch ? 5 : 1;
      
      if (tokenStatus.daily_tokens_remaining < tokensNeeded) {
        toast({
          title: "Insufficient Tokens",
          description: `You need ${tokensNeeded} tokens for this search. You have ${tokenStatus.daily_tokens_remaining} remaining.`,
          variant: "destructive",
        });
        return;
      }
    } catch (error) {
      console.error('Failed to check token status:', error);
      toast({
        title: "Error",
        description: "Failed to check token status. Please try again.",
        variant: "destructive",
      });
      return;
    }

    const startTime = Date.now();
    const userMessageId = Date.now().toString();
    const assistantMessageId = (Date.now() + 1).toString();

    // Add user message
    const userMessage: Message = {
      id: userMessageId,
      type: 'user',
      content: messageContent,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setStreamingMessageId(assistantMessageId);

    // Add empty assistant message for streaming
    const assistantMessage: Message = {
      id: assistantMessageId,
      type: 'assistant',
      content: '',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, assistantMessage]);

    try {
      const token = localStorage.getItem('auth_token');
      if (!token) {
        throw new Error('Authentication required. Please login first.');
      }

      // Prepare form data for the backend
      const formData = new FormData();
      formData.append('messages', JSON.stringify([])); // Empty messages for now
      
      // Add files if any
      if (files && files.length > 0) {
        files.forEach(file => {
          formData.append('files', file);
        });
      }

      // Choose endpoint based on research type
      const endpoint = isDeepResearch 
        ? `http://localhost:8000/report/${encodeURIComponent(messageContent)}`
        : `http://localhost:8000/stream_completion/${encodeURIComponent(messageContent)}`;

      if (isDeepResearch) {
        // For deep research, use the report endpoint (non-streaming)
        const response = await fetch(endpoint, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          },
          body: formData,
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        const responseTime = Date.now() - startTime;
        
        setMessages(prev =>
          prev.map(msg =>
            msg.id === assistantMessageId
              ? { ...msg, content: data.report || 'No report generated', responseTime }
              : msg
          )
        );
      } else {
        // For quick response, use streaming endpoint
        const response = await fetch(endpoint, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          },
          body: formData,
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();
        let accumulatedContent = '';

        if (reader) {
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });
            accumulatedContent += chunk;
            
            setMessages(prev =>
              prev.map(msg =>
                msg.id === assistantMessageId
                  ? { ...msg, content: accumulatedContent }
                  : msg
              )
            );
          }
        }

        // Calculate response time in milliseconds
        const responseTime = Date.now() - startTime;
        setMessages(prev =>
          prev.map(msg =>
            msg.id === assistantMessageId
              ? { ...msg, responseTime }
              : msg
          )
        );
      }

    } catch (error) {
      console.error('Streaming error:', error);
      
      // Update the assistant message with error
      setMessages(prev =>
        prev.map(msg =>
          msg.id === assistantMessageId
            ? { ...msg, content: 'Sorry, I encountered an error while processing your request. Please try again.' }
            : msg
        )
      );

      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to send message. Please check your connection and try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
      setStreamingMessageId(null);
    }
  }, [messages, setMessages, setIsLoading, currentConversationTitle, onConversationCreated, refreshConversations, toast]);

  return { sendStreamingMessage, streamingMessageId };
};
