
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Sparkles, ArrowLeft } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { useToast } from "@/hooks/use-toast";

interface LoginPageProps {
  onBack?: () => void;
}

export const LoginPage = ({ onBack }: LoginPageProps) => {
  const [isLoading, setIsLoading] = useState(false);
  const { loginWithGoogle } = useAuth();
  const { toast } = useToast();

  const handleGoogleLogin = async () => {
    setIsLoading(true);
    try {
      await loginWithGoogle();
      toast({
        title: "Login initiated",
        description: "Redirecting to Google login...",
      });
    } catch (error) {
      toast({
        title: "Login failed",
        description: "Failed to initiate Google login. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50/20 to-white/40 dark:from-gray-900/20 dark:to-gray-800/20 p-4">
      <Card className="w-full max-w-md shadow-lg">
        <CardHeader className="text-center">
          {onBack && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onBack}
              className="absolute top-4 left-4 p-2"
            >
              <ArrowLeft className="h-4 w-4" />
            </Button>
          )}
          <div className="inline-flex items-center justify-center w-12 h-12 bg-gradient-to-br from-primary/90 via-blue-500/90 to-purple-500/90 rounded-2xl mb-4 mx-auto shadow-lg shadow-primary/15">
            <Sparkles className="h-6 w-6 text-white" />
          </div>
          <CardTitle className="text-2xl font-light">Welcome to Spy Search</CardTitle>
          <CardDescription>
            Sign in with your Google account to continue
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button 
            onClick={handleGoogleLogin} 
            className="w-full" 
            disabled={isLoading}
          >
            {isLoading ? "Connecting to Google..." : "Sign in with Google"}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
};
