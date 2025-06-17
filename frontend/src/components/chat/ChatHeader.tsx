
import { Button } from "@/components/ui/button";
import { Bot } from "lucide-react";

interface ChatHeaderProps {
  onClearChat: () => void;
}

export const ChatHeader = ({ onClearChat }: ChatHeaderProps) => {
  return (
    <div className="flex justify-between items-center p-4 border-b border-gray-200/30 dark:border-gray-700/30 bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl">
      <div className="flex items-center gap-3">
        <div className="p-2 rounded-lg bg-gradient-to-br from-primary/90 to-blue-500/90 shadow-md">
          <Bot className="h-4 w-4 text-white" />
        </div>
        <div>
          <h2 className="text-base font-semibold text-gray-900 dark:text-white">Intelligence Assistant</h2>
          <p className="text-xs text-gray-500 dark:text-gray-400">AI-powered research</p>
        </div>
      </div>
      <Button
        variant="ghost"
        size="sm"
        onClick={onClearChat}
        className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 rounded-lg px-3 py-1.5 hover:bg-gray-100/40 dark:hover:bg-gray-800/40"
      >
        New Chat
      </Button>
    </div>
  );
};
