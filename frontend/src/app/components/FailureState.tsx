import { XCircle, AlertTriangle, RotateCcw } from 'lucide-react';

interface FailureStateProps {
  onRetry: () => void;
  onReset: () => void;
}

export function FailureState({ onRetry, onReset }: FailureStateProps) {
  return (
    <div className="text-center space-y-6">
      <div className="flex items-center justify-center">
        <div className="relative">
          <div className="w-24 h-24 rounded-full bg-red-100 flex items-center justify-center">
            <XCircle className="w-16 h-16 text-red-600" />
          </div>
          <div className="absolute -bottom-2 -right-2 w-10 h-10 rounded-full bg-red-600 flex items-center justify-center">
            <AlertTriangle className="w-6 h-6 text-white" />
          </div>
        </div>
      </div>

      <div>
        <h2 className="text-2xl mb-2 text-gray-900">Verification Failed</h2>
        <p className="text-gray-600">
          We couldn't verify your identity. Please try again.
        </p>
      </div>

      <div className="bg-red-50 border border-red-200 rounded-xl p-6 space-y-3">
        <div className="flex items-start space-x-3">
          <AlertTriangle className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" />
          <div className="text-left">
            <p className="text-red-900">Face not detected</p>
            <p className="text-sm text-red-700">Make sure your face is clearly visible</p>
          </div>
        </div>
        <div className="flex items-start space-x-3">
          <AlertTriangle className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" />
          <div className="text-left">
            <p className="text-red-900">Poor lighting conditions</p>
            <p className="text-sm text-red-700">Ensure adequate lighting on your face</p>
          </div>
        </div>
        <div className="flex items-start space-x-3">
          <AlertTriangle className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" />
          <div className="text-left">
            <p className="text-red-900">Document mismatch</p>
            <p className="text-sm text-red-700">Face doesn't match uploaded document</p>
          </div>
        </div>
      </div>

      <div className="flex gap-3">
        <button
          onClick={onReset}
          className="flex-1 border border-gray-300 text-gray-700 py-3 rounded-xl hover:bg-gray-50 transition-all"
        >
          Start Over
        </button>
        <button
          onClick={onRetry}
          className="flex-1 bg-[#3b82f6] text-white py-3 rounded-xl hover:bg-blue-600 transition-all flex items-center justify-center space-x-2"
        >
          <RotateCcw className="w-5 h-5" />
          <span>Try Again</span>
        </button>
      </div>
    </div>
  );
}
