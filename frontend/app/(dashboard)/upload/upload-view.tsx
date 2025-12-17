"use client"

import { useState } from "react"
import { Upload, FileUp, AlertCircle, RefreshCcw, CheckCircle2 } from "lucide-react"
import { toast } from "sonner"
import { ReceiptDropzone } from "@/components/receipt-dropzone"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

export function UploadView() {
  const [file, setFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [uploadSuccess, setUploadSuccess] = useState(false)

  const handleFileSelect = (selectedFile: File) => {
    setFile(selectedFile)
    setError(null)
    setUploadSuccess(false)
  }

  const handleFileRemove = () => {
    setFile(null)
    setError(null)
    setUploadSuccess(false)
  }

  const handleUpload = async () => {
    if (!file) return

    setIsUploading(true)
    setError(null)
    setUploadSuccess(false)

    const formData = new FormData()
    formData.append("file", file)

    const promise = async () => {
      const response = await fetch("http://localhost:8001/receipts/upload", {
        method: "POST",
        body: formData
      })

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: "Unknown error occurred" }))
        throw new Error(error.detail || `Upload failed with status ${response.status}`)
      }

      const data = await response.json()
      setUploadSuccess(true)
      setFile(null)
      return data
    }

    toast.promise(promise(), {
      loading: "Uploading receipt...",
      success: () => {
        setIsUploading(false)
        return "Receipt uploaded successfully!"
      },
      error: (err) => {
        setIsUploading(false)
        const message = err instanceof Error ? err.message : "Failed to upload receipt"
        setError(message)
        return "Upload failed"
      },
    })
  }

  const handleRetry = () => {
    handleUpload()
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Upload className="h-8 w-8 text-primary" />
        <h1 className="text-3xl font-bold tracking-tight">Upload Receipt</h1>
      </div>

      <div className="mx-auto max-w-2xl space-y-6">
        {error && (
          <Alert variant="destructive" className="animate-in fade-in slide-in-from-top-2">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Upload Failed</AlertTitle>
            <AlertDescription className="flex items-center justify-between">
              <span>{error}</span>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={handleRetry}
                className="ml-4 h-8 border-destructive/50 hover:bg-destructive/10 hover:text-destructive"
              >
                <RefreshCcw className="mr-2 h-3 w-3" />
                Retry
              </Button>
            </AlertDescription>
          </Alert>
        )}

        {uploadSuccess && (
          <Alert className="border-green-500/50 text-green-600 dark:text-green-400 [&>svg]:text-green-600 animate-in fade-in slide-in-from-top-2">
            <CheckCircle2 className="h-4 w-4" />
            <AlertTitle>Success</AlertTitle>
            <AlertDescription>
              Your receipt has been uploaded and is being processed. You can see the status in the table below.
            </AlertDescription>
          </Alert>
        )}

        <ReceiptDropzone 
          onFileSelect={handleFileSelect}
          onFileRemove={handleFileRemove}
          selectedFile={file}
          disabled={isUploading}
        />

        <div className="flex justify-end">
          <Button 
            onClick={handleUpload} 
            disabled={!file || isUploading}
            className="w-full sm:w-auto"
            size="lg"
          >
            {isUploading ? (
              <>
                <RefreshCcw className="mr-2 h-4 w-4 animate-spin" />
                Processing...
              </>
            ) : (
              <>
                <FileUp className="mr-2 h-4 w-4" />
                Upload Receipt
              </>
            )}
          </Button>
        </div>
      </div>

      <div className="rounded-lg border border-muted-foreground/25 p-6">
        <h2 className="text-xl font-semibold mb-4">Processing Status</h2>
        <p className="text-center text-muted-foreground py-4">
          Upload status and processing queue will appear here
        </p>
      </div>
    </div>
  )
}
