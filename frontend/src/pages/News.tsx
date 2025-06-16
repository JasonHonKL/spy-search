
import { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Eye, ArrowLeft, ExternalLink, Calendar, Globe, TrendingUp, Gamepad2, DollarSign, Heart, Trophy } from "lucide-react";
import { Link } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";

interface NewsItem {
  snippet: string;
  title: string;
  link: string;
  date: string;
  source: string;
}

const News = () => {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState("technology");
  const [lastFetchTime, setLastFetchTime] = useState<Record<string, number>>({});
  const { toast } = useToast();

  const categories = [
    { id: "technology", label: "Technology", icon: TrendingUp },
    { id: "finance", label: "Finance", icon: DollarSign },
    { id: "entertainment", label: "Entertainment", icon: Gamepad2 },
    { id: "sports", label: "Sports", icon: Trophy },
    { id: "world", label: "World", icon: Globe },
    { id: "health", label: "Health", icon: Heart }
  ];

  const fetchNews = async (category: string, forceRefresh = false) => {
    const now = Date.now();
    const lastFetch = lastFetchTime[category] || 0;
    const tenMinutes = 10 * 60 * 1000; // 10 minutes in milliseconds
    
    // Check if we should fetch (force refresh or 10 minutes have passed)
    if (!forceRefresh && (now - lastFetch) < tenMinutes) {
      return; // Don't fetch, use cached data
    }

    setIsLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/news/${category}`);
      if (response.ok) {
        const data = await response.json();
        setNews(data.news || []);
        setLastFetchTime(prev => ({ ...prev, [category]: now }));
      } else {
        throw new Error("Failed to fetch news");
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to fetch news. Please try again.",
        variant: "destructive",
      });
      setNews([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchNews(selectedCategory);
  }, [selectedCategory]);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      year: 'numeric'
    });
  };

  const truncateText = (text: string, maxLength: number) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + "...";
  };

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
                <Eye className="h-6 w-6 text-primary" />
              </div>
              <h1 className="text-2xl font-light bg-gradient-to-r from-primary to-blue-500 bg-clip-text text-transparent">Discover</h1>
            </div>
          </div>
        </div>

        {/* Category Navigation */}
        <div className="flex flex-wrap gap-3 mb-10 justify-center">
          {categories.map((category) => (
            <Button
              key={category.id}
              variant={selectedCategory === category.id ? "default" : "ghost"}
              size="sm"
              onClick={() => setSelectedCategory(category.id)}
              className={`rounded-full px-6 py-3 transition-all duration-300 ${
                selectedCategory === category.id
                  ? "bg-primary text-white shadow-lg shadow-primary/25"
                  : "bg-white/60 dark:bg-gray-800/40 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100 hover:bg-white/80 dark:hover:bg-gray-800/60 border border-gray-200/50 dark:border-gray-700/50 backdrop-blur-sm"
              }`}
            >
              <category.icon className="h-4 w-4 mr-2" />
              {category.label}
            </Button>
          ))}
        </div>

        {/* News Grid */}
        <div className="max-w-7xl mx-auto">
          {isLoading ? (
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {Array.from({ length: 8 }).map((_, i) => (
                <Card key={i} className="bg-white/60 dark:bg-gray-800/40 backdrop-blur-sm border border-gray-200/50 dark:border-gray-700/50 animate-pulse">
                  <CardContent className="p-6">
                    <div className="space-y-4">
                      <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
                      <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
                      <div className="space-y-2">
                        <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded"></div>
                        <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-5/6"></div>
                        <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-4/6"></div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : news.length === 0 ? (
            <div className="text-center py-16">
              <div className="w-16 h-16 rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center mx-auto mb-6">
                <Globe className="h-8 w-8 text-gray-400 dark:text-gray-600" />
              </div>
              <h3 className="text-xl font-medium text-gray-900 dark:text-white mb-3">No news found</h3>
              <p className="text-gray-600 dark:text-gray-400">Try selecting a different category</p>
            </div>
          ) : (
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {news.map((item, index) => (
                <Card 
                  key={index} 
                  className="bg-white/80 dark:bg-gray-800/60 backdrop-blur-sm border border-gray-200/50 dark:border-gray-700/50 hover:shadow-xl hover:scale-[1.02] transition-all duration-300 cursor-pointer group"
                  onClick={() => window.open(item.link, '_blank')}
                >
                  <CardContent className="p-6">
                    <div className="space-y-4">
                      <h3 className="font-semibold text-gray-900 dark:text-white text-base leading-tight group-hover:text-primary transition-colors">
                        {truncateText(item.title, 80)}
                      </h3>
                      
                      <p className="text-gray-600 dark:text-gray-300 text-sm leading-relaxed">
                        {truncateText(item.snippet, 120)}
                      </p>
                      
                      <div className="flex items-center justify-between pt-4 border-t border-gray-200/50 dark:border-gray-700/50">
                        <div className="flex items-center gap-3 text-xs text-gray-500 dark:text-gray-400">
                          <Badge variant="secondary" className="text-xs bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300">
                            {item.source}
                          </Badge>
                          <div className="flex items-center gap-1">
                            <Calendar className="h-3 w-3" />
                            {formatDate(item.date)}
                          </div>
                        </div>
                        <ExternalLink className="h-4 w-4 text-gray-400 group-hover:text-primary transition-colors" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default News;
