"""
Audio Transcription Pipeline - SPARC Implementation

SPECIFICATION:
- Input: Audio bytes (WAV/MP3/OGG) from Twilio or browser
- Output: Transcribed text with < 800ms latency
- Constraints: Handle multiple formats, streaming capability
- Quality: High accuracy with noise tolerance

PSEUDOCODE:
1. Validate audio format and duration
2. Convert to required format if needed
3. Send to Whisper API
4. Handle response and errors
5. Return transcribed text

ARCHITECTURE:
- Adapter pattern for different audio sources
- Strategy pattern for transcription providers
- Circuit breaker for API failures

REFINEMENT:
- Pre-process audio for optimal quality
- Chunk large audio for streaming
- Cache common phrases

CODE:
"""
import io
import base64
from typing import Optional, Union, AsyncGenerator
import httpx
from openai import AsyncOpenAI
from dataclasses import dataclass
from enum import Enum
from app.config import settings

class AudioFormat(Enum):
    WAV = "wav"
    MP3 = "mp3"
    OGG = "ogg"
    WEBM = "webm"
    RAW = "raw"

@dataclass
class AudioData:
    """
    PATTERN: Data class for audio metadata
    WHY: Type safety and clear contracts
    """
    content: bytes
    format: AudioFormat
    sample_rate: Optional[int] = None
    duration: Optional[float] = None
    source: str = "unknown"

class TranscriptionStrategy:
    """
    PATTERN: Strategy pattern for multiple transcription providers
    WHY: Easy to swap providers or add fallbacks
    """
    async def transcribe(self, audio: AudioData) -> str:
        raise NotImplementedError

class WhisperStrategy(TranscriptionStrategy):
    """OpenAI Whisper implementation"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        
    async def transcribe(self, audio: AudioData) -> str:
        """
        CONCEPT: Direct API call with minimal processing
        WHY: Whisper handles most formats natively
        """
        # Create file-like object for API
        audio_file = io.BytesIO(audio.content)
        audio_file.name = f"audio.{audio.format.value}"
        
        try:
            # Call Whisper API
            transcript = await self.client.audio.transcriptions.create(
                model=settings.whisper_model,
                file=audio_file,
                response_format="text",
                language="en"  # Optimize for English
            )
            
            return transcript.strip()
            
        except Exception as e:
            print(f"Whisper transcription error: {e}")
            raise

class AudioPipeline:
    """
    Main audio processing pipeline
    PATTERN: Facade pattern for complex audio operations
    """
    
    def __init__(self):
        self.transcription_strategy = WhisperStrategy()
        self.max_duration = settings.max_audio_duration
        
    def _detect_format(self, audio_bytes: bytes) -> AudioFormat:
        """
        CONCEPT: Magic byte detection
        WHY: More reliable than file extensions
        """
        if audio_bytes.startswith(b'RIFF'):
            return AudioFormat.WAV
        elif audio_bytes.startswith(b'\xff\xfb') or audio_bytes.startswith(b'ID3'):
            return AudioFormat.MP3
        elif audio_bytes.startswith(b'OggS'):
            return AudioFormat.OGG
        elif b'webm' in audio_bytes[:40].lower():
            return AudioFormat.WEBM
        else:
            return AudioFormat.RAW
    
    def _validate_audio(self, audio: AudioData) -> bool:
        """
        PATTERN: Early validation
        WHY: Fail fast with clear errors
        """
        # Check size (rough duration estimate)
        max_size = 25 * 1024 * 1024  # 25MB limit
        if len(audio.content) > max_size:
            raise ValueError(f"Audio too large: {len(audio.content)} bytes")
        
        # Check format support
        supported_formats = [AudioFormat.WAV, AudioFormat.MP3, AudioFormat.OGG, AudioFormat.WEBM]
        if audio.format not in supported_formats:
            raise ValueError(f"Unsupported format: {audio.format}")
        
        return True
    
    async def transcribe_audio(
        self,
        audio_bytes: bytes,
        source: str = "unknown",
        format_hint: Optional[str] = None
    ) -> str:
        """
        PATTERN: Main entry point with automatic format detection
        WHY: Simple interface hiding complexity
        """
        # Detect or use provided format
        if format_hint:
            audio_format = AudioFormat(format_hint.lower())
        else:
            audio_format = self._detect_format(audio_bytes)
        
        # Create audio data object
        audio = AudioData(
            content=audio_bytes,
            format=audio_format,
            source=source
        )
        
        # Validate
        self._validate_audio(audio)
        
        # Transcribe
        text = await self.transcription_strategy.transcribe(audio)
        
        # Post-process
        text = self._clean_transcript(text)
        
        return text
    
    async def transcribe_base64(
        self,
        audio_base64: str,
        source: str = "browser"
    ) -> str:
        """
        CONCEPT: Base64 handling for browser audio
        WHY: Browser MediaRecorder outputs base64
        """
        # Decode base64
        audio_bytes = base64.b64decode(audio_base64)
        
        return await self.transcribe_audio(audio_bytes, source)
    
    async def transcribe_stream(
        self,
        audio_stream: AsyncGenerator[bytes, None],
        format: AudioFormat = AudioFormat.RAW
    ) -> AsyncGenerator[str, None]:
        """
        PATTERN: Streaming transcription for real-time processing
        WHY: Lower perceived latency for long audio
        NOTE: Simplified version - full implementation would chunk properly
        """
        buffer = io.BytesIO()
        chunk_size = 1024 * 512  # 512KB chunks
        
        async for chunk in audio_stream:
            buffer.write(chunk)
            
            # Process when we have enough data
            if buffer.tell() > chunk_size:
                audio_data = AudioData(
                    content=buffer.getvalue(),
                    format=format,
                    source="stream"
                )
                
                text = await self.transcription_strategy.transcribe(audio_data)
                if text:
                    yield text
                
                # Reset buffer
                buffer = io.BytesIO()
        
        # Process remaining audio
        if buffer.tell() > 0:
            audio_data = AudioData(
                content=buffer.getvalue(),
                format=format,
                source="stream"
            )
            
            text = await self.transcription_strategy.transcribe(audio_data)
            if text:
                yield text
    
    def _clean_transcript(self, text: str) -> str:
        """
        PATTERN: Post-processing for quality
        WHY: Remove artifacts and normalize text
        """
        if not text:
            return ""
        
        # Remove multiple spaces
        text = " ".join(text.split())
        
        # Remove common Whisper artifacts
        artifacts = ["[BLANK_AUDIO]", "[INAUDIBLE]", "..."]
        for artifact in artifacts:
            text = text.replace(artifact, "")
        
        # Trim
        text = text.strip()
        
        # Ensure it ends with proper punctuation
        if text and text[-1] not in ".!?":
            text += "."
        
        return text

# Global audio pipeline instance
audio_pipeline = AudioPipeline()