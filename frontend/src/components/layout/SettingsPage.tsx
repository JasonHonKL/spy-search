
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Settings } from "lucide-react";
import { AgentConfig } from "@/components/AgentConfig";
import { ThemeToggle } from "@/components/ThemeToggle";

interface SettingsPageProps {
  agents: string[];
  onBack: () => void;
  onAgentConfigSave: (config: {
    agents: string[];
    provider: string;
    model: string;
  }) => void;
}

export const SettingsPage = ({ agents, onBack, onAgentConfigSave }: SettingsPageProps) => {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <Button
            variant="ghost"
            onClick={onBack}
            className="text-muted-foreground hover:text-foreground"
          >
            ← Back to Chat
          </Button>
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-primary/10 border border-primary/20">
              <Settings className="h-5 w-5 text-primary" />
            </div>
            <h1 className="text-2xl font-light text-foreground">Settings</h1>
          </div>
          <div className="w-24"></div>
        </div>

        {/* Settings Content */}
        <div className="max-w-3xl mx-auto space-y-6">
          {/* Theme Settings */}
          <Card className="glass-card border-0">
            <CardHeader className="pb-4">
              <CardTitle className="flex items-center gap-3 text-xl font-light">
                Theme Preferences
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium">Theme</h3>
                  <p className="text-sm text-muted-foreground">Choose your preferred theme</p>
                </div>
                <ThemeToggle />
              </div>
            </CardContent>
          </Card>

          {/* Agent Configuration */}
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
                onAgentConfigSave={onAgentConfigSave}
              />
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
