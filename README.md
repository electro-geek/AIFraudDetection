Based on the provided problem statement, you need to build a secure **REST API** that distinguishes between real human voices and AI-generated synthetic voices across five specific languages.

Here is a breakdown of what needs to be done and how to implement it using **FastAPI**.

---

## 1. Project Requirements Overview

To succeed in this project, your system must meet these specific constraints:

* 
**Supported Languages:** Tamil, English, Hindi, Malayalam, and Telugu .


* 
**Input Format:** A single MP3 file sent as a **Base64** encoded string within a JSON body.


* 
**Security:** Every request must be authenticated using an **API Key** in the header (`x-api-key`).


* 
**Output:** A JSON response containing the classification (`AI_GENERATED` or `HUMAN`), a confidence score, and a brief explanation.



---

## 2. Implementation Steps

### Step A: Setup and Dependencies

You will need a Python environment with `fastapi`, `uvicorn` (for the server), and a library for audio processing/AI inference (like `librosa` for feature extraction or a pre-trained model from `HuggingFace`).

### Step B: Define the Data Models

Using `pydantic`, define the structure of the incoming request to ensure it matches the requirements exactly.

### Step C: Build the API Logic

1. 
**Authentication:** Use FastAPI's `Security` or `Header` dependencies to verify the `x-api-key`.


2. 
**Decoding:** Convert the incoming Base64 string back into binary MP3 data.


3. **Inference:** Pass the audio data through your AI model to determine if it is human or synthetic.
4. 
**Response:** Format the result according to the specified success or error JSON schemas.



---

## 3. FastAPI Project Structure

Here is a skeleton of how your `main.py` should look to comply with the problem statement:

```python
from fastapi import FastAPI, Header, HTTPException, status
from pydantic import BaseModel
import base64

app = FastAPI()

# [cite_start]1. Define Request Body [cite: 47]
class VoiceRequest(BaseModel):
    language: str  # Tamil, English, Hindi, Malayalam, Telugu
    audioFormat: str # Always "mp3"
    audioBase64: str

# [cite_start]2. Define Response Body [cite: 58]
class VoiceResponse(BaseModel):
    status: str
    language: str
    classification: str # AI_GENERATED or HUMAN
    confidenceScore: float
    explanation: str

[cite_start]API_KEY = "sk_test_123456789" # Store this securely [cite: 32]

@app.post("/api/voice-detection", response_model=VoiceResponse)
async def detect_voice(request: VoiceRequest, x_api_key: str = Header(None)):
    # [cite_start]3. Check API Key [cite: 30, 33]
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"status": "error", "message": "Invalid API key"}
        )

    try:
        # [cite_start]4. Decode Base64 [cite: 17, 26]
        audio_data = base64.b64decode(request.audioBase64)
        
        # --- PLACEHOLDER FOR AI MODEL LOGIC ---
        # 1. Save audio_data to temporary file or buffer
        # [cite_start]2. Run your detection model (Accuracy is key!) [cite: 77]
        # 3. Get classification and confidence score
        
        [cite_start]classification = "HUMAN" # Example result [cite: 21]
        confidence = 0.95
        reason = "Natural breathing patterns and varied prosody detected."
        # --------------------------------------

        return {
            "status": "success",
            "language": request.language,
            "classification": classification,
            "confidenceScore": confidence,
            "explanation": reason
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

```

---

## 4. Key Evaluation Criteria to Remember

* 
**Consistency:** Your model must perform reliably across all 5 languages.


* 
**Speed:** Ensure the API responds quickly (latency matters).


* 
**Strict Rules:** Do not hard-code results. The classification must be either `AI_GENERATED` or `HUMAN`.



Would you like me to help you find a pre-trained AI model suitable for detecting synthetic speech in these specific languages?

This document is structured to be read by an AI-driven IDE (like Cursor, Windsurf, or PearAI) to generate the complete project structure and logic required for the AI Voice Detection Challenge.

# Project Specification: Multi-lingual AI Voice Detection API

## 1. Project Overview

The goal is to build a secure REST API that classifies whether an MP3 voice recording is `AI_GENERATED` or `HUMAN`. The system must support five specific languages: Tamil, English, Hindi, Malayalam, and Telugu .

---

## 2. Technical Requirements

* **Framework:** FastAPI.
* 
**Input Format:** JSON containing a Base64-encoded MP3 file.


* 
**Authentication:** Header-based API Key (`x-api-key`) .


* 
**Response Format:** JSON with `status`, `classification`, `confidenceScore`, and `explanation`.


* 
**Strict Constraints:** No hard-coding of results; results must be generated via analysis.



---

## 3. Project Structure

Create the following directory structure:

```text
voice_detection_api/
├── main.py              # FastAPI application and routes
├── middleware/          # Security and Authentication
│   └── auth.py
├── models/              # Pydantic schemas for request/response
│   └── schemas.py
├── services/            # AI Inference and logic
│   └── detector.py
├── requirements.txt     # Python dependencies
└── .env                 # Secret API Key storage

```

---

## 4. Implementation Details

### A. Data Schemas (`models/schemas.py`)

Define the input and output models based on the challenge documentation:

* 
**Request:** Must include `language`, `audioFormat` (fixed as "mp3"), and `audioBase64`.


* 
**Response:** Must include `status`, `language`, `classification`, `confidenceScore`, and `explanation`.



### B. Security (`middleware/auth.py`)

* Implement a function to validate the `x-api-key` header .


* Reject any request missing the key with a `401 Unauthorized` status and a JSON error message .



### C. Logic & Inference (`services/detector.py`)

* 
**Decoding:** Convert `audioBase64` into bytes.


* 
**Analysis:** Process the MP3 across the 5 supported languages.


* 
**Classification:** Return `AI_GENERATED` for synthetic voices and `HUMAN` for real voices .


* 
**Explanation:** Generate a short, qualitative reason for the classification (e.g., "Unnatural pitch consistency").



### D. API Endpoint (`main.py`)

* 
**Endpoint:** `POST /api/voice-detection`.


* **Logic:**
1. Authenticate the request.


2. Parse the JSON body .


3. Invoke the detection service.


4. Return the response in the exact specified JSON format .





---

## 5. Evaluation Success Criteria

* 
**Accuracy:** High detection rate of synthetic vs. real voices.


* 
**Reliability:** The API must handle multiple requests and respond within a reasonable time.


* 
**Format Compliance:** Ensure the JSON keys and values match the documentation perfectly.



---

## 6. Prompt for your IDE

> "Using the provided `.md` specification, generate a FastAPI project. Ensure that the API key authentication is strictly enforced via headers. Use a placeholder logic in `services/detector.py` for the AI model but include the necessary imports for `librosa` and `numpy` for feature extraction. Ensure the Base64 decoding of the MP3 input is handled safely before analysis."

Would you like me to generate the actual code for the `requirements.txt` file to get your environment started?