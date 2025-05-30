import io
import wave
#----------------------------
SAMPLE_RATE = 24000  # Sample rate for audio processing matched with frontned
#----------------------------

class AudioBufferManager:
    def __init__(self, chunk_duration_sec=5, sample_rate=SAMPLE_RATE):
        self.buffer = b""
        self.sample_rate = sample_rate
        self.chunk_size = sample_rate * 2 * chunk_duration_sec  # 2 bytes per sample (16-bit audio)

    def add_chunk(self, pcm_chunk):
        self.buffer += pcm_chunk

    def should_process(self):
        return len(self.buffer) >= self.chunk_size

    def get_wav_io(self):
        wav_io = io.BytesIO()
        with wave.open(wav_io, 'wb') as wf:
            wf.setnchannels(1)  # Mono audio
            wf.setsampwidth(2)  # 2 bytes per sample (16-bit)
            wf.setframerate(self.sample_rate)
            wf.writeframes(self.buffer)
        wav_io.seek(0)
        return wav_io

    def reset(self):
        self.buffer = b""
