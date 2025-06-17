
import { useState, useRef } from "react";
import { SidebarProvider, SidebarInset } from "@/components/ui/sidebar";
import { ChatInterface } from "@/components/ChatInterface";
import { ConversationSidebar, ConversationSidebarRef } from "@/components/ConversationSidebar";
import { TopNavigation } from "@/components/layout/TopNavigation";
import { SimplifiedSettingsPage } from "@/components/layout/SimplifiedSettingsPage";
import { useToast } from "@/hooks/use-toast";

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

const Index = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [currentConversationTitle, setCurrentConversationTitle] = useState<string | null>(null);
  const { toast } = useToast();
  
  // Reference to the sidebar's refresh function
  const conversationSidebarRef = useRef<ConversationSidebarRef>(null);

  const handleConversationSelect = async (title: string) => {
    try {
      const response = await fetch('http://localhost:8000/load_message', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify({ title }),
      });
      
      if (response.ok) {
        const loadedMessages = await response.json();
        const messagesWithDates = loadedMessages.map((msg: any, index: number) => ({
          id: `${index}`,
          type: msg.role === 'user' ? 'user' : 'assistant',
          content: msg.content,
          timestamp: new Date()
        }));
        setMessages(messagesWithDates);
        setCurrentConversationTitle(title);
      }
    } catch (error) {
      console.error('Failed to load conversation:', error);
      toast({
        title: "Error",
        description: "Failed to load conversation. Please try again.",
        variant: "destructive",
      });
    }
  };

  const handleNewConversation = () => {
    setMessages([]);
    setCurrentConversationTitle(null);
    setIsLoading(false);
  };

  const handleConversationCreated = (title: string) => {
    setCurrentConversationTitle(title);
  };

  const refreshConversations = async () => {
    if (conversationSidebarRef.current) {
      await conversationSidebarRef.current.refreshConversations();
    }
  };

  if (showSettings) {
    return (
      <SimplifiedSettingsPage
        onBack={() => setShowSettings(false)}
      />
    );
  }

  return (
    <SidebarProvider defaultOpen={false}>
      <div className="min-h-screen flex w-full bg-background">
        <ConversationSidebar
          ref={conversationSidebarRef}
          currentConversationTitle={currentConversationTitle}
          onConversationSelect={handleConversationSelect}
          onNewConversation={handleNewConversation}
        />
        
        <SidebarInset className="flex-1">
          <div className="flex flex-col h-screen">
            <TopNavigation
              onNewConversation={handleNewConversation}
              onSettingsClick={() => setShowSettings(true)}
            />

            <div className="flex-1 min-h-0">
              <ChatInterface 
                messages={messages}
                setMessages={setMessages}
                isLoading={isLoading}
                setIsLoading={setIsLoading}
                currentConversationId={currentConversationTitle}
                onConversationCreated={handleConversationCreated}
                refreshConversations={refreshConversations}
              />
            </div>
          </div>
        </SidebarInset>
      </div>
    </SidebarProvider>
  );
};

export default Index;
