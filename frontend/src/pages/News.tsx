
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Clock } from "lucide-react";
import { Link } from "react-router-dom";

const News = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50/30 to-white/50 dark:from-gray-900/30 dark:to-gray-800/30">
      <div className="container mx-auto px-6 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-10">
          <div className="flex items-center gap-6">
            <Link to="/">
              <Button variant="ghost" size="sm" className="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 rounded-xl">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back
              </Button>
            </Link>
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-xl bg-gradient-to-br from-primary/10 to-blue-500/10 border border-primary/20">
                <Clock className="h-6 w-6 text-primary" />
              </div>
              <h1 className="text-2xl font-light bg-gradient-to-r from-primary to-blue-500 bg-clip-text text-transparent">News Discovery</h1>
            </div>
          </div>
        </div>

        {/* Coming Soon Content */}
        <div className="max-w-2xl mx-auto text-center">
          <Card className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border border-gray-200/50 dark:border-gray-700/50 shadow-lg">
            <CardHeader className="pb-6">
              <div className="mx-auto w-20 h-20 rounded-full bg-gradient-to-br from-primary/10 to-blue-500/10 flex items-center justify-center mb-6">
                <Clock className="h-10 w-10 text-primary" />
              </div>
              <CardTitle className="text-3xl font-light text-gray-900 dark:text-white">
                Coming Soon
              </CardTitle>
            </CardHeader>
            <CardContent className="text-center">
              <p className="text-lg text-gray-600 dark:text-gray-300 mb-8 leading-relaxed">
                We're working hard to bring you an amazing news discovery experience. 
                Stay tuned for real-time news search and analysis powered by AI.
              </p>
              <Link to="/">
                <Button size="lg" className="rounded-full px-8">
                  Return to Search
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default News;
