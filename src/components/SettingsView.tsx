import React from 'react';
import { StudentProfile, Language, LearningLevel } from '../types';
import { Settings, User, Globe, Sliders, Volume2, Shield } from 'lucide-react';

interface SettingsViewProps {
  profile: StudentProfile;
  setProfile: React.Dispatch<React.SetStateAction<StudentProfile>>;
}

export const SettingsView: React.FC<SettingsViewProps> = ({ profile, setProfile }) => {
  return (
    <div style={{
      padding: '32px',
      height: 'calc(100vh - 70px)',
      overflowY: 'auto',
      display: 'flex',
      flexDirection: 'column',
      gap: '24px',
      background: 'var(--bg-primary)'
    }}>
      <div>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Settings color="var(--accent-cyan)" /> Personal Tutor & Profile Settings
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginTop: '4px' }}>
          Configure your personal learning profile, default tutoring language, learning level, and voice parameters.
        </p>
      </div>

      <div style={{ maxWidth: '750px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
        {/* Profile Info Card */}
        <div className="glass-panel" style={{ padding: '24px', borderRadius: 'var(--radius-lg)' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <User size={18} color="var(--accent-primary)" /> Student Profile
          </h3>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '6px' }}>Student Name</label>
              <input
                type="text"
                value={profile.name}
                onChange={(e) => setProfile(prev => ({ ...prev, name: e.target.value }))}
                style={{
                  width: '100%',
                  background: 'var(--bg-tertiary)',
                  border: '1px solid var(--border-color)',
                  color: 'var(--text-primary)',
                  padding: '10px 14px',
                  borderRadius: 'var(--radius-md)',
                  fontFamily: 'var(--font-main)'
                }}
              />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '6px' }}>Email</label>
              <input
                type="text"
                value={profile.email}
                disabled
                style={{
                  width: '100%',
                  background: 'var(--bg-tertiary)',
                  border: '1px solid var(--border-color)',
                  color: 'var(--text-muted)',
                  padding: '10px 14px',
                  borderRadius: 'var(--radius-md)',
                  fontFamily: 'var(--font-main)'
                }}
              />
            </div>
          </div>
        </div>

        {/* Pedagogical Preferences */}
        <div className="glass-panel" style={{ padding: '24px', borderRadius: 'var(--radius-lg)' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Sliders size={18} color="var(--accent-cyan)" /> Tutor Persona & Learning Level
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '6px' }}>Default Learning Level</label>
              <select
                value={profile.level}
                onChange={(e) => setProfile(prev => ({ ...prev, level: e.target.value as LearningLevel }))}
                style={{
                  width: '100%',
                  background: 'var(--bg-tertiary)',
                  border: '1px solid var(--border-color)',
                  color: 'var(--text-primary)',
                  padding: '10px 14px',
                  borderRadius: 'var(--radius-md)',
                  fontFamily: 'var(--font-main)',
                  outline: 'none'
                }}
              >
                <option value="Beginner">Beginner (Simple terminology, basic examples, intuitive explanations)</option>
                <option value="Intermediate">Intermediate (Technical terminology, implementation details, moderate examples)</option>
                <option value="Advanced">Advanced (Technical depth, edge cases, complexity analysis, challenging problems)</option>
              </select>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '6px' }}>Preferred Language</label>
              <select
                value={profile.language}
                onChange={(e) => setProfile(prev => ({ ...prev, language: e.target.value as Language }))}
                style={{
                  width: '100%',
                  background: 'var(--bg-tertiary)',
                  border: '1px solid var(--border-color)',
                  color: 'var(--text-primary)',
                  padding: '10px 14px',
                  borderRadius: 'var(--radius-md)',
                  fontFamily: 'var(--font-main)',
                  outline: 'none'
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
