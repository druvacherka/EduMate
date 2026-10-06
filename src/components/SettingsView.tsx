import React, { useState } from 'react';
import { StudentProfile, Language, LearningLevel } from '../types';
import { updateStudentProfile } from '../services/api';
import { Settings, User, Globe, Sliders, GraduationCap, Clock, Check, Save } from 'lucide-react';

interface SettingsViewProps {
  profile: StudentProfile;
  setProfile: React.Dispatch<React.SetStateAction<StudentProfile>>;
  onOpenOnboarding?: () => void;
}

export const SettingsView: React.FC<SettingsViewProps> = ({ profile, setProfile, onOpenOnboarding }) => {
  const [name, setName] = useState<string>(profile.name);
  const [educationLevel, setEducationLevel] = useState<string>(profile.educationLevel || '');
  const [institution, setInstitution] = useState<string>(profile.institution || '');
  const [streamBranch, setStreamBranch] = useState<string>(profile.streamBranch || '');
  const [academicYearSemester, setAcademicYearSemester] = useState<string>(profile.academicYearSemester || '');
  const [dailyHours, setDailyHours] = useState<number>(profile.dailyStudyHours || 0);
  const [savedSuccess, setSavedSuccess] = useState<boolean>(false);
  const [saving, setSaving] = useState<boolean>(false);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    const updated = await updateStudentProfile({
      name: name.trim(),
      level: profile.level,
      language: profile.language,
      education_level: educationLevel,
      institution: institution.trim(),
      stream_branch: streamBranch.trim(),
      academic_year_semester: academicYearSemester.trim(),
      daily_study_hours: dailyHours,
    });

    if (updated && updated.status === 'success') {
      setProfile((prev) => ({
        ...prev,
        name: name.trim(),
        educationLevel,
        institution,
        streamBranch,
        academicYearSemester,
        dailyStudyHours: dailyHours,
      }));
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3500);
    }
    setSaving(false);
  };

  return (
    <div
      style={{
        padding: '28px 36px',
        height: 'calc(100vh - 56px)',
        overflowY: 'auto',
        display: 'flex',
        flexDirection: 'column',
        gap: '24px',
        background: 'var(--bg-primary)',
      }}
    >
      <div>
        <h2
          style={{
            fontSize: '1.35rem',
            fontWeight: 700,
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            color: 'var(--text-primary)',
          }}
        >
          <Settings size={20} color="#60a5fa" /> Personal Learning Profile & Preferences
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.86rem', marginTop: '4px' }}>
          Configure your academic level, curriculum context, preferred language, and tutoring depth.
        </p>
      </div>

      {savedSuccess && (
        <div
          style={{
            maxWidth: '750px',
            background: 'rgba(16, 185, 129, 0.15)',
            border: '1px solid rgba(16, 185, 129, 0.3)',
            borderRadius: 12,
            padding: '12px 18px',
            color: '#6ee7b7',
            display: 'flex',
            alignItems: 'center',
            gap: 10,
          }}
        >
          <Check size={18} />
          <span>Profile and academic preferences saved successfully!</span>
        </div>
      )}

      <form onSubmit={handleSave} style={{ maxWidth: '750px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
        {/* Profile Card */}
        <div
          style={{
            padding: '22px 24px',
            borderRadius: 'var(--radius-lg)',
            backgroundColor: 'var(--bg-secondary)',
            border: '1px solid var(--border-color)',
            display: 'flex',
            flexDirection: 'column',
            gap: '16px',
          }}
        >
          <h3
            style={{
              fontSize: '1rem',
              fontWeight: 600,
              color: 'var(--text-primary)',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
            }}
          >
            <User size={17} color="#60a5fa" /> Student Identity
          </h3>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div>
              <label
                style={{
                  display: 'block',
                  fontSize: '0.74rem',
                  color: 'var(--text-muted)',
                  textTransform: 'uppercase',
                  fontWeight: 600,
                  marginBottom: '6px',
                }}
              >
                Student Name
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                style={{
                  width: '100%',
                  background: 'var(--bg-tertiary)',
                  border: '1px solid var(--border-color)',
                  color: 'var(--text-primary)',
                  padding: '9px 13px',
                  borderRadius: 'var(--radius-md)',
                  fontSize: '0.88rem',
                  outline: 'none',
                }}
              />
            </div>
            <div>
              <label
                style={{
                  display: 'block',
                  fontSize: '0.74rem',
                  color: 'var(--text-muted)',
                  textTransform: 'uppercase',
                  fontWeight: 600,
                  marginBottom: '6px',
                }}
              >
                Account Email
              </label>
              <input
                type="text"
                value={profile.email || ''}
                disabled
                style={{
                  width: '100%',
                  background: 'var(--bg-tertiary)',
                  border: '1px solid var(--border-color)',
                  color: 'var(--text-muted)',
                  padding: '9px 13px',
                  borderRadius: 'var(--radius-md)',
                  fontSize: '0.88rem',
                  cursor: 'not-allowed',
                }}
              />
            </div>
          </div>
        </div>

        {/* Education & Academic Context */}
        <div
          style={{
            padding: '22px 24px',
            borderRadius: 'var(--radius-lg)',
            backgroundColor: 'var(--bg-secondary)',
            border: '1px solid var(--border-color)',
            display: 'flex',
            flexDirection: 'column',
            gap: '16px',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3
              style={{
                fontSize: '1rem',
                fontWeight: 600,
                color: 'var(--text-primary)',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
              }}
            >
              <GraduationCap size={17} color="#60a5fa" /> Academic Hierarchy Context
            </h3>

            {onOpenOnboarding && (
              <button
                type="button"
                onClick={onOpenOnboarding}
                style={{
                  background: 'rgba(56, 189, 248, 0.1)',
                  border: '1px solid rgba(56, 189, 248, 0.3)',
                  color: '#38bdf8',
                  borderRadius: 8,
                  padding: '4px 10px',
                  fontSize: '0.78rem',
                  cursor: 'pointer',
                }}
              >
                Open Setup Wizard
              </button>
            )}
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div>
              <label
                style={{
                  display: 'block',
                  fontSize: '0.74rem',
                  color: 'var(--text-muted)',
                  textTransform: 'uppercase',
                  fontWeight: 600,
                  marginBottom: '6px',
                }}
              >
                Education Level
              </label>
              <select
                value={educationLevel}
                onChange={(e) => setEducationLevel(e.target.value)}
                style={{
                  width: '100%',
                  background: 'var(--bg-tertiary)',
                  border: '1px solid var(--border-color)',
                  color: 'var(--text-primary)',
                  padding: '9px 13px',
                  borderRadius: 'var(--radius-md)',
                  fontSize: '0.88rem',
                  outline: 'none',
                }}
              >
                <option value="">Select education level</option>
                <option value="Class 10">Class 10 (Secondary School)</option>
                <option value="Class 11">Class 11 (Higher Secondary)</option>
                <option value="Class 12 / Intermediate">Class 12 / Intermediate</option>
                <option value="Diploma / Polytechnic">Diploma / Polytechnic</option>
                <option value="B.Tech / Engineering">B.Tech / Engineering</option>
                <option value="Undergraduate / Degree">Undergraduate / Degree (B.Sc / BCA / B.Com)</option>
                <option value="Postgraduate (M.Tech / MCA)">Postgraduate (M.Tech / MCA)</option>
                <option value="Competitive / Govt Exams">Competitive / Govt Exams (UPSC, Banking, SSC)</option>
                <option value="General Skill Development">General Skill Development</option>
              </select>
            </div>

            <div>
              <label
                style={{
                  display: 'block',
                  fontSize: '0.74rem',
                  color: 'var(--text-muted)',
                  textTransform: 'uppercase',
                  fontWeight: 600,
                  marginBottom: '6px',
                }}
              >
                Board / University / College
              </label>
              <input
                type="text"
                placeholder="e.g. board, university, college, or school"
                value={institution}
                onChange={(e) => setInstitution(e.target.value)}
                style={{
                  width: '100%',
                  background: 'var(--bg-tertiary)',
                  border: '1px solid var(--border-color)',
                  color: 'var(--text-primary)',
                  padding: '9px 13px',
                  borderRadius: 'var(--radius-md)',
                  fontSize: '0.88rem',
                  outline: 'none',
                }}
              />
            </div>

            <div>
              <label
                style={{
                  display: 'block',
                  fontSize: '0.74rem',
                  color: 'var(--text-muted)',
                  textTransform: 'uppercase',
                  fontWeight: 600,
                  marginBottom: '6px',
                }}
              >
                Stream / Branch
              </label>
              <input
                type="text"
                value={streamBranch}
                onChange={(e) => setStreamBranch(e.target.value)}
                style={{
                  width: '100%',
                  background: 'var(--bg-tertiary)',
                  border: '1px solid var(--border-color)',
                  color: 'var(--text-primary)',
                  padding: '9px 13px',
                  borderRadius: 'var(--radius-md)',
                  fontSize: '0.88rem',
                  outline: 'none',
                }}
              />
            </div>

            <div>
              <label
                style={{
                  display: 'block',
                  fontSize: '0.74rem',
                  color: 'var(--text-muted)',
                  textTransform: 'uppercase',
                  fontWeight: 600,
                  marginBottom: '6px',
                }}
              >
                Academic Semester / Year
              </label>
              <input
                type="text"
                value={academicYearSemester}
                onChange={(e) => setAcademicYearSemester(e.target.value)}
                style={{
                  width: '100%',
                  background: 'var(--bg-tertiary)',
                  border: '1px solid var(--border-color)',
                  color: 'var(--text-primary)',
                  padding: '9px 13px',
                  borderRadius: 'var(--radius-md)',
                  fontSize: '0.88rem',
                  outline: 'none',
                }}
              />
            </div>
          </div>
        </div>

        {/* Pedagogical & Study Preferences */}
        <div
          style={{
            padding: '22px 24px',
            borderRadius: 'var(--radius-lg)',
            backgroundColor: 'var(--bg-secondary)',
            border: '1px solid var(--border-color)',
            display: 'flex',
            flexDirection: 'column',
            gap: '16px',
          }}
        >
          <h3
            style={{
              fontSize: '1rem',
              fontWeight: 600,
              color: 'var(--text-primary)',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
            }}
          >
            <Sliders size={17} color="#60a5fa" /> Tutor Depth & Language
          </h3>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div>
              <label
                style={{
                  display: 'block',
                  fontSize: '0.74rem',
                  color: 'var(--text-muted)',
                  textTransform: 'uppercase',
                  fontWeight: 600,
                  marginBottom: '6px',
                }}
              >
                Pedagogical Depth Level
              </label>
              <select
                value={profile.level}
                onChange={(e) => setProfile((prev) => ({ ...prev, level: e.target.value as LearningLevel }))}
                style={{
                  width: '100%',
                  background: 'var(--bg-tertiary)',
                  border: '1px solid var(--border-color)',
                  color: 'var(--text-primary)',
                  padding: '9px 13px',
                  borderRadius: 'var(--radius-md)',
                  fontSize: '0.88rem',
                  outline: 'none',
                }}
              >
                <option value="Beginner">Beginner (Intuitive analogies, fundamental concepts)</option>
                <option value="Intermediate">Intermediate (Practical implementations, trade-offs)</option>
                <option value="Advanced">Advanced (Internal mechanics, edge cases, complexity)</option>
              </select>
            </div>

            <div>
              <label
                style={{
                  display: 'block',
                  fontSize: '0.74rem',
                  color: 'var(--text-muted)',
                  textTransform: 'uppercase',
                  fontWeight: 600,
                  marginBottom: '6px',
                }}
              >
                Preferred Language
              </label>
              <select
                value={profile.language}
                onChange={(e) => setProfile((prev) => ({ ...prev, language: e.target.value as Language }))}
                style={{
                  width: '100%',
                  background: 'var(--bg-tertiary)',
                  border: '1px solid var(--border-color)',
                  color: 'var(--text-primary)',
                  padding: '9px 13px',
                  borderRadius: 'var(--radius-md)',
                  fontSize: '0.88rem',
                  outline: 'none',
                }}
              >
                <option value="English">English</option>
                <option value="Hindi">Hindi</option>
                <option value="Telugu">Telugu</option>
              </select>
            </div>
          </div>

          <div>
            <label
              style={{
                display: 'block',
                fontSize: '0.74rem',
                color: 'var(--text-muted)',
                textTransform: 'uppercase',
                fontWeight: 600,
                marginBottom: '6px',
              }}
            >
              Daily Available Study Hours: <strong style={{ color: '#38bdf8' }}>{dailyHours}h / day</strong>
            </label>
            <input
              type="range"
              min="0.5"
              max="6.0"
              step="0.5"
              value={dailyHours}
              onChange={(e) => setDailyHours(parseFloat(e.target.value))}
              style={{ width: '100%', accentColor: '#38bdf8' }}
            />
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 8 }}>
          <button
            type="submit"
            className="btn-primary"
            disabled={saving}
            style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '10px 24px' }}
          >
            <Save size={16} />
            <span>{saving ? 'Saving Changes...' : 'Save Profile Changes'}</span>
          </button>
        </div>
      </form>
    </div>
  );
};
