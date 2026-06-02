import { User } from 'lucide-react';
import { useState } from 'react';

interface StepOneProps {
  formData: {
    fullName: string;
    dateOfBirth: string;
    idNumber: string;
  };
  onChange: (field: string, value: string) => void;
  onNext: (userId: string) => void;
}

export function StepOne({ formData, onChange, onNext }: StepOneProps) {
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!formData.fullName || !formData.dateOfBirth || !formData.idNumber) {
      setError('Please fill in all fields.');
      return;
    }

    setLoading(true);

    try {
      const params = new URLSearchParams();
      params.append('name', formData.fullName);
      params.append('id_number', formData.idNumber);
      params.append('dob', formData.dateOfBirth);

      const res = await fetch("https://bezawit-ai-safebank-id.hf.space/add-user", {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: params,
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Server error');
      }

      const data = await res.json();
      console.log('✅ USER CREATED:', data);

      onNext(data.user_id); // ⭐ THIS IS id_number
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Failed to connect');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">

      <div className="flex items-center justify-center mb-6">
        <div className="w-16 h-16 rounded-full bg-blue-100 flex items-center justify-center">
          <User className="w-8 h-8 text-[#3b82f6]" />
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-600 text-sm px-4 py-3 rounded-xl">
          {error}
        </div>
      )}

      <div>
        <label className="block text-sm mb-2">Full Name</label>
        <input
          type="text"
          value={formData.fullName}
          onChange={(e) => onChange('fullName', e.target.value)}
          className="w-full px-4 py-3 border rounded-xl"
        />
      </div>

      <div>
        <label className="block text-sm mb-2">Date of Birth</label>
        <input
          type="date"
          value={formData.dateOfBirth}
          onChange={(e) => onChange('dateOfBirth', e.target.value)}
          className="w-full px-4 py-3 border rounded-xl"
        />
      </div>

      <div>
        <label className="block text-sm mb-2">ID Number</label>
        <input
          type="text"
          value={formData.idNumber}
          onChange={(e) => onChange('idNumber', e.target.value)}
          className="w-full px-4 py-3 border rounded-xl"
        />
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-[#3b82f6] text-white py-3 rounded-xl"
      >
        {loading ? 'Saving...' : 'Continue'}
      </button>
    </form>
  );
}