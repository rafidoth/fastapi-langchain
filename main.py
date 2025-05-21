from fastapi import FastAPI, HTTPException,File, UploadFile, WebSocket
import uuid
import os
import io
from dotenv import load_dotenv  
from groq import Groq
from pydantic import BaseModel

load_dotenv()


app = FastAPI()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
MODEL_NAME = "distil-whisper-large-v3-en"  


client = Groq(api_key=GROQ_API_KEY)

@app.post("/transcribe/")
async def transcribe_audio(file: UploadFile = File(...)):
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not set.")
    try:
        audio_bytes = await file.read()
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "aud.mp3"
        transcription = client.audio.transcriptions.create(
          file=(audio_file.name, audio_file),
          model="whisper-large-v3",
          prompt="Specify context or spelling",  # Optional
          response_format="json",  # Optional
          language="en",  # Optional
          temperature=0.0  # Optional
        )
        print(transcription)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class State(BaseModel):
    x : float = 0.0
    y : float = 0.0


class User(BaseModel):
    username : str
    state : State


class ConnectionManager:
    def __init__(self) -> None:
        self.connections : dict[str, WebSocket] = {}
        self.users : dict[str, User] = {}

    async def receive_message(self, id : str):
            # print("Receiving message from ", self.users[id].username)
            ws = self.connections[id]
            data = await ws.receive_json()
            # print(data)
            new_state = State(**data)
            current_state = self.users[id].state

            if new_state!= current_state :
                self.users[id].state = new_state
                await self.broadcast()




    async def connect(self, websocket : WebSocket) :
        await websocket.accept()
        username = websocket.query_params['username']
        # print(username +" is joining")
        id =  uuid.uuid4()
        self.connections[str(id)] = websocket
        new_user = User(username=username, state=State())
        self.users[str(id)] = new_user
        # print("User Created ", self.users[str(id)])
        return str(id)


    async def broadcast(self) :
        json_response = [user.model_dump() for _ , user in self.users.items()]
        # print("broadcasted ", json_response)
        for _ , ws in self.connections.items():
            await ws.send_json(json_response)
    
    def disconnect(self, id : str ):
        del self.connections[id]
        del self.users[id]
        


manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket : WebSocket): 
        id = await manager.connect(websocket)         
        try :
            while True :
                await manager.receive_message(id)
        except Exception as e :  
            print(f"Error: {e}")
        finally:
            manager.disconnect(id)
            
