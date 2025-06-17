
import { Button } from "@/components/ui/button";
import { Settings, Eye } from "lucide-react";
import { ThemeToggle } from "@/components/ThemeToggle";
import { useAuth } from "@/contexts/AuthContext";
import { useNavigate } from "react-router-dom";

interface TopNavigationProps {
  onNewConversation: () => void;
  onSettingsClick: () => void;
}

export const TopNavigation = ({ onNewConversation, onSettingsClick }: TopNavigationProps) => {
  const { user, logout, isAuthenticated, loginWithGoogle } = useAuth();
  const navigate = useNavigate();

  const handleLogoClick = () => {
    onNewConversation();
    navigate('/');
  };

  return (
    <div className="w-full bg-white/80 dark:bg-gray-950/80 backdrop-blur-xl border-b border-gray-200/20 dark:border-gray-800/20">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Left side - Logo with Eye Icon - Clickable */}
          <button onClick={handleLogoClick} className="flex items-center gap-3 hover:opacity-80 transition-opacity">
            <div className="relative">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-700 rounded-xl flex items-center justify-center shadow-lg">
                <Eye className="h-5 w-5 text-white" />
              </div>
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900 dark:text-white tracking-tight">
                Spy Search
              </h1>
              <p className="text-xs text-gray-500 dark:text-gray-400 font-medium">
                AI-Powered Research
              </p>
            </div>
          </button>

          {/* Right side - Actions */}
          <div className="flex items-center gap-3">
            {isAuthenticated && user ? (
              <div className="flex items-center gap-3 pr-3 border-r border-gray-200 dark:border-gray-700">
                <div className="flex items-center gap-2">
                  <img 
                    src={user.picture} 
                    alt={user.name}
                    className="w-8 h-8 rounded-full border-2 border-gray-100 dark:border-gray-700"
                  />
                  <div className="hidden sm:block">
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      {user.name}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      Researcher
                    </p>
                  </div>
                </div>
                <Button
                  onClick={logout}
                  variant="ghost"
                  size="sm"
                  className="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
                >
                  Sign Out
                </Button>
              </div>
            ) : (
              <div className="pr-3 border-r border-gray-200 dark:border-gray-700">
                <Button
                  onClick={loginWithGoogle}
                  variant="default"
                  size="sm"
                  className="bg-blue-500 hover:bg-blue-600 text-white rounded-xl transition-all duration-200 shadow-md"
                >
                  Sign In
                </Button>
              </div>
            )}

            <div className="flex items-center gap-2">
              <ThemeToggle />
              <Button
                onClick={onSettingsClick}
                variant="ghost"
                size="sm"
                className="rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 transition-all duration-200"
              >
                <Settings className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
