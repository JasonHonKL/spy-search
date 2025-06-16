
import { useState, useCallback } from 'react';
import { conversationManager } from '@/components/ConversationSidebar';

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

  const sendStreamingMessage = useCallback(async (
    messageContent: string,
    files: File[],
    isDeepResearch: boolean
  ) => {
    const startTime = Date.now();
    
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: messageContent,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    // Determine conversation title
    let conversationTitle = currentConversationTitle;
    if (!conversationTitle) {
      conversationTitle = messageContent.substring(0, 30) + "...";
      onConversationCreated?.(conversationTitle);
    }

    // Save user message immediately
    await conversationManager.saveMessage(conversationTitle, 'user', messageContent);
    
    // Refresh conversations after saving user message
    if (refreshConversations) {
      await refreshConversations();
    }

    // Create assistant message placeholder for streaming
    const assistantMessageId = (Date.now() + 1).toString();
    const assistantMessage: Message = {
      id: assistantMessageId,
      type: 'assistant',
      content: '',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, assistantMessage]);
    setStreamingMessageId(assistantMessageId);

    try {
      const endpoint = isDeepResearch ? 'report' : 'stream_completion';
      const encodedQuery = encodeURIComponent(messageContent);
      
      // Convert messages to the required format
      const allMessages = [...messages, userMessage];
      const formattedMessages = allMessages.map(msg => ({
        role: msg.type === 'user' ? 'user' : 'assistant',
        content: msg.content
      }));

      const formData = new FormData();
      formData.append('messages', JSON.stringify(formattedMessages));

      const response = await fetch(`http://localhost:8000/${endpoint}/${encodedQuery}`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      let finalContent = '';

      if (isDeepResearch) {
        // Handle non-streaming response for deep research
        const data = await response.json();
        
        if (data.error) {
          throw new Error(data.error);
        }

        finalContent = data.report;
        const responseTime = Date.now() - startTime;
        
        setMessages(prev => 
          prev.map(msg => 
            msg.id === assistantMessageId 
              ? { ...msg, content: finalContent, responseTime }
              : msg
          )
        );
      } else {
        // Handle streaming response for quick completion
        const reader = response.body?.getReader();
        const decoder = new TextDecoder();

        if (!reader) {
          throw new Error('No response stream available');
        }

        let accumulatedContent = '';

        while (true) {
          const { done, value } = await reader.read();
          
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          accumulatedContent += chunk;

          // Update the assistant message with accumulated content
          setMessages(prev => 
            prev.map(msg => 
              msg.id === assistantMessageId 
                ? { ...msg, content: accumulatedContent }
                : msg
            )
          );
        }

        finalContent = accumulatedContent;
        const responseTime = Date.now() - startTime;
        
        // Update with final response time
        setMessages(prev => 
          prev.map(msg => 
            msg.id === assistantMessageId 
              ? { ...msg, content: finalContent, responseTime }
              : msg
          )
        );
      }

      // Save complete assistant response
      await conversationManager.saveMessage(conversationTitle, 'assistant', finalContent);
      
      // Refresh conversations after saving assistant message
      if (refreshConversations) {
        await refreshConversations();
      }

    } catch (error) {
      const errorMessage = "Sorry, I encountered an error while generating your report. Please try again.";
      const responseTime = Date.now() - startTime;
      
      setMessages(prev => 
        prev.map(msg => 
          msg.id === assistantMessageId 
            ? { ...msg, content: errorMessage, responseTime }
            : msg
        )
      );

      // Save error message
      await conversationManager.saveMessage(conversationTitle, 'assistant', errorMessage);
      
      // Refresh conversations after saving error message
      if (refreshConversations) {
        await refreshConversations();
      }

      console.error('Streaming error:', error);
    } finally {
      setIsLoading(false);
      setStreamingMessageId(null);
    }
  }, [messages, setMessages, setIsLoading, currentConversationTitle, onConversationCreated, refreshConversations]);

  return {
    sendStreamingMessage,
    streamingMessageId
  };
};
