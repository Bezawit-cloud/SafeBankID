import { Upload, FileText, X } from 'lucide-react';
import { useState } from 'react';

interface StepTwoProps {
  userFormData: {
    fullName: string;
    dateOfBirth: string;
    idNumber: string;
  };
  onNext: () => void;
  onBack: () => void;
}

export function StepTwo({ userFormData, onNext, onBack }: StepTwoProps) {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => setIsDragging(false);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files.length > 0) {
      setUploadedFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.length) {
      setUploadedFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!uploadedFile) return;

    setLoading(true);
    setResult(null);

    try {
      const formData = new FormData();

      formData.append('id_file', uploadedFile);
      formData.append('full_name', userFormData.fullName);
      formData.append('id_number', userFormData.idNumber);
      formData.append('dob', userFormData.dateOfBirth);

      // optional fields (can improve later)
      formData.append('gender', 'unknown');
      formData.append('expiry_date', '2030-01-01');

      const response = await fetch("http://127.0.0.1:8000/verify-id", {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      console.log("🔍 OCR RESPONSE:", data);

      setResult(data);

      // ✅ FIX: correct backend path
      if (response.ok && data?.ocr_result?.status === 'verified') {
        setTimeout(() => onNext(), 800);
      }

    } catch (error) {
      console.error('Upload error:', error);

      setResult({
        success: false,
        ocr_result: {
          status: 'failed'
        },
        error: 'Backend connection failed'
      });

    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">

      {/* ICON */}
      <div className="flex items-center justify-center mb-6">
        <div className="w-16 h-16 rounded-full bg-blue-100 flex items-center justify-center">
          <Upload className="w-8 h-8 text-[#3b82f6]" />
        </div>
      </div>

      {/* UPLOAD AREA */}
      {!uploadedFile ? (
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all ${
            isDragging
              ? 'border-[#3b82f6] bg-blue-50'
              : 'border-gray-300 hover:border-[#3b82f6] hover:bg-blue-50'
          }`}
        >
          <input
            type="file"
            id="fileUpload"
            className="hidden"
            accept="image/*,.pdf"
            onChange={handleFileChange}
          />

          <label htmlFor="fileUpload" className="cursor-pointer">
            <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-700 mb-2">
              Upload National ID or Passport
            </p>
            <p className="text-sm text-gray-500">
              Drag & drop or click to browse
            </p>
            <p className="text-xs text-gray-400 mt-2">
              JPG, PNG, PDF supported
            </p>
          </label>
        </div>
      ) : (
        <div className="border border-gray-300 rounded-xl p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 rounded-lg bg-blue-100 flex items-center justify-center">
                <FileText className="w-6 h-6 text-[#3b82f6]" />
              </div>

              <div>
                <p className="text-gray-900">{uploadedFile.name}</p>
                <p className="text-sm text-gray-500">
                  {(uploadedFile.size / 1024).toFixed(2)} KB
                </p>
              </div>
            </div>

            <button
              onClick={() => {
                setUploadedFile(null);
                setResult(null);
              }}
              className="p-2 hover:bg-gray-100 rounded-lg"
            >
              <X className="w-5 h-5 text-gray-500" />
            </button>
          </div>
        </div>
      )}

      {/* RESULT */}
      {result && (
        <div
          className={`text-sm px-4 py-3 rounded-xl border ${
            result?.ocr_result?.status === 'verified'
              ? 'bg-green-50 border-green-200 text-green-700'
              : 'bg-red-50 border-red-200 text-red-600'
          }`}
        >
          {result?.ocr_result?.status === 'verified'
            ? '✅ ID Verified Successfully'
            : '❌ Verification Failed — Name, ID or DOB did not match'}

          {/* DEBUG */}
          {result?.ocr_result?.match_scores && (
            <div className="mt-2 text-xs space-y-1 opacity-75">
              <p>Name: {result.ocr_result.match_scores.full_name}%</p>
              <p>ID: {result.ocr_result.match_scores.id_number}%</p>
              <p>DOB: {result.ocr_result.match_scores.dob}%</p>
            </div>
          )}
        </div>
      )}

      {/* BUTTONS */}
      <div className="flex gap-3">
        <button
          onClick={onBack}
          className="flex-1 border border-gray-300 py-3 rounded-xl"
        >
          Back
        </button>

        <button
          onClick={handleUpload}
          disabled={!uploadedFile || loading}
          className="flex-1 bg-[#3b82f6] text-white py-3 rounded-xl disabled:bg-gray-300"
        >
          {loading ? 'Verifying...' : 'Continue Verification'}
        </button>
      </div>

    </div>
  );
}