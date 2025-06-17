
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowLeft, Palette, CreditCard, Sun, Moon, Sparkles, Coins } from "lucide-react";
import { ThemeToggle } from "@/components/ThemeToggle";
import { useTheme } from "@/hooks/useTheme";
import { useState, useEffect } from 'react';
import { apiClient } from '@/services/apiClient';
import { useAuth } from '@/contexts/AuthContext';

interface SimplifiedSettingsPageProps {
  onBack: () => void;
}

interface TokenStatusData {
  daily_tokens_remaining: number;
  last_reset: string;
}

export const SimplifiedSettingsPage = ({ onBack }: SimplifiedSettingsPageProps) => {
  const { theme } = useTheme();
  const { isAuthenticated } = useAuth();
  const [tokenStatus, setTokenStatus] = useState<TokenStatusData | null>(null);

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

  const handlePurchaseCredits = () => {
    console.log("Purchase credits clicked - Stripe integration coming soon");
  };

  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-gray-50 via-white to-blue-50/30 dark:from-gray-900 dark:via-gray-900 dark:to-blue-950/20">
      <div className="w-full h-full">
        {/* Header */}
        <div className="w-full bg-white/80 dark:bg-gray-950/80 backdrop-blur-xl border-b border-gray-200/20 dark:border-gray-800/20">
          <div className="max-w-7xl mx-auto px-6 py-4">
            <div className="flex items-center gap-6">
              <Button
                variant="ghost"
                size="sm"
                onClick={onBack}
                className="p-3 hover:bg-gray-100/60 dark:hover:bg-gray-800/50 rounded-2xl transition-all duration-200"
              >
                <ArrowLeft className="h-5 w-5" />
              </Button>
              <div>
                <h1 className="text-3xl font-semibold text-foreground tracking-tight">Settings</h1>
                <p className="text-base text-muted-foreground mt-1">Customize your research experience</p>
              </div>
            </div>
          </div>
        </div>

        {/* Settings Content */}
        <div className="max-w-5xl mx-auto p-8">
          <div className="space-y-8">
            {/* Token Status - Always visible when authenticated */}
            {isAuthenticated && (
              <Card className="glass-card border-0 shadow-sm">
                <CardHeader className="pb-6">
                  <CardTitle className="flex items-center gap-3 text-xl font-medium">
                    <div className="p-2 bg-gradient-to-br from-blue-500/10 to-indigo-500/10 rounded-xl">
                      <Coins className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                    </div>
                    Token Status
                  </CardTitle>
                  <CardDescription className="text-base">
                    Your remaining research tokens for today
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="flex items-center justify-between p-6 bg-gradient-to-r from-blue-50/50 to-indigo-50/50 dark:from-blue-950/20 dark:to-indigo-950/20 rounded-2xl border border-blue-100/50 dark:border-blue-800/30">
                    <div className="space-y-2">
                      <h3 className="text-lg font-medium text-foreground">Daily Tokens Remaining</h3>
                      <p className="text-muted-foreground text-sm">
                        1 token = Quick search • 5 tokens = Deep search
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                        {tokenStatus?.daily_tokens_remaining || 0}
                      </div>
                      <p className="text-sm text-muted-foreground">tokens left</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Theme Settings */}
            <Card className="glass-card border-0 shadow-sm">
              <CardHeader className="pb-6">
                <CardTitle className="flex items-center gap-3 text-xl font-medium">
                  <div className="p-2 bg-gradient-to-br from-purple-500/10 to-pink-500/10 rounded-xl">
                    <Palette className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                  </div>
                  Appearance
                </CardTitle>
                <CardDescription className="text-base">
                  Personalize your visual experience
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center justify-between p-6 bg-gradient-to-r from-purple-50/50 to-pink-50/50 dark:from-purple-950/20 dark:to-pink-950/20 rounded-2xl border border-purple-100/50 dark:border-purple-800/30">
                  <div className="space-y-2">
                    <h3 className="text-lg font-medium text-foreground">Theme Preference</h3>
                    <p className="text-muted-foreground">
                      Currently using <span className="font-medium text-foreground">{theme === 'light' ? 'Light' : 'Dark'}</span> mode
                    </p>
                  </div>
                  <div className="flex items-center gap-3">
                    <Sun className="h-5 w-5 text-muted-foreground" />
                    <ThemeToggle />
                    <Moon className="h-5 w-5 text-muted-foreground" />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Purchase Credits */}
            <Card className="glass-card border-0 shadow-sm">
              <CardHeader className="pb-6">
                <CardTitle className="flex items-center gap-3 text-xl font-medium">
                  <div className="p-2 bg-gradient-to-br from-emerald-500/10 to-teal-500/10 rounded-xl">
                    <CreditCard className="h-5 w-5 text-emerald-600 dark:text-emerald-400" />
                  </div>
                  Research Credits
                </CardTitle>
                <CardDescription className="text-base">
                  Manage your research tokens and billing
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center justify-between p-6 bg-gradient-to-r from-emerald-50/50 to-teal-50/50 dark:from-emerald-950/20 dark:to-teal-950/20 rounded-2xl border border-emerald-100/50 dark:border-emerald-800/30">
                  <div className="space-y-2">
                    <h3 className="text-lg font-medium text-foreground flex items-center gap-2">
                      <Sparkles className="h-4 w-4 text-emerald-500" />
                      Get More Credits
                    </h3>
                    <p className="text-muted-foreground">
                      Unlock unlimited AI-powered research capabilities
                    </p>
                  </div>
                  <Button
                    onClick={handlePurchaseCredits}
                    className="bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 text-white border-0 px-6 py-3 rounded-xl shadow-lg shadow-emerald-500/25 transition-all duration-200"
                  >
                    <CreditCard className="mr-2 h-4 w-4" />
                    Purchase Credits
                  </Button>
                </div>
                
                <div className="text-sm text-muted-foreground bg-blue-50/50 dark:bg-blue-950/20 p-4 rounded-xl border border-blue-100/50 dark:border-blue-800/30">
                  <div className="flex items-center gap-2 mb-2">
                    <Sparkles className="h-4 w-4 text-blue-500" />
                    <span className="font-medium text-blue-700 dark:text-blue-300">Coming Soon</span>
                  </div>
                  <p className="text-blue-600 dark:text-blue-400">
                    Secure payment processing via Stripe will be available shortly.
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};
