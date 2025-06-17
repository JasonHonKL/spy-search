
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { SidebarTrigger } from "@/components/ui/sidebar";
import { Settings, Eye, Newspaper, GraduationCap, LogIn, LogOut, User } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { useAuth } from "@/contexts/AuthContext";

interface TopNavigationProps {
  onNewConversation: () => void;
  onSettingsClick: () => void;
}

export const TopNavigation = ({ onNewConversation, onSettingsClick }: TopNavigationProps) => {
  const { toast } = useToast();
  const { isAuthenticated, user, loginWithGoogle, logout, isLoading } = useAuth();

  const handleLogout = () => {
    logout();
    toast({
      title: "Logged out",
      description: "You have been successfully logged out.",
    });
  };

  const handleLoginClick = async () => {
    try {
      await loginWithGoogle();
    } catch (error) {
      toast({
        title: "Login failed",
        description: "Failed to initiate Google login. Please try again.",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="flex items-center justify-between p-4 border-b border-border/20 bg-background">
      <div className="flex items-center gap-4">
        <SidebarTrigger />
        <Link to="/" onClick={onNewConversation} className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-primary/10 border border-primary/20">
            <Eye className="h-4 w-4 text-primary" />
          </div>
          <h1 className="text-base font-light gradient-text">Spy Search</h1>
        </Link>
        <div className="flex gap-2">
          <Link to="/news">
            <Button variant="ghost" size="sm" className="text-muted-foreground hover:text-foreground">
              <Newspaper className="h-4 w-4 mr-2" />
              Discover
            </Button>
          </Link>
          <Link to="/academic">
            <Button variant="ghost" size="sm" className="text-muted-foreground hover:text-foreground">
              <GraduationCap className="h-4 w-4 mr-2" />
              Academic
            </Button>
          </Link>
        </div>
      </div>
      <div className="flex items-center gap-2">
        {isLoading ? (
          <div className="text-sm text-muted-foreground">Loading...</div>
        ) : isAuthenticated ? (
          <>
            <div className="flex items-center gap-3">
              {user?.picture && (
                <img 
                  src={user.picture} 
                  alt={user.name || user.email} 
                  className="w-8 h-8 rounded-full border border-border"
                />
              )}
              <div className="text-right">
                <div className="text-sm font-medium text-foreground">{user?.name}</div>
                <div className="text-xs text-muted-foreground">{user?.email}</div>
              </div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleLogout}
              className="text-muted-foreground hover:text-foreground"
            >
              <LogOut className="h-4 w-4 mr-2" />
              Logout
            </Button>
          </>
        ) : (
          <Button
            variant="ghost"
            size="sm"
            onClick={handleLoginClick}
            className="text-muted-foreground hover:text-foreground"
          >
            <LogIn className="h-4 w-4 mr-2" />
            Sign in with Google
          </Button>
        )}
        <Button
          variant="ghost"
          size="sm"
          onClick={onSettingsClick}
          className="text-muted-foreground hover:text-foreground"
        >
          <Settings className="h-4 w-4 mr-2" />
          Settings
        </Button>
      </div>
    </div>
  );
};
