import ScoreBadge from "./ScoreBadge.jsx";

function formatDateRange(start, end) {
  if (!start && !end) return null;
  return `${start || "—"} – ${end || "Present"}`;
}

export default function ResultsPaper({ data, onReset }) {
  const {
    full_name,
    email,
    phone,
    location,
    links = [],
    summary,
    skills = [],
    education = [],
    experience = [],
    resume_score,
    score_breakdown,
    suggested_roles = [],
  } = data;

  return (
    <div className="results-stage">
      {/* Left: the resume, laid out like a typed page */}
      <div className="paper-card resume-sheet">
        <div className="resume-header">
          <h2>{full_name || "Your Resume"}</h2>
          <div className="resume-contact">
            {email && <span>{email}</span>}
            {phone && <span>{phone}</span>}
            {location && <span>{location}</span>}
            {links.map((link) => (
              <span key={link}>{link}</span>
            ))}
          </div>
        </div>

        {summary && (
          <div className="resume-section">
            <h3>📝 Summary</h3>
            <p className="resume-summary">{summary}</p>
          </div>
        )}

        {skills.length > 0 && (
          <div className="resume-section">
            <h3>✨ Skills</h3>
            <div className="skill-chips">
              {skills.map((skill) => (
                <span className="skill-chip" key={skill}>
                  {skill}
                </span>
              ))}
            </div>
          </div>
        )}

        {experience.length > 0 && (
          <div className="resume-section">
            <h3>💼 Experience</h3>
            {experience.map((entry, i) => (
              <div className="entry-block" key={i}>
                <div className="entry-title-row">
                  <span>
                    {entry.title || "Role"} {entry.company ? `· ${entry.company}` : ""}
                  </span>
                  {formatDateRange(entry.start_date, entry.end_date) && (
                    <span className="entry-dates">{formatDateRange(entry.start_date, entry.end_date)}</span>
                  )}
                </div>
                {entry.description && <p className="entry-description">{entry.description}</p>}
              </div>
            ))}
          </div>
        )}

        {education.length > 0 && (
          <div className="resume-section">
            <h3>🎓 Education</h3>
            {education.map((entry, i) => (
              <div className="entry-block" key={i}>
                <div className="entry-title-row">
                  <span>{entry.institution || "Institution"}</span>
                  {formatDateRange(entry.start_date, entry.end_date) && (
                    <span className="entry-dates">{formatDateRange(entry.start_date, entry.end_date)}</span>
                  )}
                </div>
                {(entry.degree || entry.field_of_study) && (
                  <div className="entry-subtitle">
                    {[entry.degree, entry.field_of_study].filter(Boolean).join(", ")}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Right: margin annotations */}
      <div className="margin-column">
        <div className="sticky-note">
          <div className="washi" />
          <ScoreBadge score={resume_score} note={score_breakdown} />
        </div>

        {suggested_roles.length > 0 && (
          <div className="sticky-note">
            <div className="washi" />
            <h3 style={{ fontFamily: "var(--font-hand)", fontSize: 20, margin: "0 0 8px", color: "var(--berry-deep)" }}>
              You'd be great as…
            </h3>
            {suggested_roles.map((role, i) => (
              <div className="role-card" key={i}>
                <div className="role-title">{role.title}</div>
                <div className="role-reason">{role.reason}</div>
              </div>
            ))}
          </div>
        )}

        <button className="reset-link" onClick={onReset}>
          ↺ Read another resume
        </button>
      </div>
    </div>
  );
}
