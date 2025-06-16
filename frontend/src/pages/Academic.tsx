
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Globe, GraduationCap, Send, ArrowLeft } from "lucide-react";
import { Link } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";
import ReactMarkdown from 'react-markdown';

const Academic = () => {
  const [query, setQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState("");
  const { toast } = useToast();

  const handleSearch = async () => {
    if (!query.trim()) return;
    
    setIsLoading(true);
    setResponse("");
    
    // Always prepend search: for academic queries
    const searchQuery = query.startsWith('search:') ? query : `search: ${query}`;
    
    try {
      const formData = new FormData();
      formData.append('messages', JSON.stringify([{ role: 'user', content: searchQuery }]));
      
      const res = await fetch(`http://localhost:8000/stream_completion_academic/${encodeURIComponent(searchQuery)}`, {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        throw new Error(`Server error: ${res.status}`);
      }

      const reader = res.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('No response stream available');
      }

      let accumulatedContent = '';

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        accumulatedContent += chunk;
        setResponse(accumulatedContent);
      }

    } catch (error) {
      toast({
        title: "Search Failed",
        description: "Failed to search academic content. Please try again.",
        variant: "destructive",
      });
      console.error('Academic search error:', error);
    } finally {
      setIsLoading(false);
    }
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
                <GraduationCap className="h-6 w-6 text-primary" />
              </div>
              <h1 className="text-2xl font-light bg-gradient-to-r from-primary to-blue-500 bg-clip-text text-transparent">Academic Research</h1>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="max-w-4xl mx-auto">
          {/* Search Section */}
          <div className="text-center mb-12">
            <h2 className="text-4xl font-extralight text-gray-900 dark:text-white mb-4">Academic Intelligence</h2>
            <p className="text-lg text-gray-600 dark:text-gray-300 font-light max-w-2xl mx-auto mb-10">
              Search academic papers, journals, and research content with AI-powered analysis
            </p>
            
            {/* Search Input */}
            <div className="flex items-center gap-3 max-w-2xl mx-auto mb-8 p-2 bg-white/90 dark:bg-gray-900/90 backdrop-blur-xl border border-gray-200/60 dark:border-gray-700/60 rounded-[32px] shadow-lg">
              <div className="flex items-center justify-center w-12 h-12 rounded-full bg-primary/10 text-primary">
                <Globe className="h-5 w-5" />
              </div>
              <Input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search academic content..."
                className="border-0 bg-transparent px-0 text-base focus-visible:ring-0 focus-visible:ring-offset-0 placeholder:text-gray-400 dark:placeholder:text-gray-500 font-medium h-12"
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
              <Button 
                onClick={handleSearch} 
                disabled={!query.trim() || isLoading}
                className="rounded-full h-12 px-6 bg-primary hover:bg-primary/90 text-white font-medium shadow-lg shadow-primary/25 transition-all duration-300 hover:scale-105 disabled:opacity-50"
              >
                <Send className="h-4 w-4 mr-2" />
                Search
              </Button>
            </div>

            {/* Categories */}
            <div className="flex flex-wrap gap-3 justify-center">
              {[
                "Medical Research", 
                "Legal Studies", 
                "Computer Science", 
                "Physics", 
                "Literature"
              ].map((category) => (
                <Button
                  key={category}
                  variant="ghost"
                  size="sm"
                  onClick={() => setQuery(`${category.toLowerCase()} recent research`)}
                  className="rounded-full border border-gray-200/50 dark:border-gray-700/50 bg-white/60 dark:bg-gray-800/40 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100 hover:bg-white/80 dark:hover:bg-gray-800/60 backdrop-blur-sm transition-all duration-300"
                >
                  {category}
                </Button>
              ))}
            </div>
          </div>

          {/* Results Section */}
          {(response || isLoading) && (
            <Card className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border border-gray-200/50 dark:border-gray-700/50 shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center gap-3">
                  <GraduationCap className="h-5 w-5 text-primary" />
                  Academic Research Results
                </CardTitle>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <div className="flex items-center justify-center py-12">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                    <span className="ml-4 text-gray-600 dark:text-gray-400">Searching academic content...</span>
                  </div>
                ) : (
                  <div className="prose prose-gray dark:prose-invert max-w-none">
                    <ReactMarkdown>{response}</ReactMarkdown>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default Academic;
