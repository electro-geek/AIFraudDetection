from pydantic import BaseModel, Field

class VoiceRequest(BaseModel):
    language: str = Field(..., description="Target language: Tamil, English, Hindi, Malayalam, Telugu")
    audioFormat: str = Field(..., description="Audio format, must be 'mp3'")
    audioBase64: str = Field(..., description="Base64 encoded MP3 audio data")

class VoiceResponse(BaseModel):
    status: str
    language: str
    classification: str
    confidenceScore: float
    explanation: str
