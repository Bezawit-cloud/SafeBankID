#  SafeBankID

### Secure AI-Powered Identity Verification System



> **Automate KYC. Detect fraud. Verify identities in seconds.**

SafeBankID is a full-stack AI identity verification platform that automates customer onboarding using **OCR, facial recognition, and real-time liveness detection**.

It replaces slow, manual KYC processes with a **fast, scalable, and fraud-resistant AI system** for fintech, banking, and digital platforms.


---

##  Live Demo

**Frontend:** https://safe-bank-id.vercel.app/


---

##  Project Overview

Traditional identity verification often requires manual document inspection and face matching, making the process slow, expensive, and vulnerable to fraud.

SafeBankID automates this workflow through OCR, facial recognition, and liveness detection.

---

#  System Architecture



![System Architecture](docs/architecture2.png)

---

# 🔄 Verification Workflow


![Verification Workflow](docs/workflow.png)

---

##  Technical Stack

### Frontend

- React (Vite)
- TailwindCSS

### Backend

- FastAPI
- Python

### Database

- PostgreSQL
- Supabase

### AI / ML

- Tesseract OCR
- DeepFace
- OpenCV

### Deployment

- Vercel
- Hugging Face Spaces

---

##  Verification Process

### Step 1: Identity Initialization

- User enters personal information
- Data is validated
- Information is stored in PostgreSQL

### Step 2: Document Verification

- User uploads an ID document
- OCR extracts text information
- Face image is extracted
- Face embedding is generated and stored

### Step 3: Biometric Verification

- User performs webcam verification
- OpenCV performs liveness detection
- DeepFace generates live embedding
- Live embedding is compared against ID embedding

### Step 4: Result

- Verification Approved / Rejected
- Confidence Score Generated
- Liveness Score Generated

---


---
## 📡 API Documentation

### Base URL

### 🔹 1. Create User

**POST** `/users/create`

Creates a new user in the system.

#### Request Body
```json
{
  "name": "John Doe",
  "dob": "2000-01-01",
  "id_number": "A1234567"
}
```
#### Response
```
{
  "user_id": 1,
  "message": "User created successfully"
}
```
### 🔹 2. Upload ID Document

POST /verify/document

Processes ID document using OCR and extracts identity data.

Request (multipart/form-data)
file: ID image
user_id: integer
#### Response
```
{
  "extracted_name": "John Doe",
  "extracted_id": "A1234567",
  "face_embedding_status": "generated"
}
```
### 🔹 3. Face Verification (Live)

POST /verify/face

Compares live face with stored ID embedding.

Request Body
```
{
  "user_id": 1,
  "live_image": "base64_string"
}
```
Response
```
{
  "confidence_score": 0.92,
  "liveness_score": 0.88,
  "status": "VERIFIED"
}
```
### 🔹 4. Get Verification Status

GET /users/{user_id}/status

Response
```
{
  "user_id": 1,
  "verified": true,
  "confidence_score": 0.92,
  "liveness_score": 0.88
}
```
##  Database Schema

### users

| Column | Type |
|----------|----------|
| id | int4 |
| name | text |
| dob | date |
| id_number | varchar |

### biometric_verification

| Column | Type |
|----------|----------|
| user_id | int4 |
| confidence_score | float |
| liveness_score | float |
| verified_at | timestamp |

---

##  Key Features

- OCR-based ID verification
- Facial recognition using embeddings
- Real-time liveness detection
- Automated KYC workflow
- Secure PostgreSQL storage
- REST API architecture
- Responsive React frontend

---

##  Future Improvements

- Passport verification
- Driver's license verification
- Advanced anti-spoofing models
- Multi-factor authentication
- Administrative dashboard

---

##  Author

**Bezawit Assefa**
