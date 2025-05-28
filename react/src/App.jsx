import { useState } from "react";
import PCM_Streamer from "./PCM_Streamer";
import MediaRecorderComponent from "./MediaRecorderComponent";

function App() {
  const [username, setUsername] = useState("");
  const [show, setShow] = useState(false);

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
            className="border m-5 rounded-sm px-2"
            placeholder="username"
          />
          {username.length !== 0 && (
            <button
              onClick={handleClick}
              className="bg-black text-white px-2 rounded-sm hover:opacity-70"
            >
              login
            </button>
          )}
        </div>
      )}

      {show && <PCM_Streamer username={username} />}
    </div>
  );
}

export default App;
