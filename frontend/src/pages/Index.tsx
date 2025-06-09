import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Settings, Eye, MessageSquare } from "lucide-react";
import { ChatInterface } from "@/components/ChatInterface";
import { AgentConfig } from "@/components/AgentConfig";
import { useToast } from "@/hooks/use-toast";

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

const Index = () => {
  const [agents, setAgents] = useState<string[]>(["planner", "reporter"]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const handleAgentConfigSave = async (config: {
    agents: string[];
    provider: string;
    model: string;
  }) => {
    setAgents(config.agents);
    
    // Send agent selection, provider, and model to backend (excluding planner)
    const agentsToSend = config.agents.filter(agent => agent !== "planner");
    
    try {
      const response = await fetch('http://localhost:8000/agents_selection', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          agents: agentsToSend,
          provider: config.provider,
          model: config.model
        }),
      });
      
      const data = await response.json();
      
      if (data.success) {
        toast({
          title: "Configuration Saved",
          description: `Agent selection, provider (${config.provider}), and model (${config.model}) have been saved successfully.`,
        });
      } else {
        throw new Error("Failed to save configuration");
      }
    } catch (error) {
      toast({
        title: "Configuration Failed",
        description: "Failed to save agent configuration. Please try again.",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-12">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="flex items-center justify-center gap-4 mb-6">
            <div className="p-4 rounded-2xl bg-primary/10 border border-primary/20 backdrop-blur-sm">
              <Eye className="h-10 w-10 text-primary" />
            </div>
            <h1 className="text-6xl font-light gradient-text tracking-tight">
              Spy Search
            </h1>
          </div>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto font-light leading-relaxed">
            Advanced AI-powered intelligence gathering and report generation platform
          </p>
        </div>

        {/* Main Content */}
        <div className="max-w-5xl mx-auto">
          <Tabs defaultValue="chat" className="w-full">
            <TabsList className="grid w-full grid-cols-2 mb-12 bg-secondary/50 backdrop-blur-sm border border-border/50">
              <TabsTrigger value="chat" className="flex items-center gap-3 data-[state=active]:bg-primary/10 data-[state=active]:text-primary">
                <MessageSquare className="h-4 w-4" />
                Intelligence Chat
              </TabsTrigger>
              <TabsTrigger value="settings" className="flex items-center gap-3 data-[state=active]:bg-primary/10 data-[state=active]:text-primary">
                <Settings className="h-4 w-4" />
                Agent Configuration
              </TabsTrigger>
            </TabsList>

            <TabsContent value="chat" className="space-y-8">
              <ChatInterface 
                agents={agents} 
                messages={messages}
                setMessages={setMessages}
                isLoading={isLoading}
                setIsLoading={setIsLoading}
              />
            </TabsContent>

            <TabsContent value="settings" className="space-y-8">
              <Card className="glass-card border-0">
                <CardHeader className="pb-8">
                  <CardTitle className="flex items-center gap-3 text-2xl font-light">
                    <Settings className="h-6 w-6 text-primary" />
                    Agent Configuration
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <AgentConfig
                    agents={agents}
                    onAgentConfigSave={handleAgentConfigSave}
                  />
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
};

export default Index;
