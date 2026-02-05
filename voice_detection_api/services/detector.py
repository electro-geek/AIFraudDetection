import base64
import librosa
import numpy as np
import io
import tempfile
import soundfile as sf
import os

def analyze_audio(request_data):
    """
    Analyzes the audio data to determine if it is AI-generated or HUMAN.
    Primary Logic: High-Frequency Cutoff Detection (Physics Based).
    AI models often generate audio with a hard frequency cutoff (e.g., at 8kHz or 11kHz),
    whereas real human recordings contain harmonics extending much higher.
    """
    try:
        # 1. Decode Base64
        audio_bytes = base64.b64decode(request_data.audioBase64)
        
        # Write to a temporary file
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_audio:
            temp_audio.write(audio_bytes)
            temp_path = temp_audio.name
            
        try:
            # 2. Load audio with librosa
            # sr=None is CRITICAL here to detect the original sampling rate limits
            y, sr = librosa.load(temp_path, sr=None)
            
            # --- PHYSICS-BASED LOGIC: HIGH FREQUENCY CUTOFF ---
            
            score = 0
            explanation_parts = []
            
            # A. Check Sampling Rate / Nyquist Frequency
            # Many TTS models output at 22050Hz or 24000Hz fixed.
            nyquist_freq = sr / 2
            
            # B. Spectral Rolloff (The "Cutoff" Point)
            # Find the frequency below which 99% of the total energy lies.
            # Real recordings usually fill the spectrum up to the mic's limit.
            rolloff_99 = librosa.feature.spectral_rolloff(y=y, sr=sr, roll_percent=0.99)
            avg_rolloff = np.mean(rolloff_99)
            
            # C. Energy Band Analysis
            # Compare energy in the "High Band" (e.g., 10kHz+) vs "Low Band"
            spectrogram = np.abs(librosa.stft(y))
            frequencies = librosa.fft_frequencies(sr=sr)
            
            # Define cutoff threshold (common AI artifact is ~11kHz due to 22k sr generation)
            cutoff_freq = 11000 
            
            # If the file itself has a low SR (e.g. 16k), it's low quality or old AI.
            if nyquist_freq < 12000:
                # Low resolution file - hard to distinguish, but suspicious context for "HD" voice
                score += 0.2
                explanation_parts.append(f"Low sampling rate ({sr}Hz) detected.")
            else:
                # File claims to be high res (e.g. 44.1k), let's check if it's empty upstairs
                
                # Check 1: The Hard Cutoff
                # If 99% of energy is below 12kHz, but file supports up to 22kHz
                if avg_rolloff < 12000:
                    score += 0.6 # Strong indicator of AI upsampling
                    explanation_parts.append(f"Unnatural hard frequency cutoff detected at {int(avg_rolloff)}Hz.")
                
                # Check 2: High Frequency "Dead Zone"
                high_band_idx = np.where(frequencies > 13000)[0]
                if len(high_band_idx) > 0:
                    high_band_energy = np.mean(spectrogram[high_band_idx, :])
                    # If effectively zero energy despite high SR container
                    if high_band_energy < 0.01:
                        score += 0.3
                        explanation_parts.append("Absence of natural high-frequency harmonics.")

            # --- SECONDARY CHECKS (Backup) ---
            # Used to confirm ambiguous cases
            
            # Texture Check (MFCC Variance) - AI is too smooth
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
            mfcc_var = np.mean(np.var(mfccs, axis=1))
            if mfcc_var < 500:
                score += 0.2
                explanation_parts.append("Lacks vocal texture variance.")

            # --- CLASSIFICATION DECISION ---
            
            threshold = 0.5
            
            if score >= threshold:
                classification = "AI_GENERATED"
                confidenceScore = min(0.6 + (score * 0.4), 0.99)
                explanation = " ".join(explanation_parts)
            else:
                classification = "HUMAN"
                confidenceScore = 0.88
                explanation = "Full frequency spectrum usage and natural harmonics detected."
            
            return {
                "classification": classification,
                "confidenceScore": round(confidenceScore, 2),
                "explanation": explanation
            }
            
        finally:
            # cleanup temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except Exception as e:
        raise ValueError(f"Error processing audio: {str(e)}")
