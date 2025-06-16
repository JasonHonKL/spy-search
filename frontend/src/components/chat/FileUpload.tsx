
import { useRef } from "react";
import { Button } from "@/components/ui/button";
import { Upload, FileText, X } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface FileUploadProps {
  uploadedFiles: File[];
  setUploadedFiles: React.Dispatch<React.SetStateAction<File[]>>;
  isDragOver: boolean;
  setIsDragOver: React.Dispatch<React.SetStateAction<boolean>>;
}

export const FileUpload = ({ 
  uploadedFiles, 
  setUploadedFiles, 
  isDragOver, 
  setIsDragOver 
}: FileUploadProps) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();

  const handleFileUpload = (files: FileList | null) => {
    if (!files) return;
    
    const pdfFiles = Array.from(files).filter(file => file.type === 'application/pdf');
    if (pdfFiles.length === 0) {
      toast({
        title: "Invalid file type",
        description: "Only PDF files are allowed.",
        variant: "destructive",
      });
      return;
    }
    
    setUploadedFiles(prev => [...prev, ...pdfFiles]);
  };

  const removeFile = (index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    handleFileUpload(e.dataTransfer.files);
  };

  return (
    <>
      {uploadedFiles.length > 0 && (
        <div className="mb-3 p-3 bg-secondary/30 rounded-xl">
          <div className="flex flex-wrap gap-2">
            {uploadedFiles.map((file, index) => (
              <div key={index} className="flex items-center gap-2 bg-background/50 px-3 py-1 rounded-lg text-sm">
                <FileText className="h-3 w-3" />
                <span className="truncate max-w-[150px]">{file.name}</span>
                <button
                  onClick={() => removeFile(index)}
                  className="text-muted-foreground hover:text-foreground"
                >
                  <X className="h-3 w-3" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      <div
        className={`${isDragOver ? 'bg-primary/10 border-2 border-dashed border-primary rounded-xl p-2' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          multiple
          onChange={(e) => handleFileUpload(e.target.files)}
          className="hidden"
        />
        <Button
          variant="outline"
          size="sm"
          onClick={() => fileInputRef.current?.click()}
          className="self-end px-3 py-3 rounded-xl flex-shrink-0"
        >
          <Upload className="h-4 w-4" />
        </Button>
      </div>
    </>
  );
};
