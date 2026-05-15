import { Camera, Loader2 } from 'lucide-react';
import { useRef, useState, useEffect } from 'react';

interface StepThreeProps {
  onNext: () => void;
  onBack: () => void;
  onFail: () => void;
  userId: string | null;
}

export function StepThree({ onNext, onBack, onFail, userId }: StepThreeProps) {
  const [isVerifying, setIsVerifying] = useState(false);
  const [status, setStatus] = useState('Camera starting...');
  const [cameraReady, setCameraReady] = useState(false);
  const [debug, setDebug] = useState<any>(null);

  const videoRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  useEffect(() => {
    const startCamera = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        streamRef.current = stream;

        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          videoRef.current.onloadedmetadata = () => {
            videoRef.current?.play();
            setCameraReady(true);
            setStatus('Camera ready. Click Start Verification.');
          };
        }
      } catch (err) {
        console.error('Camera error:', err);
        setStatus('Camera access denied. Please allow camera.');
      }
    };

    startCamera();

    return () => {
      streamRef.current?.getTracks().forEach((t) => t.stop());
    };
  }, []);

  const startVerification = async () => {
    if (!userId) {
      alert('User ID missing');
      return;
    }

    if (!cameraReady || !videoRef.current) {
      alert('Camera not ready');
      return;
    }

    setIsVerifying(true);
    setStatus('Capturing face...');
    setDebug(null);

    try {
      const video = videoRef.current;

      const canvas = document.createElement('canvas');
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      const ctx = canvas.getContext('2d');
      ctx?.drawImage(video, 0, 0);

      const blob = await new Promise<Blob | null>((resolve) =>
        canvas.toBlob(resolve, 'image/jpeg')
      );

      if (!blob) {
        setStatus('Failed to capture image');
        setIsVerifying(false);
        return;
      }

      const formData = new FormData();
      formData.append('file', blob, 'face.jpg');

      setStatus('Verifying identity...');

      const response = await fetch(`https://safebankid.onrender.com/verify-secure/${userId}`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      console.log('🔥 FULL BACKEND:', data);

      setDebug(data);

      // ✅ SUCCESS
      if (data.access === 'GRANTED') {
        setStatus('✅ Verification successful');
        setTimeout(() => onNext(), 800);
        return;
      }

      // ❌ SPECIFIC ERRORS
      if (data.error) {
        setStatus(`❌ ${data.error}`);
      } else if (data.confidence !== undefined && data.liveness_score !== undefined) {
        setStatus(
          `❌ Face mismatch (conf: ${data.confidence.toFixed(2)}, live: ${data.liveness_score.toFixed(2)})`
        );
      } else {
        setStatus('❌ Verification failed');
      }

      setTimeout(() => onFail(), 1500);

    } catch (err) {
      console.error(err);
      setStatus('Server connection error');
      setTimeout(() => onFail(), 1000);
    } finally {
      setIsVerifying(false);
    }
  };

  return (
    <div className="space-y-6">

      {/* CAMERA */}
      <div className="relative bg-gray-900 rounded-xl overflow-hidden aspect-[4/3]">
        <video
          ref={videoRef}
          autoPlay
          muted
          playsInline
          className="w-full h-full object-cover"
        />

        {!cameraReady && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-900">
            <div className="text-center text-white">
              <Camera className="w-16 h-16 mx-auto opacity-50" />
              <p className="mt-2 text-sm">{status}</p>
            </div>
          </div>
        )}

        {cameraReady && (
          <div className="absolute bottom-0 left-0 right-0 bg-black/50 text-white text-sm text-center py-2">
            {status}
          </div>
        )}
      </div>

      {/* DEBUG PANEL 🔥 */}
      {debug && (
        <div className="text-xs bg-gray-100 p-3 rounded-xl">
          <p><b>Access:</b> {debug.access}</p>
          <p><b>Confidence:</b> {debug.confidence}</p>
          <p><b>Liveness:</b> {debug.liveness_score}</p>
          <p><b>Error:</b> {debug.error}</p>
        </div>
      )}

      {/* BUTTONS */}
      <div className="flex gap-3">
        <button
          onClick={onBack}
          disabled={isVerifying}
          className="flex-1 border py-3 rounded-xl"
        >
          Back
        </button>

        <button
          onClick={startVerification}
          disabled={!cameraReady || isVerifying}
          className="flex-1 bg-[#3b82f6] text-white py-3 rounded-xl flex items-center justify-center gap-2 disabled:bg-gray-300"
        >
          {isVerifying ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Verifying...
            </>
          ) : (
            'Start Verification'
          )}
        </button>
      </div>

    </div>
  );
}