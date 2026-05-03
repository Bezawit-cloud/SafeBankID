import { useState } from 'react';
import { Shield } from 'lucide-react';
import { ProgressStepper } from './components/ProgressStepper';
import { StepOne } from './components/StepOne';
import { StepTwo } from './components/StepTwo';
import { StepThree } from './components/StepThree';
import { SuccessState } from './components/SuccessState';
import { FailureState } from './components/FailureState';

export default function App() {
  const [currentStep, setCurrentStep] = useState(1);
  const [verificationState, setVerificationState] = useState<'in-progress' | 'success' | 'failure'>('in-progress');
  const [formData, setFormData] = useState({
    fullName: '',
    dateOfBirth: '',
    idNumber: '',
  });

  const handleFormChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleNext = () => {
    setCurrentStep(prev => prev + 1);
  };

  const handleBack = () => {
    setCurrentStep(prev => prev - 1);
  };

  const handleSuccess = () => {
    setVerificationState('success');
  };

  const handleFailure = () => {
    setVerificationState('failure');
  };

  const handleReset = () => {
    setCurrentStep(1);
    setVerificationState('in-progress');
    setFormData({
      fullName: '',
      dateOfBirth: '',
      idNumber: '',
    });
  };

  const handleRetry = () => {
    setVerificationState('in-progress');
    setCurrentStep(3);
  };

  return (
    <div className="min-h-screen bg-[#f8fafc] flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <div className="w-14 h-14 rounded-full bg-[#3b82f6] flex items-center justify-center">
              <Shield className="w-8 h-8 text-white" />
            </div>
          </div>
          <h1 className="text-3xl text-gray-900 mb-2">SAFEbankID</h1>
          <p className="text-gray-600">Secure AI Identity Verification</p>
          {verificationState === 'in-progress' && (
            <p className="text-sm text-gray-500 mt-2">
              Step {currentStep} of 3
            </p>
          )}
        </div>

        {/* Main Card */}
        <div className="bg-white rounded-2xl shadow-lg p-8">
          {verificationState === 'success' ? (
            <SuccessState onReset={handleReset} />
          ) : verificationState === 'failure' ? (
            <FailureState onRetry={handleRetry} onReset={handleReset} />
          ) : (
            <>
              <ProgressStepper currentStep={currentStep} totalSteps={3} />

              {currentStep === 1 && (
                <StepOne
                  formData={formData}
                  onChange={handleFormChange}
                  onNext={handleNext}
                />
              )}

              {currentStep === 2 && (
                <StepTwo onNext={handleNext} onBack={handleBack} />
              )}

              {currentStep === 3 && (
                <StepThree
                  onNext={handleSuccess}
                  onBack={handleBack}
                  onFail={handleFailure}
                />
              )}
            </>
          )}
        </div>

        {/* Footer */}
        <div className="text-center mt-6">
          <p className="text-xs text-gray-500">
            🔒 Your data is encrypted and secure
          </p>
        </div>
      </div>
    </div>
  );
}