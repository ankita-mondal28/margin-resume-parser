import { useEffect, useState } from "react";

const MESSAGES = [
  "Reading between the lines…",
  "Circling the good parts…",
  "Jotting a few notes in the margin…",
  "Double-checking the dates…",
];

export default function Loader() {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setIndex((i) => (i + 1) % MESSAGES.length);
    }, 1800);
    return () => clearInterval(timer);
  }, []);

  const message = MESSAGES[index];

  return (
    <div className="loading-stage">
      <svg className="pen-scribble" viewBox="0 0 120 60" aria-hidden="true">
        <path d="M5,45 C25,10 35,50 55,20 C70,0 85,45 115,15" />
      </svg>
      <p>{message}</p>
    </div>
  );
}
