
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";
import { FolderPlus } from "lucide-react";

interface FolderManagerProps {
  onFolderCreated: () => void;
}

export const FolderManager = ({ onFolderCreated }: FolderManagerProps) => {
  const [newFolderName, setNewFolderName] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const createFolder = async () => {
    if (!newFolderName.trim()) return;
    
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/create_folder', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filepath: newFolderName.trim() }),
      });
      
      const data = await response.json();
      if (data.success) {
        toast({
          title: "Folder Created",
          description: `Successfully created folder: ${newFolderName}`,
        });
        setNewFolderName("");
        onFolderCreated();
      } else {
        throw new Error(data.error || "Failed to create folder");
      }
    } catch (error) {
      toast({
        title: "Creation Failed",
        description: error instanceof Error ? error.message : "Failed to create folder",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center gap-2">
          <FolderPlus className="h-4 w-4" />
          Create New Folder
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex gap-2">
          <Input
            value={newFolderName}
            onChange={(e) => setNewFolderName(e.target.value)}
            placeholder="Enter folder name"
            onKeyPress={(e) => e.key === 'Enter' && createFolder()}
          />
          <Button 
            onClick={createFolder} 
            disabled={!newFolderName.trim() || isLoading}
          >
            Create
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};
