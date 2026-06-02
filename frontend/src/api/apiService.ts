// frontend/src/api/apiService.ts

// Point this to your live Hugging Face URL
const API_BASE_URL = "https://bezawit-ai-safebank-id.hf.space";

export async function verifyUser(formData: FormData) {
  const response = await fetch(`${API_BASE_URL}/verify-id`, {
    method: "POST",
    body: formData, 
  });
  
  if (!response.ok) {
    throw new Error('Network response was not ok');
  }
  
  return await response.json();
}