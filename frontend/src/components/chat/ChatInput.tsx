
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
  const [isDeepSearch, setIsDeepSearch] = useState(false);
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
    
    onSendMessage(messageContent, [], isDeepSearch);
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

  const handleSearchModeScroll = (e: React.WheelEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDeepSearch(!isDeepSearch);
  };

  const toggleDeepSearch = () => {
    setIsDeepSearch(!isDeepSearch);
  };

  return (
    <div className="w-full max-w-3xl mx-auto">
      <div className="relative group">
        <div className="flex items-center gap-2 p-1.5 bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border border-gray-200/50 dark:border-gray-700/50 rounded-3xl shadow-sm hover:shadow-md transition-all duration-200 focus-within:border-primary/30 focus-within:shadow-md">
          
          {/* Search Toggle */}
          <button
            onClick={toggleSearchMode}
            className={`flex items-center justify-center w-10 h-10 rounded-full transition-all duration-200 ${
              currentSearchMode 
                ? 'bg-primary/15 text-primary shadow-sm' 
                : 'bg-gray-100/50 dark:bg-gray-800/50 text-gray-500 dark:text-gray-400 hover:bg-gray-200/50 dark:hover:bg-gray-700/50 hover:text-gray-700 dark:hover:text-gray-300'
            }`}
          >
            <Globe className="h-4 w-4" />
          </button>

          {/* Input Field with proper text wrapping */}
          <div className="flex-1">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={currentSearchMode ? "Search the web..." : "Ask me anything..."}
              disabled={isLoading || authLoading}
              className="w-full border-0 bg-transparent px-0 py-2 text-sm focus-visible:ring-0 focus-visible:ring-offset-0 placeholder:text-gray-400 dark:placeholder:text-gray-500 font-medium resize-none min-h-[24px] max-h-[96px] overflow-y-auto"
              rows={1}
              style={{
                height: 'auto',
                minHeight: '24px'
              }}
              onInput={(e) => {
                const target = e.target as HTMLTextAreaElement;
                target.style.height = 'auto';
                target.style.height = `${Math.min(target.scrollHeight, 96)}px`;
              }}
            />
          </div>

          {/* Search Mode Toggle Button */}
          <div className="flex items-center gap-1">
            <Button
              onClick={toggleDeepSearch}
              onWheel={handleSearchModeScroll}
              disabled={false}
              size="sm"
              variant="ghost"
              className={`rounded-full h-8 w-8 p-0 transition-all duration-200 hover:scale-105 mr-1 ${
                isDeepSearch 
                  ? 'bg-orange-100 hover:bg-orange-200 text-orange-600 border border-orange-200' 
                  : 'bg-blue-100 hover:bg-blue-200 text-blue-600 border border-blue-200'
              }`}
              title={`${isDeepSearch ? 'Deep Search' : 'Quick Search'} - Click or scroll to toggle`}
            >
              {isDeepSearch ? <Send className="h-3 w-3" /> : <Zap className="h-3 w-3" />}
            </Button>
            
            {/* Send Button */}
            <Button
              onClick={handleSubmit}
              disabled={!input.trim() || isLoading || authLoading}
              size="sm"
              className={`rounded-full h-10 w-10 p-0 transition-all duration-200 hover:scale-105 disabled:opacity-50 disabled:hover:scale-100 shadow-sm ${
                isAuthenticated 
                  ? 'bg-primary hover:bg-primary/90 text-white shadow-primary/20' 
                  : 'bg-gray-400 hover:bg-gray-500 text-white'
              }`}
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Authentication Status Indicator */}
        {!isAuthenticated && !authLoading && (
          <div className="absolute -top-8 left-4 px-3 py-1 bg-orange-100 text-orange-600 text-xs font-medium rounded-full shadow-sm animate-fade-in">
            Sign in required
          </div>
        )}

        {/* Search Mode Indicator */}
        {currentSearchMode && isAuthenticated && (
          <div className="absolute -top-8 left-4 px-3 py-1 bg-primary/15 text-primary text-xs font-medium rounded-full shadow-sm animate-fade-in">
            Web Search Active
          </div>
        )}

        {/* Search Type Indicator */}
        {isAuthenticated && (
          <div className="absolute -top-8 right-4 px-3 py-1 bg-gray-100/80 dark:bg-gray-800/80 text-gray-600 dark:text-gray-300 text-xs font-medium rounded-full shadow-sm animate-fade-in">
            {isDeepSearch ? 'Deep Search' : 'Quick Search'}
          </div>
        )}
      </div>
    </div>
  );
};
