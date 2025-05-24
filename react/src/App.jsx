import { useEffect } from "react";
import { useState } from "react";
import MediaRecorderComponent from "./MediaRecorderComponent";

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

      {show && <MediaRecorderComponent username={username} />}
    </div>
  );
}

export default App;
