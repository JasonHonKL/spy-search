
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Send, Globe, Zap } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { useToast } from "@/hooks/use-toast";

interface ChatInputProps {
  input: string;
  setInput: (value: string) => void;
  isLoading: boolean;
  onSendMessage: (message: string, files: File[], isDeepResearch: boolean) => void;
  searchMode?: boolean;
  onSearchModeChange?: (enabled: boolean) => void;
  onLoginRequired?: () => void;
}

export const ChatInput = ({ 
  input, 
  setInput, 
  isLoading, 
  onSendMessage,
  searchMode = true,
  onSearchModeChange,
  onLoginRequired
}: ChatInputProps) => {
  const [internalSearchMode, setInternalSearchMode] = useState(true);
  const [isDeepResearch, setIsDeepResearch] = useState(false);
  const { isAuthenticated, loginWithGoogle, isLoading: authLoading } = useAuth();
  const { toast } = useToast();

  const currentSearchMode = onSearchModeChange ? searchMode : internalSearchMode;

  const handleSubmit = async () => {
    if (!input.trim() || isLoading) return;
    
    // Check authentication before allowing search
    if (!isAuthenticated) {
      toast({
        title: "Authentication required",
        description: "Please sign in with Google to use the search functionality.",
        variant: "destructive",
      });
      
      try {
        await loginWithGoogle();
      } catch (error) {
        console.error('Login failed:', error);
      }
      return;
    }
    
    const messageContent = currentSearchMode && !input.trim().startsWith('search:') 
      ? `search: ${input.trim()}` 
      : input.trim();
    
    onSendMessage(messageContent, [], isDeepResearch);
    setInput("");
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const toggleSearchMode = () => {
    const newMode = !currentSearchMode;
    if (onSearchModeChange) {
      onSearchModeChange(newMode);
    } else {
      setInternalSearchMode(newMode);
    }
  };

  const toggleDeepResearch = () => {
    setIsDeepResearch(!isDeepResearch);
  };

  return (
    <div className="w-full">
      {/* Search Mode Indicator */}
      {currentSearchMode && isAuthenticated && (
        <div className="flex justify-center mb-2">
          <div className="inline-flex items-center px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-xs font-medium rounded-full">
            {isDeepResearch ? "Deep Research Active" : "Quick Search Active"}
          </div>
        </div>
      )}

      <div className="relative">
        <div className="flex items-center gap-2 p-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl shadow-sm hover:shadow-md transition-all duration-200">
          
          {/* Search Toggle */}
          <button
            onClick={toggleSearchMode}
            className={`flex items-center justify-center w-8 h-8 rounded-full transition-all duration-200 ${
              currentSearchMode 
                ? 'bg-blue-500 text-white shadow-md' 
                : 'bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600'
            }`}
          >
            <Globe className="h-4 w-4" />
          </button>

          {/* Deep Research Toggle - Only show when search is active */}
          {currentSearchMode && (
            <button
              onClick={toggleDeepResearch}
              className={`flex items-center justify-center w-8 h-8 rounded-full transition-all duration-200 ${
                isDeepResearch 
                  ? 'bg-purple-500 text-white shadow-md' 
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
              title={isDeepResearch ? "Deep Research Mode" : "Quick Search Mode"}
            >
              <Zap className="h-4 w-4" />
            </button>
          )}

          {/* Input Field */}
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={
              currentSearchMode 
                ? isDeepResearch 
                  ? "Deep research the web..." 
                  : "Quick search the web..."
                : "Ask me anything..."
            }
            disabled={isLoading || authLoading}
            className="flex-1 border-0 bg-transparent px-2 py-1 text-sm focus-visible:outline-none placeholder:text-gray-400 dark:placeholder:text-gray-500 text-gray-900 dark:text-white"
          />

          {/* Send Button */}
          <Button
            onClick={handleSubmit}
            disabled={!input.trim() || isLoading || authLoading}
            size="sm"
            className={`rounded-full h-8 w-8 p-0 transition-all duration-200 ${
              isAuthenticated && input.trim()
                ? 'bg-blue-500 hover:bg-blue-600 text-white shadow-md' 
                : 'bg-gray-300 dark:bg-gray-600 text-gray-500 dark:text-gray-400 cursor-not-allowed'
            }`}
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>

        {/* Authentication Status Indicator */}
        {!isAuthenticated && !authLoading && (
          <div className="absolute -top-8 left-2 px-2 py-1 bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400 text-xs font-medium rounded-full">
            Sign in required for search
          </div>
        )}
      </div>
    </div>
  );
};
