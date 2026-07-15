export default function ScoreBadge({ score, note }) {
  return (
    <div className="score-wrap">
      <svg className="score-circle-svg" viewBox="0 0 96 96" aria-hidden="true">
        <path
          d="M48,9 C71,7 90,24 89,47 C88,70 69,90 46,89 C23,88 6,68 8,45 C9,23 26,8 48,9 Z"
          fill="none"
          stroke="var(--berry)"
          strokeWidth="3.5"
          strokeLinecap="round"
        />
        <text x="48" y="46" textAnchor="middle" className="score-number">
          {score}
        </text>
        <text x="48" y="62" textAnchor="middle" className="score-label">
          OUT OF 100
        </text>
      </svg>
      <p className="score-note">{note || "Solid resume overall!"}</p>
    </div>
  );
}
