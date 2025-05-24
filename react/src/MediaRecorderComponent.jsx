import React, { useState, useRef } from "react";
import { useEffect } from "react";

function MediaRecorderComponent({ username }) {
  const ws = useRef(null);
  const [recordingStatus, setRecordingStatus] = useState("idle"); // idle, recording, stopped
  const mediaRecorder = useRef(null);
  const stream = useRef(null);
  const [receivedMessages, setReceivedMessages] = useState([]);
  const delay = 5000; // 5 seconds

  const startListening = async () => {
    try {
      stream.current = await navigator.mediaDevices.getUserMedia({
        audio: true,
      });
      mediaRecorder.current = new MediaRecorder(stream.current);

      // const chunks = [];
      mediaRecorder.current.ondataavailable = (event) => {
        if (event.data.size === 0) return;
        console.log("data from mic : ", event.data);
        if (ws.current?.readyState === 1) {
          ws.current.send(event.data);
        }
      };

      mediaRecorder.current.onstop = () => {
        setRecordingStatus("stopped");
      };

      mediaRecorder.current.start(delay);
      setRecordingStatus("recording");
    } catch (error) {
      console.error("Error accessing media devices:", error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorder.current && mediaRecorder.current.state === "recording") {
      mediaRecorder.current.stop();
      stream.current.getTracks().forEach((track) => track.stop());
    }
  };

  const resetRecording = () => {
    setRecordingStatus("idle");
  };

  useEffect(() => {
    ws.current = new WebSocket(`ws://localhost:8000/ws?username=${username}`);
    ws.current.onopen = () => {
      console.log("WebSocket connection opened");
    };
    ws.current.onmessage = (event) => {
      console.log("Received message:", event.data);
      const response = JSON.parse(event.data);
      console.log("Parsed response:", response);
      setReceivedMessages(response.messages || []);
    };
    ws.current.onclose = () => {
      console.log("WebSocket connection closed");
    };
  }, []);

  return (
    <>
      <div>
        <p>Status: {recordingStatus}</p>
        <button
          onClick={startListening}
          disabled={recordingStatus === "recording"}
        >
          Start Recording
        </button>
        <button
          onClick={stopRecording}
          disabled={recordingStatus !== "recording"}
        >
          Stop Recording
        </button>
        <button onClick={resetRecording} disabled={recordingStatus === "idle"}>
          Reset
        </button>
      </div>
      <div>
        <h3>Messages:</h3>
        <ul>
          {receivedMessages.map((msg, index) => (
            <li key={index}>
              <span className="user">{msg.role}</span> : {msg.content}
            </li>
          ))}
        </ul>
      </div>
    </>
  );
}
export default MediaRecorderComponent;
