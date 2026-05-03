import { Camera, Loader2 } from 'lucide-react';
import { useState } from 'react';

interface StepThreeProps {
  onNext: () => void;
  onBack: () => void;
  onFail: () => void;
}

export function StepThree({ onNext, onBack, onFail }: StepThreeProps) {
  const [isVerifying, setIsVerifying] = useState(false);
  const [status, setStatus] = useState('Waiting for face detection...');

  const startVerification = () => {
    setIsVerifying(true);
    setStatus('Analyzing face...');

    // Simulate verification process with 80% success rate
    setTimeout(() => {
      const isSuccess = Math.random() > 0.2;
      if (isSuccess) {
        setStatus('Verification successful!');
        setTimeout(() => onNext(), 500);
      } else {
        setStatus('Verification failed');
        setTimeout(() => onFail(), 500);
      }
    }, 3000);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-center mb-6">
        <div className="w-16 h-16 rounded-full bg-blue-100 flex items-center justify-center">
          <Camera className="w-8 h-8 text-[#3b82f6]" />
        </div>
      </div>

      <div className="relative bg-gray-900 rounded-xl overflow-hidden aspect-[4/3] flex items-center justify-center">
        <div className="absolute inset-0 bg-gradient-to-br from-gray-800 to-gray-900"></div>
        <div className="relative z-10 text-center">
          <div className="w-48 h-48 border-4 border-dashed border-white/30 rounded-full mx-auto mb-4 flex items-center justify-center">
            <Camera className="w-20 h-20 text-white/40" />
          </div>
          <p className="text-white text-lg mb-2">Position your face in the frame</p>
          <div className="flex items-center justify-center space-x-2">
            {isVerifying && <Loader2 className="w-4 h-4 text-white animate-spin" />}
            <p className="text-white/70 text-sm">{status}</p>
          </div>
        </div>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
        <p className="text-sm text-blue-900">
          <strong>Tips for best results:</strong>
        </p>
        <ul className="text-sm text-blue-800 mt-2 space-y-1">
          <li>• Ensure good lighting on your face</li>
          <li>• Remove glasses or hats</li>
          <li>• Look directly at the camera</li>
        </ul>
      </div>

      <div className="flex gap-3">
        <button
          onClick={onBack}
          disabled={isVerifying}
          className="flex-1 border border-gray-300 text-gray-700 py-3 rounded-xl hover:bg-gray-50 transition-all disabled:bg-gray-100 disabled:cursor-not-allowed"
        >
          Back
        </button>
        <button
          onClick={startVerification}
          disabled={isVerifying}
          className="flex-1 bg-[#3b82f6] text-white py-3 rounded-xl hover:bg-blue-600 transition-all disabled:bg-blue-400 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
        >
          {isVerifying ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Verifying...</span>
            </>
          ) : (
            <span>Start Verification</span>
          )}
        </button>
      </div>
    </div>
  );
}
