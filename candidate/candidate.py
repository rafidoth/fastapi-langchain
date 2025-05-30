from stt import AudioBufferManager
from fastapi import WebSocket
import os
import openai


class Candidate:
    def __init__(self, username: str, websocket: WebSocket):
        self.username = username,
        self.websocket = websocket
        self.audio_buffer = AudioBufferManager()
        self.transcription_buffer = ""
        self.openai_transcription_client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


    async def send_to_whisper(self, prompt : str):
        wav_io = self.audio_buffer.get_wav_io()
        try:
            response = await self.openai_transcription_client.audio.transcriptions.create(
                file=("audio.wav", wav_io, "audio/wav"),
                model="whisper-1",
                prompt=prompt,
                language="en",
                response_format="json",
                temperature=0.2  #betterr fluency with previous convo.
            )
            return response
        except Exception as e:
            print(f"Error sending to OpenAI: {e}")
            return None
        finally:
            self.audio_buffer.reset()

    async def process_candidate_audio(self, audio_bytes: bytes):
        self.add_audio_chunk(audio_bytes)
        if self.should_process() :
            response = await self.send_to_whisper(self.transcription_buffer[-400:])
            if response :
                self.transcription_buffer += f"{response.text}"
                await self.websocket.send_text(self.transcription_buffer)
                print("Candidate Said : ", response.text)



    def add_audio_chunk(self, audio_bytes: bytes):
        self.audio_buffer.add_chunk(audio_bytes)


    def should_process(self):
        return self.audio_buffer.should_process()

    async def send_text(self, message: str):
        await self.websocket.send_text(message)

    async def close(self):
        if len(self.audio_buffer.buffer) > 0:
            response = await self.send_to_whisper(prompt=self.transcription_buffer[-400:])
            if response:
                print("Final transcription:", response.text)
        
        await self.websocket.close()
