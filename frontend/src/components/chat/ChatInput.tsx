
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send, Globe, Zap } from "lucide-react";

interface ChatInputProps {
  input: string;
  setInput: (value: string) => void;
  isLoading: boolean;
  agents: string[];
  onSendMessage: (message: string, files: File[], isDeepResearch: boolean) => void;
  searchMode?: boolean;
  onSearchModeChange?: (enabled: boolean) => void;
}

export const ChatInput = ({ 
  input, 
  setInput, 
  isLoading, 
  agents, 
  onSendMessage,
  searchMode = true,
  onSearchModeChange
}: ChatInputProps) => {
  const [internalSearchMode, setInternalSearchMode] = useState(true);
  const [isDeepSearch, setIsDeepSearch] = useState(false);

  const currentSearchMode = onSearchModeChange ? searchMode : internalSearchMode;

  const handleSubmit = () => {
    if (!input.trim() || isLoading) return;
    
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
              disabled={isLoading}
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
              disabled={!input.trim() || isLoading}
              size="sm"
              className="rounded-full h-10 w-10 p-0 transition-all duration-200 hover:scale-105 disabled:opacity-50 disabled:hover:scale-100 bg-primary hover:bg-primary/90 text-white shadow-sm shadow-primary/20"
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Search Mode Indicator */}
        {currentSearchMode && (
          <div className="absolute -top-8 left-4 px-3 py-1 bg-primary/15 text-primary text-xs font-medium rounded-full shadow-sm animate-fade-in">
            Web Search Active
          </div>
        )}

        {/* Search Type Indicator */}
        <div className="absolute -top-8 right-4 px-3 py-1 bg-gray-100/80 dark:bg-gray-800/80 text-gray-600 dark:text-gray-300 text-xs font-medium rounded-full shadow-sm animate-fade-in">
          {isDeepSearch ? 'Deep Search' : 'Quick Search'}
        </div>
      </div>
    </div>
  );
};
