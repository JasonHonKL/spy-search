
import { Button } from "@/components/ui/button";
import { Cpu, Globe, TrendingUp, Bot, Sparkles, Heart, Bitcoin, Microscope } from "lucide-react";

interface PromptSuggestionsProps {
  onPromptClick: (promptText: string) => void;
  isAuthenticated: boolean;
}

export const PromptSuggestions = ({ onPromptClick, isAuthenticated }: PromptSuggestionsProps) => {
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
    <div className="max-w-4xl mx-auto">
      <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-4 uppercase tracking-wider">
        Popular Topics
      </p>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 justify-items-center">
        {promptSuggestions.map((prompt) => (
          <Button
            key={prompt.text}
            variant="ghost"
            onClick={() => onPromptClick(prompt.text)}
            disabled={!isAuthenticated}
            className={`group h-auto p-3 rounded-xl border border-gray-200/40 dark:border-gray-700/40 bg-white/50 dark:bg-gray-800/30 backdrop-blur-sm hover:bg-white/70 dark:hover:bg-gray-800/50 hover:shadow-md hover:scale-[1.01] transition-all duration-200 text-left justify-start w-full max-w-[180px] ${
              !isAuthenticated ? 'opacity-50 cursor-not-allowed' : ''
            }`}
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
  );
};
