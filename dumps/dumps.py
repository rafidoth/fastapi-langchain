
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
MODEL_NAME = "distil-whisper-large-v3-en"  


client = Groq(api_key=GROQ_API_KEY)


class GroqTranscriptResponse(BaseModel):
    text : str
    request_id : str


async def transcribe_audio(audio_bytes : bytes , prompt : str):
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not set.")
    try:
        # audio_bytes = await file.read()
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "aud.webm"
        print("Transcribing audio with prompt:", prompt)
        print("Audio file size:", len(audio_bytes), "bytes")
        transcription = client.audio.transcriptions.create(
          file=(audio_file.name, audio_file, "audio/webm"),
          model="whisper-large-v3",
          prompt= prompt,
          response_format="json",  # Optional
          language="en",  # Optional
          temperature=0.0  # Optional
        )
        response_text = transcription.text
        response_request_id = transcription.x_groq['id']
        return GroqTranscriptResponse(text=response_text, request_id=response_request_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))






class AudioBufferManager:
    def __init__(self, chunk_duration_sec=5, sample_rate=16000):
        self.buffer = b""
        self.sample_rate = sample_rate
        self.chunk_size = sample_rate * 2 * chunk_duration_sec  # 2 bytes per sample

    def add_chunk(self, pcm_chunk):
        self.buffer += pcm_chunk

    def should_process(self):
        return len(self.buffer) >= self.chunk_size

    def get_wav_io(self):
        import io, wave
        wav_io = io.BytesIO()
        with wave.open(wav_io, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            wf.writeframes(self.buffer)
        wav_io.seek(0)
        return wav_io

    def reset(self):
        self.buffer = b""


