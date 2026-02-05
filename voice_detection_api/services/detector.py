import base64
import librosa
import numpy as np
import io
import tempfile
import soundfile as sf
import os

# --- INDIVIDUAL DETECTION STRATEGIES ---

def detect_spectral_cutoff(y, sr):
    """
    STRATEGY 1: PHYSICS / FREQUENCY CUTOFF
    Checks for hard frequency cutoffs often found in upsampled AI audio.
    """
    score = 0
    reason = None
    
    # 1. Check Sampling Rate vs Rolloff
    rolloff_99 = librosa.feature.spectral_rolloff(y=y, sr=sr, roll_percent=0.99)
    avg_rolloff = np.mean(rolloff_99)
    
    # "HD" audio should have energy up to 16kHz+. AI often cuts at 11kHz.
    if avg_rolloff < 12000 and sr > 24000:
        score = 0.9 # High probability of Fake
        reason = f"Unnatural frequency cutoff at {int(avg_rolloff)}Hz."
    elif avg_rolloff < 8000:
         score = 0.7 # Very low fidelity, suspicious
         reason = "Extremely low frequency bandwidth."
    else:
        score = 0.1
        reason = "Natural wide-band frequency response."
        
    return score, reason

def detect_texture_anomaly(y, sr):
    """
    STRATEGY 2: STATISTICAL / TEXTURE
    Checks for the 'perfect smoothness' of AI vs 'messy texture' of Humans using MFCCs.
    """
    # MFCC extraction
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
    # Variance across time (how much the texture changes)
    mfcc_var = np.mean(np.var(mfccs, axis=1)) 
    
    if mfcc_var < 500:
        return 0.7, "Low vocal texture variance (too smooth)."
    elif mfcc_var < 700:
        return 0.4, "Moderately suppressed vocal details."
    
    return 0.1, "Rich, natural vocal texture."

def detect_dynamics(y, sr):
    """
    STRATEGY 3: TEMPORAL DYNAMICS
    Checks Zero Crossing Rate (ZCR) for natural rapid fluctuations.
    """
    zcr = librosa.feature.zero_crossing_rate(y)
    zcr_var = np.var(zcr) # Variance of ZCR
    
    # Robots often have very stable ZCR. Humans are erratic.
    if zcr_var < 0.005: 
        return 0.6, "Unusually consistent zero-crossing rate."
    
    return 0.1, "Natural dynamic signal fluctuations."

# --- MAIN AGGREGATOR ---

def analyze_audio(request_data):
    """
    Ensemble Classifier: Runs multiple distinct logic checks and polls the results.
    """
    try:
        # Decode and Load
        audio_bytes = base64.b64decode(request_data.audioBase64)
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_audio:
            temp_audio.write(audio_bytes)
            temp_path = temp_audio.name
            
        try:
            y, sr = librosa.load(temp_path, sr=None)
            
            # --- POLLING STAGE ---
            
            # Run all strategies
            results = [
                detect_spectral_cutoff(y, sr),
                detect_texture_anomaly(y, sr),
                detect_dynamics(y, sr)
            ]
            
            # Aggregate scores
            total_score = 0
            explanations = []
            weights = [0.5, 0.3, 0.2] # Cutoff is most reliable (0.5), then Texture (0.3), then Dynamics (0.2)
            
            for i, (score, reason) in enumerate(results):
                weighted_score = score * weights[i]
                total_score += weighted_score
                if score > 0.4: # Only list reasons that flagged as suspicious
                    explanations.append(reason)
            
            # --- FINAL DECISION ---
            
            # Normalize total score (max possible approx 0.9)
            # Threshold: If weighted average > 0.45, we call it AI
            
            if total_score >= 0.45:
                classification = "AI_GENERATED"
                # Map score to confidence (0.45->0.70, 0.9->0.99)
                confidenceScore = min(0.70 + (total_score * 0.3), 0.99)
                final_explanation = " | ".join(explanations) if explanations else "Multiple synthetic anomalies detected."
            else:
                classification = "HUMAN"
                confidenceScore = 0.85 + (0.1 * (1.0 - total_score)) # Higher confidence if score is low
                final_explanation = "Passed multiple signal authenticity checks (Spectral, Texture, Dynamics)."
            
            return {
                "classification": classification,
                "confidenceScore": round(confidenceScore, 2),
                "explanation": final_explanation
            }
            
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except Exception as e:
        raise ValueError(f"Error processing audio: {str(e)}")
