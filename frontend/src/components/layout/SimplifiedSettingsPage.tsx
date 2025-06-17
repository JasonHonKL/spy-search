
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowLeft, Palette, CreditCard, Sun, Moon } from "lucide-react";
import { ThemeToggle } from "@/components/ThemeToggle";
import { useTheme } from "@/hooks/useTheme";

interface SimplifiedSettingsPageProps {
  onBack: () => void;
}

export const SimplifiedSettingsPage = ({ onBack }: SimplifiedSettingsPageProps) => {
  const { theme } = useTheme();

  const handlePurchaseCredits = () => {
    // Placeholder for Stripe integration
    console.log("Purchase credits clicked - Stripe integration coming soon");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50/50 to-white dark:from-gray-900/50 dark:to-gray-800/50">
      <div className="max-w-4xl mx-auto p-6">
        <div className="flex items-center gap-4 mb-8">
          <Button
            variant="ghost"
            size="sm"
            onClick={onBack}
            className="p-2 hover:bg-gray-100/50 dark:hover:bg-gray-800/50 rounded-lg"
          >
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-2xl font-light text-foreground">Settings</h1>
            <p className="text-sm text-muted-foreground">Manage your preferences and account</p>
          </div>
        </div>

        <div className="space-y-6">
          {/* Theme Settings */}
          <Card className="glass-card border-0">
            <CardHeader className="pb-4">
              <CardTitle className="flex items-center gap-3 text-lg font-medium">
                <Palette className="h-5 w-5 text-primary" />
                Theme Settings
              </CardTitle>
              <CardDescription>Customize your visual experience</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <h3 className="text-sm font-medium text-foreground">Color Theme</h3>
                  <p className="text-xs text-muted-foreground">
                    Currently using {theme === 'light' ? 'Light' : 'Dark'} theme
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <Sun className="h-4 w-4 text-muted-foreground" />
                  <ThemeToggle />
                  <Moon className="h-4 w-4 text-muted-foreground" />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Purchase Credits */}
          <Card className="glass-card border-0">
            <CardHeader className="pb-4">
              <CardTitle className="flex items-center gap-3 text-lg font-medium">
                <CreditCard className="h-5 w-5 text-primary" />
                Credits & Billing
              </CardTitle>
              <CardDescription>Manage your credits and billing information</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-gradient-to-r from-primary/5 to-blue-500/5 rounded-lg border border-primary/10">
                <div className="space-y-1">
                  <h3 className="text-sm font-medium text-foreground">Purchase Credits</h3>
                  <p className="text-xs text-muted-foreground">
                    Buy credits to continue using our AI research services
                  </p>
                </div>
                <Button
                  onClick={handlePurchaseCredits}
                  className="bg-primary hover:bg-primary/90 text-primary-foreground"
                >
                  <CreditCard className="mr-2 h-4 w-4" />
                  Buy Credits
                </Button>
              </div>
              
              <div className="text-xs text-muted-foreground bg-muted/30 p-3 rounded-lg">
                <p>💡 Stripe integration will be implemented soon for secure credit purchases.</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
