import os
from fastapi import FastAPI, WebSocket 
import uuid
from dotenv import load_dotenv  
import io
import openai
import wave




#----------------------------
SAMPLE_RATE = 24000  # Sample rate for audio processing matched with frontned
#----------------------------

load_dotenv()
app = FastAPI()

client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

class ClientConnectionManager:
    def __init__(self):
        self.connections: dict[str, WebSocket] = {}
        self.users: dict[str, str] = {}
        self.audio_buffers: dict[str, AudioBufferManager] = {}
        self.transcriptions: dict[str, str] = {}

    async def send_to_openai(self, audio_buffer: AudioBufferManager, prompt : str):
        wav_io = audio_buffer.get_wav_io()
        try:
            response = await client.audio.transcriptions.create(
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
            audio_buffer.reset()

    async def receive_message(self, id: str):
        ws = self.connections[id]
        data = await ws.receive_bytes()
        if data:
            # print(f"Received message from {self.users[id]}, data length: {len(data)}")
            # Add chunk to buffer
            self.audio_buffers[id].add_chunk(data)
            
            # Process if we have enough audio
            if self.audio_buffers[id].should_process():
                response = await self.send_to_openai(self.audio_buffers[id], prompt=self.transcriptions[id][-400:])
                if response:
                    self.transcriptions[id] = f"{self.transcriptions[id]} {response.text}"
                    await ws.send_text(self.transcriptions[id])
                    print("Response from OpenAI:", response)
                    # You could send the response back to the client here if needed
                    # await ws.send_text(response.text)

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        username = websocket.query_params['username']
        userid = str(uuid.uuid4())
        self.connections[userid] = websocket
        self.users[userid] = username
        self.audio_buffers[userid] = AudioBufferManager()
        self.transcriptions[userid] = ""
        print(f"User {username} connected with ID {userid}")
        return userid

    async def disconnect(self, id: str):
        # Process any remaining audio before disconnecting
        if len(self.audio_buffers[id].buffer) > 0:
            response = await self.send_to_openai(self.audio_buffers[id], prompt=self.transcriptions[id][-400:])
            if response:
                print("Final transcription:", response.text)
        
        await self.connections[id].close()
        del self.connections[id]
        del self.users[id]
        del self.audio_buffers[id]
        print(f"User {id} disconnected")

manager = ClientConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket): 
    id = await manager.connect(websocket)         
    try:
        while True:
            await manager.receive_message(id)
    except Exception as e:  
        print(f"Error: {e}")
    finally:
        await manager.disconnect(id)
