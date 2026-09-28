import React from 'react';
import { StudentProfile, Language, LearningLevel } from '../types';
import { updateStudentProfile } from '../services/api';
import { Settings, User, Globe, Sliders, Volume2, Shield } from 'lucide-react';

interface SettingsViewProps {
  profile: StudentProfile;
  setProfile: React.Dispatch<React.SetStateAction<StudentProfile>>;
}

export const SettingsView: React.FC<SettingsViewProps> = ({ profile, setProfile }) => {
  return (
    <div style={{
      padding: '28px 36px',
      height: 'calc(100vh - 56px)',
      overflowY: 'auto',
      display: 'flex',
      flexDirection: 'column',
      gap: '24px',
      background: 'var(--bg-primary)'
    }}>
      <div>
        <h2 style={{ fontSize: '1.35rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '10px', color: 'var(--text-primary)' }}>
          <Settings size={20} color="#60a5fa" /> Personal Tutor & Profile Settings
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.86rem', marginTop: '4px' }}>
          Configure your personal learning profile, default tutoring language, learning level, and pedagogical preferences.
        </p>
      </div>

      <div style={{ maxWidth: '750px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
        {/* Profile Info Card */}
        <div style={{
          padding: '22px 24px',
          borderRadius: 'var(--radius-lg)',
          backgroundColor: 'var(--bg-secondary)',
          border: '1px solid var(--border-color)',
          display: 'flex',
          flexDirection: 'column',
          gap: '16px'
        }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <User size={17} color="#60a5fa" /> Student Profile
          </h3>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.74rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600, marginBottom: '6px' }}>
                Student Name
              </label>
              <input
                type="text"
                value={profile.name}
                onChange={(e) => setProfile(prev => ({ ...prev, name: e.target.value }))}
                style={{
                  width: '100%',
                  background: 'var(--bg-tertiary)',
                  border: '1px solid var(--border-color)',
                  color: 'var(--text-primary)',
                  padding: '9px 13px',
                  borderRadius: 'var(--radius-md)',
                  fontFamily: 'var(--font-main)',
                  fontSize: '0.88rem',
                  outline: 'none'
                }}
                onFocus={(e) => e.currentTarget.style.borderColor = 'var(--accent-primary)'}
                onBlur={(e) => e.currentTarget.style.borderColor = 'var(--border-color)'}
              />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.74rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600, marginBottom: '6px' }}>
                Account Email
              </label>
              <input
                type="text"
                value={profile.email || 'student@edumate.internal'}
                disabled
                style={{
                  width: '100%',
                  background: 'var(--bg-tertiary)',
                  border: '1px solid var(--border-color)',
                  color: 'var(--text-muted)',
                  padding: '9px 13px',
                  borderRadius: 'var(--radius-md)',
                  fontFamily: 'var(--font-main)',
                  fontSize: '0.88rem',
                  cursor: 'not-allowed'
                }}
              />
            </div>
          </div>
        </div>

        {/* Pedagogical Preferences */}
        <div style={{
          padding: '22px 24px',
          borderRadius: 'var(--radius-lg)',
          backgroundColor: 'var(--bg-secondary)',
          border: '1px solid var(--border-color)',
          display: 'flex',
          flexDirection: 'column',
          gap: '16px'
        }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Sliders size={17} color="#60a5fa" /> Tutor Persona & Learning Level
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.74rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600, marginBottom: '6px' }}>
                Default Learning Level
              </label>
              <select
                value={profile.level}
                onChange={async (e) => {
                  const newLevel = e.target.value as LearningLevel;
                  setProfile(prev => ({ ...prev, level: newLevel }));
                  await updateStudentProfile({ level: newLevel });
                }}
                style={{
                  width: '100%',
                  background: 'var(--bg-tertiary)',
                  border: '1px solid var(--border-color)',
                  color: 'var(--text-primary)',
                  padding: '9px 13px',
                  borderRadius: 'var(--radius-md)',
                  fontFamily: 'var(--font-main)',
                  fontSize: '0.88rem',
                  outline: 'none',
                  cursor: 'pointer'
                }}
              >
                <option value="Beginner">Beginner (Simple terminology, basic examples, intuitive explanations)</option>
                <option value="Intermediate">Intermediate (Technical terminology, implementation details, moderate examples)</option>
                <option value="Advanced">Advanced (Technical depth, edge cases, complexity analysis, challenging problems)</option>
              </select>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.74rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600, marginBottom: '6px' }}>
                Preferred Language
              </label>
              <select
                value={profile.language}
                onChange={async (e) => {
                  const newLang = e.target.value as Language;
                  setProfile(prev => ({ ...prev, language: newLang }));
                  await updateStudentProfile({ language: newLang });
                }}
                style={{
                  width: '100%',
                  background: 'var(--bg-tertiary)',
                  border: '1px solid var(--border-color)',
                  color: 'var(--text-primary)',
                  padding: '9px 13px',
                  borderRadius: 'var(--radius-md)',
                  fontFamily: 'var(--font-main)',
                  fontSize: '0.88rem',
                  outline: 'none',
                  cursor: 'pointer'
                }}
              >
                <option value="English">English</option>
                <option value="Hindi">हिन्दी (Hindi)</option>
                <option value="Telugu">తెలుగు (Telugu)</option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
