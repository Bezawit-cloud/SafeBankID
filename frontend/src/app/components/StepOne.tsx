import { User } from 'lucide-react';

interface StepOneProps {
  formData: {
    fullName: string;
    dateOfBirth: string;
    idNumber: string;
  };
  onChange: (field: string, value: string) => void;
  onNext: () => void;
}

export function StepOne({ formData, onChange, onNext }: StepOneProps) {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.fullName && formData.dateOfBirth && formData.idNumber) {
      onNext();
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="flex items-center justify-center mb-6">
        <div className="w-16 h-16 rounded-full bg-blue-100 flex items-center justify-center">
          <User className="w-8 h-8 text-[#3b82f6]" />
        </div>
      </div>

      <div>
        <label htmlFor="fullName" className="block text-sm mb-2 text-gray-700">
          Full Name
        </label>
        <input
          id="fullName"
          type="text"
          value={formData.fullName}
          onChange={(e) => onChange('fullName', e.target.value)}
          className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#3b82f6] focus:border-transparent transition-all"
          placeholder="Enter your full name"
          required
        />
      </div>

      <div>
        <label htmlFor="dateOfBirth" className="block text-sm mb-2 text-gray-700">
          Date of Birth
        </label>
        <input
          id="dateOfBirth"
          type="date"
          value={formData.dateOfBirth}
          onChange={(e) => onChange('dateOfBirth', e.target.value)}
          className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#3b82f6] focus:border-transparent transition-all"
          required
        />
      </div>

      <div>
        <label htmlFor="idNumber" className="block text-sm mb-2 text-gray-700">
          ID Number
        </label>
        <input
          id="idNumber"
          type="text"
          value={formData.idNumber}
          onChange={(e) => onChange('idNumber', e.target.value)}
          className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#3b82f6] focus:border-transparent transition-all"
          placeholder="Enter your ID number"
          required
        />
      </div>

      <button
        type="submit"
        className="w-full bg-[#3b82f6] text-white py-3 rounded-xl hover:bg-blue-600 transition-all"
      >
        Continue
      </button>
    </form>
  );
}
