
import { useState, useEffect, useRef } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useToast } from "@/hooks/use-toast";
import { 
  Database, 
  FolderPlus, 
  Upload, 
  Trash2, 
  File, 
  Check,
  X 
} from "lucide-react";

interface FolderContent {
  foldername: string;
  contents: string[];
}

interface DatabaseModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export const DatabaseModal = ({ open, onOpenChange }: DatabaseModalProps) => {
  const [folders, setFolders] = useState<FolderContent[]>([]);
  const [newFolderName, setNewFolderName] = useState("");
  const [selectedFolder, setSelectedFolder] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);
  const [draggedOverFolder, setDraggedOverFolder] = useState<string>("");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();

  // Fetch folders on modal open
  useEffect(() => {
    if (open) {
      fetchFolders();
    }
  }, [open]);

  const fetchFolders = async () => {
    try {
      const response = await fetch('http://localhost:8000/folder_list');
      if (response.ok) {
        const data = await response.json();
        setFolders(data.files || []);
      }
    } catch (error) {
      console.error('Error fetching folders:', error);
    }
  };

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
        fetchFolders();
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

  const deleteFolder = async (folderName: string) => {
    setIsLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/delete_folder?filepath=${encodeURIComponent(folderName)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      
      const data = await response.json();
      if (data.success) {
        toast({
          title: "Folder Deleted",
          description: `Successfully deleted folder: ${folderName}`,
        });
        fetchFolders();
      } else {
        throw new Error(data.error || "Failed to delete folder");
      }
    } catch (error) {
      toast({
        title: "Deletion Failed",
        description: error instanceof Error ? error.message : "Failed to delete folder",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const deleteFile = async (folderName: string, fileName: string) => {
    setIsLoading(true);
    try {
      const filePath = `${folderName}/${fileName}`;
      const response = await fetch(`http://localhost:8000/delete_file?filepath=${encodeURIComponent(filePath)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      
      const data = await response.json();
      if (data.success) {
        toast({
          title: "File Deleted",
          description: `Successfully deleted file: ${fileName}`,
        });
        fetchFolders();
      } else {
        throw new Error(data.error || "Failed to delete file");
      }
    } catch (error) {
      toast({
        title: "Deletion Failed",
        description: error instanceof Error ? error.message : "Failed to delete file",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const selectFolder = async (folderName: string) => {
    try {
      const response = await fetch(`http://localhost:8000/select_folder?folder_name=${folderName}`);
      const data = await response.json();
      
      if (data.success) {
        setSelectedFolder(folderName);
        toast({
          title: "Folder Selected",
          description: `Successfully selected folder: ${folderName}`,
        });
      } else {
        throw new Error("Failed to select folder");
      }
    } catch (error) {
      toast({
        title: "Selection Failed",
        description: error instanceof Error ? error.message : "Failed to select folder",
        variant: "destructive",
      });
    }
  };

  const handleFileUpload = async (files: FileList | null, targetFolder: string) => {
    if (!files || !targetFolder) return;
    
    const pdfFiles = Array.from(files).filter(file => file.type === 'application/pdf');
    if (pdfFiles.length === 0) {
      toast({
        title: "Invalid file type",
        description: "Only PDF files are allowed.",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    try {
      for (const file of pdfFiles) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('filepath', `${targetFolder}/${file.name}`);

        const response = await fetch('http://localhost:8000/upload_file', {
          method: 'POST',
          body: formData,
        });

        const data = await response.json();
        if (!data.success) {
          throw new Error(data.error || `Failed to upload ${file.name}`);
        }
      }

      toast({
        title: "Upload Successful",
        description: `Successfully uploaded ${pdfFiles.length} file(s) to ${targetFolder}`,
      });
      fetchFolders();
    } catch (error) {
      toast({
        title: "Upload Failed",
        description: error instanceof Error ? error.message : "Failed to upload files",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleDragOver = (e: React.DragEvent, folderName?: string) => {
    e.preventDefault();
    setIsDragOver(true);
    if (folderName) setDraggedOverFolder(folderName);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    setDraggedOverFolder("");
  };

  const handleDrop = (e: React.DragEvent, folderName: string) => {
    e.preventDefault();
    setIsDragOver(false);
    setDraggedOverFolder("");
    handleFileUpload(e.dataTransfer.files, folderName);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[80vh] flex flex-col">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-3">
            <Database className="h-5 w-5 text-primary" />
            Database & Folder Management
          </DialogTitle>
        </DialogHeader>

        <div className="flex flex-col space-y-6 flex-1 min-h-0">
          {/* Create New Folder */}
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

          {/* Folders List */}
          <Card className="flex-1 min-h-0">
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Available Folders</CardTitle>
            </CardHeader>
            <CardContent className="p-0 h-full">
              <ScrollArea className="h-[400px] px-6">
                <div className="space-y-4 py-4">
                  {folders.map((folder) => (
                    <div 
                      key={folder.foldername}
                      className={`p-4 border rounded-lg transition-colors ${
                        draggedOverFolder === folder.foldername 
                          ? 'border-primary bg-primary/10' 
                          : 'border-border'
                      } ${
                        selectedFolder === folder.foldername 
                          ? 'ring-2 ring-primary' 
                          : ''
                      }`}
                      onDragOver={(e) => handleDragOver(e, folder.foldername)}
                      onDragLeave={handleDragLeave}
                      onDrop={(e) => handleDrop(e, folder.foldername)}
                    >
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <h3 className="font-medium">{folder.foldername}</h3>
                          {selectedFolder === folder.foldername && (
                            <Badge variant="default" className="text-xs">
                              <Check className="h-3 w-3 mr-1" />
                              Selected
                            </Badge>
                          )}
                          <Badge variant="secondary" className="text-xs">
                            {folder.contents.length} files
                          </Badge>
                        </div>
                        <div className="flex gap-2">
                          <input
                            ref={fileInputRef}
                            type="file"
                            accept=".pdf"
                            multiple
                            onChange={(e) => handleFileUpload(e.target.files, folder.foldername)}
                            className="hidden"
                          />
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => fileInputRef.current?.click()}
                            disabled={isLoading}
                          >
                            <Upload className="h-3 w-3 mr-1" />
                            Upload
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => selectFolder(folder.foldername)}
                            disabled={isLoading}
                          >
                            Select
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => deleteFolder(folder.foldername)}
                            disabled={isLoading}
                          >
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>

                      {/* Files in folder */}
                      {folder.contents.length > 0 && (
                        <div className="space-y-2">
                          <h4 className="text-sm font-medium text-muted-foreground">Files:</h4>
                          <div className="grid grid-cols-1 gap-1">
                            {folder.contents.map((file) => (
                              <div 
                                key={file} 
                                className="flex items-center justify-between p-2 bg-secondary/50 rounded text-sm"
                              >
                                <div className="flex items-center gap-2">
                                  <File className="h-3 w-3" />
                                  <span className="truncate">{file}</span>
                                </div>
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  onClick={() => deleteFile(folder.foldername, file)}
                                  disabled={isLoading}
                                  className="h-6 w-6 p-0"
                                >
                                  <X className="h-3 w-3" />
                                </Button>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Drop zone indicator */}
                      {draggedOverFolder === folder.foldername && (
                        <div className="mt-2 p-2 border-2 border-dashed border-primary rounded text-center text-sm text-primary">
                          Drop PDF files here to upload
                        </div>
                      )}
                    </div>
                  ))}
                  
                  {folders.length === 0 && (
                    <div className="text-center text-muted-foreground py-8">
                      No folders found. Create your first folder above.
                    </div>
                  )}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </div>
      </DialogContent>
    </Dialog>
  );
};
