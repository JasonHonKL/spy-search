
import { useState, useEffect } from 'react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { AlertTriangle } from 'lucide-react';
import { apiClient } from '@/services/apiClient';
import { useAuth } from '@/contexts/AuthContext';

interface TokenStatusData {
  daily_tokens_remaining: number;
  last_reset: string;
}

export const TokenStatus = () => {
  const [tokenStatus, setTokenStatus] = useState<TokenStatusData | null>(null);
  const { isAuthenticated } = useAuth();

  const fetchTokenStatus = async () => {
    if (!isAuthenticated) return;
    
    try {
      const status = await apiClient.getTokenStatus();
      setTokenStatus(status);
    } catch (error) {
      console.error('Failed to fetch token status:', error);
    }
  };

  useEffect(() => {
    fetchTokenStatus();
    // Refresh token status every 30 seconds
    const interval = setInterval(fetchTokenStatus, 30000);
    return () => clearInterval(interval);
  }, [isAuthenticated]);

  // Only show warning when tokens are low (less than 5)
  if (!isAuthenticated || !tokenStatus || tokenStatus.daily_tokens_remaining >= 5) {
    return null;
  }

  return (
    <Alert className="bg-orange-50 dark:bg-orange-950/30 border-orange-200 dark:border-orange-800">
      <AlertTriangle className="h-4 w-4 text-orange-600 dark:text-orange-400" />
      <AlertDescription className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-orange-800 dark:text-orange-200 font-medium">
            Low tokens remaining!
          </span>
          <span className="text-orange-600 dark:text-orange-400 text-sm">
            1 token = Quick search • 5 tokens = Deep search
          </span>
        </div>
        <Badge variant="destructive" className="ml-4">
          {tokenStatus.daily_tokens_remaining} left
        </Badge>
      </AlertDescription>
    </Alert>
  );
};
