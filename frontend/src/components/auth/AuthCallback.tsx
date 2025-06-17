
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";

export const AuthCallback = () => {
  const navigate = useNavigate();
  const { toast } = useToast();

  useEffect(() => {
    const handleCallback = async () => {
      const urlParams = new URLSearchParams(window.location.search);
      const code = urlParams.get('code');
      const error = urlParams.get('error');

      if (error) {
        console.error('OAuth error:', error);
        toast({
          title: "Authentication Failed",
          description: "There was an error during authentication. Please try again.",
          variant: "destructive",
        });
        navigate('/');
        return;
      }

      if (!code) {
        console.error('No authorization code received');
        toast({
          title: "Authentication Failed",
          description: "No authorization code received. Please try again.",
          variant: "destructive",
        });
        navigate('/');
        return;
      }

      try {
        // Call the backend's callback endpoint directly
        const response = await fetch(`http://localhost:8000/auth/google/callback?code=${code}`, {
          method: 'GET',
        });

        if (response.ok) {
          const data = await response.json();
          
          // Store the JWT token and user data
          localStorage.setItem('auth_token', data.access_token);
          localStorage.setItem('user_data', JSON.stringify(data.user));
          
          toast({
            title: "Login Successful",
            description: "You have been logged in successfully.",
          });
          
          // Navigate to home page - the AuthContext will pick up the token
          navigate('/');
          
          // Reload to trigger auth state update
          window.location.reload();
        } else {
          throw new Error('Authentication failed');
        }
      } catch (error) {
        console.error('Callback processing error:', error);
        toast({
          title: "Authentication Failed",
          description: "Failed to complete authentication. Please try again.",
          variant: "destructive",
        });
        navigate('/');
      }
    };

    handleCallback();
  }, [navigate, toast]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
        <p className="text-sm text-muted-foreground">Processing authentication...</p>
      </div>
    </div>
  );
};
