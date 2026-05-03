import { CheckCircle2, Shield } from 'lucide-react';

interface SuccessStateProps {
  onReset: () => void;
}

export function SuccessState({ onReset }: SuccessStateProps) {
  return (
    <div className="text-center space-y-6">
      <div className="flex items-center justify-center">
        <div className="relative">
          <div className="w-24 h-24 rounded-full bg-green-100 flex items-center justify-center">
            <CheckCircle2 className="w-16 h-16 text-green-600" />
          </div>
          <div className="absolute -bottom-2 -right-2 w-10 h-10 rounded-full bg-[#3b82f6] flex items-center justify-center">
            <Shield className="w-6 h-6 text-white" />
          </div>
        </div>
      </div>

      <div>
        <h2 className="text-2xl mb-2 text-gray-900">Verification Successful!</h2>
        <p className="text-gray-600">
          Your identity has been verified successfully.
        </p>
      </div>

      <div className="bg-green-50 border border-green-200 rounded-xl p-6 space-y-3">
        <div className="flex items-start space-x-3">
          <CheckCircle2 className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
          <div className="text-left">
            <p className="text-green-900">Identity confirmed</p>
            <p className="text-sm text-green-700">Your documents have been validated</p>
          </div>
        </div>
        <div className="flex items-start space-x-3">
          <CheckCircle2 className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
          <div className="text-left">
            <p className="text-green-900">Liveness check passed</p>
            <p className="text-sm text-green-700">Face verification successful</p>
          </div>
        </div>
        <div className="flex items-start space-x-3">
          <CheckCircle2 className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
          <div className="text-left">
            <p className="text-green-900">Secure authentication</p>
            <p className="text-sm text-green-700">Your account is now protected</p>
          </div>
        </div>
      </div>

      <button
        onClick={onReset}
        className="w-full bg-[#3b82f6] text-white py-3 rounded-xl hover:bg-blue-600 transition-all"
      >
        Complete Setup
      </button>
    </div>
  );
}
