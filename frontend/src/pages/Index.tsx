
import { useState } from "react";
import { ChatInterface } from "@/components/ChatInterface";
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
  const { toast } = useToast();

  const handleNewConversation = () => {
    setMessages([]);
    setIsLoading(false);
  };

  if (showSettings) {
    return (
      <SimplifiedSettingsPage
        onBack={() => setShowSettings(false)}
      />
    );
  }

  return (
    <div className="min-h-screen flex flex-col w-full bg-background">
      <TopNavigation
        onNewConversation={handleNewConversation}
        onSettingsClick={() => setShowSettings(true)}
      />

      <div className="flex-1 flex flex-col min-h-0">
        {/* Main Chat Interface */}
        <div className="flex-1 min-h-0">
          <ChatInterface 
            messages={messages}
            setMessages={setMessages}
            isLoading={isLoading}
            setIsLoading={setIsLoading}
            currentConversationId={null}
            onConversationCreated={() => {}}
            refreshConversations={async () => {}}
          />
        </div>
      </div>
    </div>
  );
};

export default Index;
