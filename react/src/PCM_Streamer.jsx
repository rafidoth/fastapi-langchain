import React, { useEffect, useRef, useState } from "react";
import { getControlMessage } from "./utils";

function PCMStreamer({ username }) {
  const ws = useRef(null);
  const audioContext = useRef(null);
  const processor = useRef(null);
  const source = useRef(null);
  const stream = useRef(null);
  const [recordingStatus, setRecordingStatus] = useState("idle");
  const [receivedMessages, setReceivedMessages] = useState();

  const convertFloat32ToInt16 = (buffer) => {
    const l = buffer.length;
    const result = new Int16Array(l);
    for (let i = 0; i < l; i++) {
      result[i] = Math.max(-1, Math.min(1, buffer[i])) * 0x7fff;
    }
    return result.buffer;
  };

  const startStreaming = async () => {
    try {
      stream.current = await navigator.mediaDevices.getUserMedia({
        audio: true,
      });
      audioContext.current = new (window.AudioContext ||
        window.webkitAudioContext)({
        sampleRate: 24000, // Match this with your backend AI model
      });

      source.current = audioContext.current.createMediaStreamSource(
        stream.current,
      );
      processor.current = audioContext.current.createScriptProcessor(
        4096,
        1,
        1,
      );

      processor.current.onaudioprocess = (e) => {
        const input = e.inputBuffer.getChannelData(0);
        const pcm = convertFloat32ToInt16(input);
        if (ws.current?.readyState === 1) {
          ws.current.send(pcm);
        }
      };

      source.current.connect(processor.current);
      processor.current.connect(audioContext.current.destination);

      setRecordingStatus("recording");
    } catch (err) {
      console.error("Mic access error:", err);
    }
  };

  const stopStreaming = () => {
    if (processor.current) processor.current.disconnect();
    if (source.current) source.current.disconnect();
    if (audioContext.current) audioContext.current.close();
    if (stream.current)
      stream.current.getTracks().forEach((track) => track.stop());
    setRecordingStatus("stopped");
    if (ws.current?.readyState === 1) {
      ws.current.send(getControlMessage("done_talking"));
    }
  };

  const resetStreaming = () => {
    setRecordingStatus("idle");
  };

  useEffect(() => {
    ws.current = new WebSocket(`ws://localhost:8000/ws?username=${username}`);
    ws.current.binaryType = "arraybuffer";

    ws.current.onopen = () => {
      console.log("WebSocket connection opened");
    };

    ws.current.onmessage = (event) => {
      console.log("Received:", event.data);
      // const response = JSON.parse(event.data);
      setReceivedMessages(event.data || "");
    };

    ws.current.onclose = () => {
      console.log("WebSocket closed");
    };

    return () => {
      ws.current?.close();
    };
  }, [username]);

  return (
    <>
      <div>
        <p>Status: {recordingStatus}</p>
        <button
          onClick={startStreaming}
          disabled={recordingStatus === "recording"}
          className={`${recordingStatus === "recording" && "bg-black text-white rounded-sm "} px-2 mx-2`}
        >
          Start
        </button>
        <button
          onClick={stopStreaming}
          disabled={recordingStatus !== "recording"}
          className="px-2 mx-2"
        >
          Stop
        </button>
        <button onClick={resetStreaming} disabled={recordingStatus === "idle"}>
          Reset
        </button>
        {/* <button */}
        {/*   onMouseDown={() => { */}
        {/*     startStreaming(); */}
        {/*   }} */}
        {/*   onMouseUp={stopStreaming} */}
        {/*   className={`${ */}
        {/*     recordingStatus === "recording" && "bg-black text-white" */}
        {/*   } */}
        {/*   cursor-pointer border-2 rounded-sm px-2 */}
        {/*     `} */}
        {/* > */}
        {/*   push to talk */}
        {/* </button> */}
      </div>

      <div>
        <h3>Transcript:</h3>
        {receivedMessages}
      </div>
    </>
  );
}

export default PCMStreamer;
