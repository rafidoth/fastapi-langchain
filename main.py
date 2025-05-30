from fastapi import FastAPI, WebSocket 
import uuid
from dotenv import load_dotenv  
from brain import askGPT
import json
from candidate.candidate import Candidate


load_dotenv()
app = FastAPI()


class ClientConnectionManager:
    def __init__(self):
        self.connections: dict[str, Candidate] = {}

    async def receive_message(self, id: str):
        candidate = self.connections[id] 
        data = await candidate.websocket.receive()
        if data:
                if "type" in data:
                    if data.get("bytes") is not None:
                        audio_bytes= data["bytes"]
                        await candidate.process_candidate_audio(audio_bytes)
                    elif data.get("text") is not None and "control" in data["text"]:
                        control_message = json.loads(data['text'])
                        if control_message['event'] == 'done_talking' :
                            print('Calling Brain.....')
                            print(askGPT(candidate.transcription_buffer))

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        username = websocket.query_params['username']
        userid = str(uuid.uuid4())
        # self.connections[userid] = websocket
        # self.users[userid] = username
        # self.audio_buffers[userid] = AudioBufferManager()
        # self.transcriptions[userid] = ""
        new_candidate = Candidate( username = username, websocket = websocket)
        self.connections[userid] = new_candidate 

        print(f"User {username} connected with ID {userid}")
        return userid

    async def disconnect(self, id: str):
        # Process any remaining audio before disconnecting
        await self.connections[id].close()
        del self.connections[id]
        # await self.connections[id].close()
        # del self.connections[id]
        # del self.users[id]
        # del self.audio_buffers[id]
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
