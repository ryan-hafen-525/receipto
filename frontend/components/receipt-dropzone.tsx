"use client"

import * as React from "react"
import { useDropzone, type FileRejection } from "react-dropzone"
import { Upload, X, FileText, Image as ImageIcon, AlertCircle } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"

interface ReceiptDropzoneProps {
  onFileSelect: (file: File) => void
  onFileRemove: () => void
  selectedFile: File | null
  className?: string
  disabled?: boolean
}

export function ReceiptDropzone({
  onFileSelect,
  onFileRemove,
  selectedFile,
  className,
  disabled = false,
}: ReceiptDropzoneProps) {
  const onDrop = React.useCallback(
    (acceptedFiles: File[], rejectedFiles: FileRejection[]) => {
      // Handle accepted files (only take the first one since multiple={false})
      if (acceptedFiles.length > 0) {
        onFileSelect(acceptedFiles[0])
      }

      // We could handle rejected files here (e.g. show toast)
      if (rejectedFiles.length > 0) {
        console.warn("File rejected:", rejectedFiles[0].errors)
      }
    },
    [onFileSelect]
  )

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      "image/jpeg": [],
      "image/png": [],
      "application/pdf": [],
    },
    maxFiles: 1,
    multiple: false,
    disabled: disabled || !!selectedFile,
  })

  // Format file size
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes"
    const k = 1024
    const sizes = ["Bytes", "KB", "MB", "GB"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
  }

  // Preview content based on state
  const renderContent = () => {
    if (selectedFile) {
      return (
        <div className="relative flex w-full max-w-sm flex-col items-center justify-center overflow-hidden rounded-lg border bg-background p-4 shadow-sm">
            <div className="absolute right-2 top-2 z-10">
              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6 rounded-full hover:bg-destructive/10 hover:text-destructive"
                onClick={(e) => {
                  e.stopPropagation()
                  onFileRemove()
                }}
              >
                <X className="h-4 w-4" />
                <span className="sr-only">Remove file</span>
              </Button>
            </div>
          <div className="mb-3 flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
            {selectedFile.type === "application/pdf" ? (
              <FileText className="h-8 w-8 text-primary" />
            ) : (
              <ImageIcon className="h-8 w-8 text-primary" />
            )}
          </div>
          <div className="text-center">
            <p className="truncate text-sm font-medium">{selectedFile.name}</p>
            <p className="text-xs text-muted-foreground">{formatFileSize(selectedFile.size)}</p>
          </div>
        </div>
      )
    }

    return (
      <div className="flex flex-col items-center justify-center gap-4 text-center">
        <div className={cn(
            "flex h-20 w-20 items-center justify-center rounded-full bg-muted transition-colors",
            isDragActive && "bg-primary/10 text-primary"
        )}>
           <Upload className={cn("h-10 w-10 text-muted-foreground", isDragActive && "text-primary")} />
        </div>
        <div className="space-y-2">
          <p className="text-lg font-medium">
            {isDragActive ? "Drop the receipt here" : "Drag and drop your receipt here"}
          </p>
          <p className="text-sm text-muted-foreground">
            or click to browse (JPG, PNG, PDF)
          </p>
        </div>
        {isDragReject && (
             <div className="flex items-center gap-2 text-sm text-destructive">
                <AlertCircle className="h-4 w-4" />
                <span>File type not supported</span>
            </div>
        )}
      </div>
    )
  }

  return (
    <div
      {...getRootProps()}
      className={cn(
        "relative flex min-h-[300px] cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-muted-foreground/25 p-12 transition-colors hover:bg-muted/50",
        isDragActive && "border-primary bg-primary/5",
        isDragReject && "border-destructive/50 bg-destructive/5",
        !!selectedFile && "cursor-default border-muted bg-muted/10 hover:bg-muted/10",
        className
      )}
    >
      <input {...getInputProps()} />
      {renderContent()}
    </div>
  )
}
