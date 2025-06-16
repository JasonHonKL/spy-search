
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Settings2, Key, Brain, Users } from "lucide-react";

interface LLMConfigProps {
  config: {
    provider: string;
    apiKey: string;
    model: string;
    agents: string[];
  };
  onConfigSave: (config: {
    provider: string;
    apiKey: string;
    model: string;
    agents: string[];
  }) => void;
}

export const LLMConfig = ({ config, onConfigSave }: LLMConfigProps) => {
  const [provider, setProvider] = useState(config.provider);
  const [apiKey, setApiKey] = useState(config.apiKey);
  const [model, setModel] = useState(config.model);
  const [agents, setAgents] = useState<string[]>(config.agents);

  const providers = [
    { value: "openai", label: "OpenAI" },
    { value: "anthropic", label: "Anthropic" },
    { value: "deepseek", label: "DeepSeek" },
    { value: "ollama", label: "Ollama" }
  ];

  const availableAgents = [
    { id: "planner", label: "Planner", required: true },
    { id: "searcher", label: "Searcher", required: false },
    { id: "local-retrieval", label: "Local Retrieval Searcher", required: false }
  ];

  // Ensure planner is always included
  useEffect(() => {
    if (!agents.includes("planner")) {
      setAgents(prev => [...prev, "planner"]);
    }
  }, [agents]);

  const handleAgentChange = (agentId: string, checked: boolean) => {
    if (agentId === "planner") return; // Planner cannot be unchecked
    
    if (checked) {
      setAgents(prev => [...prev, agentId]);
    } else {
      setAgents(prev => prev.filter(agent => agent !== agentId));
    }
  };

  const handleSave = () => {
    const finalAgents = agents.includes("planner") ? agents : [...agents, "planner"];
    onConfigSave({
      provider,
      apiKey,
      model,
      agents: finalAgents
    });
  };

  return (
    <div className="space-y-8">
      {/* Provider Selection */}
      <Card className="glass-card border-0">
        <CardHeader className="pb-4">
          <CardTitle className="flex items-center gap-3 text-lg font-medium">
            <Brain className="h-5 w-5 text-primary" />
            LLM Provider
          </CardTitle>
          <CardDescription>Choose your language model provider</CardDescription>
        </CardHeader>
        <CardContent>
          <Select value={provider} onValueChange={setProvider}>
            <SelectTrigger className="apple-input">
              <SelectValue placeholder="Select provider" />
            </SelectTrigger>
            <SelectContent>
              {providers.map((p) => (
                <SelectItem key={p.value} value={p.value}>
                  {p.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </CardContent>
      </Card>

      {/* API Configuration */}
      <Card className="glass-card border-0">
        <CardHeader className="pb-4">
          <CardTitle className="flex items-center gap-3 text-lg font-medium">
            <Key className="h-5 w-5 text-primary" />
            API Configuration
          </CardTitle>
          <CardDescription>Configure your API credentials and model</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-3">
            <Label htmlFor="apiKey" className="text-foreground font-medium">
              API Key
            </Label>
            <Input
              id="apiKey"
              type="password"
              placeholder="Enter your API key"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              className="apple-input"
            />
          </div>

          <div className="space-y-3">
            <Label htmlFor="model" className="text-foreground font-medium">
              Model
            </Label>
            <Input
              id="model"
              type="text"
              placeholder="Enter model name (e.g., gpt-4, claude-3-opus, deepseek-chat)"
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className="apple-input"
            />
          </div>
        </CardContent>
      </Card>

      {/* Agent Selection */}
      <Card className="glass-card border-0">
        <CardHeader className="pb-4">
          <CardTitle className="flex items-center gap-3 text-lg font-medium">
            <Users className="h-5 w-5 text-primary" />
            Agent Selection
          </CardTitle>
          <CardDescription>Select which agents to use for intelligence gathering</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {availableAgents.map((agent) => (
            <div key={agent.id} className="flex items-center space-x-3">
              <Checkbox
                id={agent.id}
                checked={agents.includes(agent.id)}
                onCheckedChange={(checked) => handleAgentChange(agent.id, checked as boolean)}
                disabled={agent.required}
                className="border-primary/50"
              />
              <Label 
                htmlFor={agent.id} 
                className={`text-foreground font-medium cursor-pointer ${
                  agent.required ? 'text-primary' : ''
                }`}
              >
                {agent.label}
                {agent.required && (
                  <span className="text-xs text-primary ml-2">(Required)</span>
                )}
              </Label>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Save Configuration */}
      <Button
        onClick={handleSave}
        className="w-full bg-primary hover:bg-primary/90 text-primary-foreground font-medium py-6 text-lg rounded-xl"
      >
        <Settings2 className="mr-3 h-5 w-5" />
        Save Configuration
      </Button>
    </div>
  );
};
