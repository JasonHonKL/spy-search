
import { Sparkles } from "lucide-react";
import { PromptSuggestions } from "./PromptSuggestions";

interface WelcomeSectionProps {
  onPromptClick: (promptText: string) => void;
  isAuthenticated: boolean;
}

export const WelcomeSection = ({ onPromptClick, isAuthenticated }: WelcomeSectionProps) => {
  return (
    <div className="text-center py-12">
      {/* Hero Section */}
      <div className="mb-8">
        <div className="inline-flex items-center justify-center w-12 h-12 bg-gradient-to-br from-primary/90 via-blue-500/90 to-purple-500/90 rounded-2xl mb-4 shadow-lg shadow-primary/15">
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
          {!isAuthenticated && (
            <span className="block text-orange-600 dark:text-orange-400 mt-2 font-medium">
              Please sign in with Google to start searching
            </span>
          )}
        </p>
      </div>

      {/* Popular Topics Grid */}
      <PromptSuggestions 
        onPromptClick={onPromptClick}
        isAuthenticated={isAuthenticated}
      />
    </div>
  );
};
