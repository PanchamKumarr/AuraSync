import io
import os
import sys
from typing import Optional
import uuid

import modal 
from pydantic import BaseModel 
import torch
import torchaudio

# Environment configuration
APP_NAME = os.environ.get("MODAL_APP_NAME", "aurasync-backend")
HF_CACHE_VOLUME = os.environ.get("MODAL_HF_CACHE_VOLUME", "aurasync-hf-cache")
S3_SECRET_NAME = os.environ.get("MODAL_S3_SECRET_NAME", "aurasync-aws-secret")
S3_BUCKET_NAME = os.environ.get("MODAL_S3_BUCKET_NAME", "aurasync-storage")

app = modal.App(APP_NAME)

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("numpy==1.26.0", "torch==2.6.0")
    .pip_install_from_requirements("requirements.txt")
    .apt_install("ffmpeg")
)

volume = modal.Volume.from_name(HF_CACHE_VOLUME, create_if_missing=True)
s3_secret = modal.Secret.from_name(S3_SECRET_NAME)

class TextToSpeechRequest(BaseModel):
    text: str
    voice_s3_key: Optional[str] = None
    language: str = "en"
    exaggeration: float = 0.5
    cfg_weight: float = 0.5

class TextToSpeechResponse(BaseModel):
    s3_Key: str

@app.cls(
    image=image,
    gpu="L40S",
    volumes={
        "/root/.cache/huggingface": volume,
        "/s3-mount": modal.CloudBucketMount(S3_BUCKET_NAME, secret=s3_secret)
    },
    scaledown_window=120,
    secrets=[s3_secret]
)
class AuraSyncEngine:
    @modal.enter()
    def load_model(self):
        """Initialization stage: Loads the ML model into memory."""
        from chatterbox.mtl_tts import ChatterboxMultilingualTTS
        self.model = ChatterboxMultilingualTTS.from_pretrained(device="cuda")

    def _inference(self, text: str, voice_s3_key: Optional[str] = None, language: str = "en", exaggeration: float = 0.5, cfg_weight: float = 0.5):
        """Inference stage: Generates the audio tensor from text."""
        with torch.no_grad():
            if voice_s3_key:
                audio_prompt_path = f"/s3-mount/{voice_s3_key}"
                if not os.path.exists(audio_prompt_path):
                    raise FileNotFoundError(f"Prompt audio not found at {audio_prompt_path}")
                
                return self.model.generate(
                    text, 
                    audio_prompt_path=audio_prompt_path,
                    language_id=language,
                    exaggeration=exaggeration,
                    cfg_weight=cfg_weight
                )
            
            return self.model.generate(
                text,
                language_id=language,
                exaggeration=exaggeration,
                cfg_weight=cfg_weight
            )

    def _save_to_s3(self, wav: torch.Tensor) -> str:
        """Storage stage: Converts tensor to WAV and saves to S3 mount."""
        wav_cpu = wav.cpu()
        buffer = io.BytesIO()
        torchaudio.save(buffer, wav_cpu, self.model.sr, format="wav")
        buffer.seek(0)
        audio_bytes = buffer.read()

        audio_uuid = str(uuid.uuid4())  
        s3_key = f"tts/{audio_uuid}.wav"
        s3_path = f"/s3-mount/{s3_key}" 
        
        os.makedirs(os.path.dirname(s3_path), exist_ok=True)
        with open(s3_path, "wb") as f:
            f.write(audio_bytes)
            
        print(f"Saved audio to S3: {s3_key}")
        return s3_key

    @modal.fastapi_endpoint(method="POST", requires_proxy_auth=True)
    def generate_speech(self, request: TextToSpeechRequest) -> TextToSpeechResponse:
        """Endpoint orchestrating Inference and Storage."""
        wav = self._inference(
            text=request.text,
            voice_s3_key=request.voice_s3_key,
            language=request.language,
            exaggeration=request.exaggeration,
            cfg_weight=request.cfg_weight
        )
        
        s3_key = self._save_to_s3(wav)
        return TextToSpeechResponse(s3_Key=s3_key)


