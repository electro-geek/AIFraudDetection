from fastapi import FastAPI, Depends, HTTPException
from models.schemas import VoiceRequest, VoiceResponse
from middleware.auth import verify_api_key
from services.detector import analyze_audio

app = FastAPI(title="AI Voice Detection API")

@app.post("/api/voice-detection", response_model=VoiceResponse, dependencies=[Depends(verify_api_key)])
async def detect_voice(request: VoiceRequest):
    try:
        if request.audioFormat.lower() != "mp3":
             raise HTTPException(status_code=400, detail="Invalid audio format. Only 'mp3' is supported.")

        result = analyze_audio(request)
        
        return {
            "status": "success",
            "language": request.language,
            "classification": result["classification"],
            "confidenceScore": result["confidenceScore"],
            "explanation": result["explanation"]
        }

    except ValueError as ve:
        return {
            "status": "error",
            "language": request.language,
            "classification": "UNKNOWN",
            "confidenceScore": 0.0,
            "explanation": str(ve)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
