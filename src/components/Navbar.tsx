import React from 'react';
import { Language, LearningLevel, StudentProfile } from '../types';
import { 
  Globe, 
  Sparkles, 
  Sun, 
  Moon, 
  ChevronDown, 
  Volume2,
  SlidersHorizontal
} from 'lucide-react';

interface NavbarProps {
  profile: StudentProfile;
  setProfile: React.Dispatch<React.SetStateAction<StudentProfile>>;
  theme: 'dark' | 'light';
  setTheme: (theme: 'dark' | 'light') => void;
  isVoiceActive: boolean;
  setIsVoiceActive: (active: boolean) => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  profile,
  setProfile,
  theme,
  setTheme,
  isVoiceActive,
  setIsVoiceActive
}) => {
  const subjects = [
    { subject: 'Data Structures', topic: 'Binary Search Trees' },
    { subject: 'Data Structures', topic: 'Recursion & Dynamic Programming' },
    { subject: 'Database Management', topic: 'Normalization (1NF, 2NF, 3NF, BCNF)' },
    { subject: 'Algorithms', topic: 'Binary Search & Sorting' },
    { subject: 'Operating Systems', topic: 'Process Synchronization & Semaphores' },
  ];

  const handleLanguageChange = (lang: Language) => {
    setProfile(prev => ({ ...prev, language: lang }));
  };

  const handleLevelChange = (level: LearningLevel) => {
    setProfile(prev => ({ ...prev, level: level }));
  };

  const handleSubjectChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selected = subjects[parseInt(e.target.value)];
    if (selected) {
      setProfile(prev => ({
        ...prev,
        currentSubject: selected.subject,
        currentTopic: selected.topic
      }));
    }
  };

  return (
    <header className="glass-panel" style={{
      height: '70px',
      width: '100%',
      padding: '0 24px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      borderBottom: '1px solid var(--border-color)',
      zIndex: 5
    }}>
      {/* Active Subject & Topic Context */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: 600 }}>
            Active Learning Topic
          </span>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <select
              onChange={handleSubjectChange}
              style={{
                background: 'var(--bg-tertiary)',
                color: 'var(--text-primary)',
                border: '1px solid var(--border-color)',
                padding: '6px 12px',
                borderRadius: 'var(--radius-md)',
                fontFamily: 'var(--font-main)',
                fontSize: '0.9rem',
                fontWeight: 600,
                outline: 'none',
                cursor: 'pointer'
              }}
            >
              {subjects.map((item, idx) => (
                <option key={idx} value={idx}>
                  {item.subject} → {item.topic}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Control Tools: Language, Level, Voice & Theme */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        {/* Learning Level Quick Pills */}
        <div style={{
          display: 'flex',
          background: 'var(--bg-tertiary)',
          padding: '4px',
          borderRadius: 'var(--radius-full)',
          border: '1px solid var(--border-color)'
        }}>
          {(['Beginner', 'Intermediate', 'Advanced'] as LearningLevel[]).map((lvl) => {
            const isSelected = profile.level === lvl;
            return (
              <button
                key={lvl}
                onClick={() => handleLevelChange(lvl)}
                style={{
                  border: 'none',
                  padding: '4px 12px',
                  borderRadius: 'var(--radius-full)',
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  background: isSelected ? 'var(--accent-gradient)' : 'transparent',
                  color: isSelected ? '#ffffff' : 'var(--text-secondary)',
                  transition: 'var(--transition-fast)'
                }}
              >
                {lvl}
              </button>
            );
          })}
        </div>

        {/* Language Selector Dropdown */}
        <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
          <Globe size={16} color="var(--accent-cyan)" style={{ position: 'absolute', left: '10px' }} />
          <select
            value={profile.language}
            onChange={(e) => handleLanguageChange(e.target.value as Language)}
            style={{
              background: 'var(--bg-tertiary)',
              color: 'var(--text-primary)',
              border: '1px solid var(--border-color)',
              padding: '6px 12px 6px 32px',
              borderRadius: 'var(--radius-md)',
              fontFamily: 'var(--font-main)',
              fontSize: '0.85rem',
              fontWeight: 500,
              outline: 'none',
              cursor: 'pointer'
            }}
          >
            <option value="English">English</option>
            <option value="Hindi">हिन्दी (Hindi)</option>
            <option value="Telugu">తెలుగు (Telugu)</option>
          </select>
        </div>

        {/* Voice Speech Mode Indicator */}
        <button
          onClick={() => setIsVoiceActive(!isVoiceActive)}
          className={`btn ${isVoiceActive ? 'btn-primary pulse-active' : 'btn-secondary'}`}
          style={{
            padding: '6px 14px',
            fontSize: '0.85rem'
          }}
          title="Toggle Spoken Tutor Voice Output"
        >
          <Volume2 size={16} color={isVoiceActive ? '#ffffff' : 'var(--accent-primary)'} />
          <span>{isVoiceActive ? 'Voice ON' : 'Voice Mute'}</span>
        </button>

        {/* Dark/Light Theme Toggle */}
        <button
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          className="btn btn-ghost"
          style={{ padding: '8px', borderRadius: 'var(--radius-full)' }}
          title="Toggle Theme"
        >
          {theme === 'dark' ? <Sun size={18} color="var(--accent-amber)" /> : <Moon size={18} color="var(--accent-primary)" />}
        </button>
      </div>
    </header>
  );
};
