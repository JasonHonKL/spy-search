
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { FolderItem } from "./FolderItem";

interface FolderContent {
  foldername: string;
  contents: string[];
}

interface FolderListProps {
  folders: FolderContent[];
  selectedFolder: string;
  isLoading: boolean;
  draggedOverFolder: string;
  onDeleteFolder: (folderName: string) => void;
  onSelectFolder: (folderName: string) => void;
  onFileUpload: (files: FileList | null, targetFolder: string) => void;
  onDeleteFile: (folderName: string, fileName: string) => void;
  onDragOver: (e: React.DragEvent, folderName?: string) => void;
  onDragLeave: (e: React.DragEvent) => void;
  onDrop: (e: React.DragEvent, folderName: string) => void;
}

export const FolderList = ({
  folders,
  selectedFolder,
  isLoading,
  draggedOverFolder,
  onDeleteFolder,
  onSelectFolder,
  onFileUpload,
  onDeleteFile,
  onDragOver,
  onDragLeave,
  onDrop
}: FolderListProps) => {
  return (
    <Card className="flex-1 min-h-0">
      <CardHeader className="pb-3">
        <CardTitle className="text-base">Available Folders</CardTitle>
      </CardHeader>
      <CardContent className="p-0 h-full">
        <ScrollArea className="h-[400px] px-6">
          <div className="space-y-4 py-4">
            {folders.map((folder) => (
              <FolderItem
                key={folder.foldername}
                folder={folder}
                selectedFolder={selectedFolder}
                isLoading={isLoading}
                isDraggedOver={draggedOverFolder === folder.foldername}
                onDelete={onDeleteFolder}
                onSelect={onSelectFolder}
                onFileUpload={onFileUpload}
                onFileDelete={onDeleteFile}
                onDragOver={onDragOver}
                onDragLeave={onDragLeave}
                onDrop={onDrop}
              />
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
  );
};
