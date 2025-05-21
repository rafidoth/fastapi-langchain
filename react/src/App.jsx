import { throttle } from "lodash";
import { useEffect } from "react";
import { useRef } from "react";
import { useState } from "react";
import useWebSocket from "react-use-websocket";

function App() {
  const [username, setUsername] = useState("");
  const [show, setShow] = useState(false);
  useEffect(() => {}, [username]);

  const handleClick = () => {
    setShow(true);
  };
  return (
    <div>
      {!show && (
        <div>
          <input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          {username.length !== 0 && (
            <button onClick={handleClick}>login</button>
          )}
        </div>
      )}

      {show && <WS username={username} />}
    </div>
  );
}

function WS({ username }) {
  const WS_URL = `ws://127.0.0.1:8000/ws`;
  const { sendJsonMessage, lastJsonMessage } = useWebSocket(WS_URL, {
    queryParams: { username },
  });
  const [users, setUsers] = useState();

  const T = 50;
  const sendJsonMessageThrottled = useRef(throttle(sendJsonMessage, T));

  console.log(users);

  useEffect(() => {
    window.addEventListener("mousemove", (e) => {
      sendJsonMessageThrottled.current({
        x: e.clientX,
        y: e.clientY,
      });
    });
  }, []);

  useEffect(() => {
    if (lastJsonMessage) {
      setUsers(lastJsonMessage);
    }
  }, [lastJsonMessage]);
  if (users) {
    return (
      <>
        <div className="flex flex-col">
          {users.map((user) => (
            <span>
              {user.username} ( {user.state.x}, {user.state.y})
            </span>
          ))}
        </div>
      </>
    );
  }
}

export default App;
