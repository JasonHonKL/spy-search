
import { useState, useEffect } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { useToast } from "@/hooks/use-toast";
import { Database } from "lucide-react";
import { FolderManager } from "./database/FolderManager";
import { FolderList } from "./database/FolderList";

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
  const [selectedFolder, setSelectedFolder] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);
  const [draggedOverFolder, setDraggedOverFolder] = useState<string>("");
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

  const deleteFolder = async (folderName: string) => {
    setIsLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/delete_folder?filepath=${encodeURIComponent(folderName)}`, {
        method: 'POST',
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
          <FolderManager onFolderCreated={fetchFolders} />
          
          <FolderList
            folders={folders}
            selectedFolder={selectedFolder}
            isLoading={isLoading}
            draggedOverFolder={draggedOverFolder}
            onDeleteFolder={deleteFolder}
            onSelectFolder={selectFolder}
            onFileUpload={handleFileUpload}
            onDeleteFile={deleteFile}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          />
        </div>
      </DialogContent>
    </Dialog>
  );
};
