
import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";
import { 
  Upload, 
  Trash2, 
  Check,
  Download,
  X,
  File 
} from "lucide-react";

interface FolderItemProps {
  folder: {
    foldername: string;
    contents: string[];
  };
  selectedFolder: string;
  isLoading: boolean;
  isDraggedOver: boolean;
  onDelete: (folderName: string) => void;
  onSelect: (folderName: string) => void;
  onFileUpload: (files: FileList | null, targetFolder: string) => void;
  onFileDelete: (folderName: string, fileName: string) => void;
  onDragOver: (e: React.DragEvent, folderName?: string) => void;
  onDragLeave: (e: React.DragEvent) => void;
  onDrop: (e: React.DragEvent, folderName: string) => void;
}

export const FolderItem = ({ 
  folder, 
  selectedFolder, 
  isLoading, 
  isDraggedOver,
  onDelete,
  onSelect,
  onFileUpload,
  onFileDelete,
  onDragOver,
  onDragLeave,
  onDrop
}: FolderItemProps) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();

  const downloadFile = async (folderName: string, fileName: string) => {
    try {
      const filePath = `${folderName}/${fileName}`;
      const response = await fetch(`http://localhost:8000/download_file/${encodeURIComponent(filePath)}`);
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = fileName;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        toast({
          title: "Download Started",
          description: `Downloading ${fileName}`,
        });
      } else {
        throw new Error("Failed to download file");
      }
    } catch (error) {
      toast({
        title: "Download Failed",
        description: error instanceof Error ? error.message : "Failed to download file",
        variant: "destructive",
      });
    }
  };

  return (
    <div 
      className={`p-4 border rounded-lg transition-colors ${
        isDraggedOver 
          ? 'border-primary bg-primary/10' 
          : 'border-border'
      } ${
        selectedFolder === folder.foldername 
          ? 'ring-2 ring-primary' 
          : ''
      }`}
      onDragOver={(e) => onDragOver(e, folder.foldername)}
      onDragLeave={onDragLeave}
      onDrop={(e) => onDrop(e, folder.foldername)}
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
            onChange={(e) => onFileUpload(e.target.files, folder.foldername)}
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
            onClick={() => onSelect(folder.foldername)}
            disabled={isLoading}
          >
            Select
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={() => onDelete(folder.foldername)}
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
                <div className="flex gap-1">
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => downloadFile(folder.foldername, file)}
                    disabled={isLoading}
                    className="h-6 w-6 p-0"
                    title="Download file"
                  >
                    <Download className="h-3 w-3" />
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => onFileDelete(folder.foldername, file)}
                    disabled={isLoading}
                    className="h-6 w-6 p-0"
                    title="Delete file"
                  >
                    <X className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Drop zone indicator */}
      {isDraggedOver && (
        <div className="mt-2 p-2 border-2 border-dashed border-primary rounded text-center text-sm text-primary">
          Drop PDF files here to upload
        </div>
      )}
    </div>
  );
};
