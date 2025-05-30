
class WhisperCommunication:
    def __init__(self, whisper_ws_url, openai_api_key, client_ws):
        self.whisper_ws_url = whisper_ws_url
        self.openai_api_key = openai_api_key
        self.client_ws = client_ws
        self.whisper_ws = None
        self.session_id = None
        self.listener_task = None
        self.session_ready = asyncio.Event()

    def init_session(self):
        session_config = {
            "type": "session.update",
            "input_audio_format": "pcm16",
            "input_audio_transcription": {
                "model": "gpt-4o-transcribe",
                "prompt": "",
                "language": "en"
            },
            "turn_detection": {
                "type": "server_vad",
                "threshold": 0.5,
                "prefix_padding_ms": 300,
                "silence_duration_ms": 500,
            },
            "input_audio_noise_reduction": {
                "type": "near_field"
            },
            "include": [
                "item.input_audio_transcription.logprobs"
            ]
        }
        return json.dumps(session_config)

    async def connect(self):
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "OpenAI-Beta": "realtime=v1"
        }
        self.whisper_ws = await websockets.connect(self.whisper_ws_url, additional_headers=headers)
        await self.whisper_ws.send(self.init_session())

        # Start listener loop in background
        self.listener_task = asyncio.create_task(self.listen_loop())

        # Wait for session created event before returning
        await self.session_ready.wait()

    async def listen_loop(self):
        try:
            if self.whisper_ws:
                async for message in self.whisper_ws:
                    data = json.loads(message)
                    print("Received from Whisper:", data)

                    # Detect session creation event and save session id
                    if data.get("type") == "transcription_session.created":
                        self.session_id = data.get("session", {}).get("id")
                        self.session_ready.set()

                    # Forward transcription or other messages to client_ws if needed
                    # Example: await self.client_ws.send(json.dumps(data))
            else:
                raise Exception("Whisper WebSocket is not connected")
        except Exception as e:
            print(f"Listener error: {e}")

    async def send_audio(self, pcm_audio):
        if not self.session_ready.is_set():
            print("Session not ready, skipping sending audio")
            return
        try:
            if self.whisper_ws:
                audio_base64 = encode_audio_to_base64(pcm_audio)
                payload = {
                    "type": "input_audio_buffer.append",
                    "audio": audio_base64,
                    "session": self.session_id
                }
                await self.whisper_ws.send(json.dumps(payload))
            else:
                raise Exception("Whisper WebSocket is not connected")
        except Exception as e:
            print(f"Error sending audio: {e}")

    async def close(self):
        if self.listener_task:
            self.listener_task.cancel()
        if self.whisper_ws:
            await self.whisper_ws.close()

