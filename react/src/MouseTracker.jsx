import React from "react";

function MouseTracker({ username }) {
  const WS_URL = `ws://127.0.0.1:8000/ws?username=${username}`;
  const wsRef = useRef(null);
  const [users, setUsers] = useState([]);

  useEffect(() => {
    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setUsers(data); // Make sure your backend sends an array
      } catch (e) {
        console.error("Invalid JSON from server:", e);
      }
    };

    ws.onerror = (err) => {
      console.error("WebSocket error:", err);
    };

    ws.onclose = () => {
      console.warn("WebSocket closed.");
    };

    const handler = (e) => {
      console.log("Mouse moved", e.clientX, e.clientY);
      if (wsRef.current) {
        console.log("Sending mouse position");
        console.log("wsRef.current open", wsRef.current.readyState);

        wsRef.current.send(JSON.stringify({ x: e.clientX, y: e.clientY }));
      }
    };

    window.addEventListener("mousemove", handler);
    return () => {
      window.removeEventListener("mousemove", handler);
    };
  }, []);

  return (
    <div className="flex flex-col">
      {users?.map((user, idx) => (
        <span key={idx}>
          {user.username} ({user.state.x}, {user.state.y})
        </span>
      ))}
    </div>
  );
}

export default MouseTracker;
