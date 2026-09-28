import React from 'react';
import { Language, LearningLevel, StudentProfile } from '../types';
import { 
  Globe, 
  Sun, 
  Moon, 
  Volume2, 
  VolumeX,
  Search,
  Flame,
  Coins
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
    { subject: 'Computer Science', topic: 'Select Topic' },
    { subject: 'Data Structures', topic: 'Binary Search Trees' },
    { subject: 'Data Structures', topic: 'Recursion & Dynamic Programming' },
    { subject: 'Database Management', topic: 'Normalization (1NF, 2NF, 3NF)' },
    { subject: 'Algorithms', topic: 'Binary Search & Sorting' },
    { subject: 'Operating Systems', topic: 'Process Synchronization' },
  ];

  const handleLanguageChange = (lang: Language) => {
    setProfile(prev => ({ ...prev, language: lang }));
  };

  const handleLevelChange = (level: LearningLevel) => {
    setProfile(prev => ({ ...prev, level: level }));
  };

  const handleSubjectChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selected = subjects[parseInt(e.target.value)];
    if (selected && selected.topic !== 'Select Topic') {
      setProfile(prev => ({
        ...prev,
        currentSubject: selected.subject,
        currentTopic: selected.topic
      }));
    }
  };

  // Calculate real mastery tokens
  const tokenPoints = Math.round(profile.masteryScore * 10);

  return (
    <header style={{
      height: '56px',
      width: '100%',
      padding: '0 20px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      backgroundColor: 'var(--bg-primary)',
      borderBottom: '1px solid var(--border-color)',
      zIndex: 5,
      userSelect: 'none'
    }}>
      {/* Left Topic/Subject Selector */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          background: 'var(--bg-secondary)',
          border: '1px solid var(--border-color)',
          borderRadius: 'var(--radius-md)',
          padding: '4px 10px'
        }}>
          <select
            onChange={handleSubjectChange}
            value={subjects.findIndex(s => s.topic === profile.currentTopic) >= 0 ? subjects.findIndex(s => s.topic === profile.currentTopic) : 0}
            style={{
              background: 'transparent',
              color: 'var(--text-primary)',
              border: 'none',
              fontSize: '0.84rem',
              fontWeight: 500,
              outline: 'none',
              cursor: 'pointer',
              fontFamily: 'var(--font-main)'
            }}
          >
            {subjects.map((item, idx) => (
              <option key={idx} value={idx} style={{ background: '#111418', color: '#f3f4f6' }}>
                {item.topic === 'Select Topic' ? 'Curriculum Topics' : `${item.subject} → ${item.topic}`}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Right Controls matching takeUforward reference */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        {/* Level Selector Pills */}
        <div style={{
          display: 'flex',
          background: 'var(--bg-secondary)',
          padding: '3px',
          borderRadius: 'var(--radius-md)',
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
                  padding: '3px 10px',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.72rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  background: isSelected ? 'var(--accent-primary)' : 'transparent',
                  color: isSelected ? '#ffffff' : 'var(--text-muted)',
                  transition: 'var(--transition-fast)'
                }}
              >
                {lvl}
              </button>
            );
          })}
        </div>

        {/* Language Selector */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          background: 'var(--bg-secondary)',
          border: '1px solid var(--border-color)',
          borderRadius: 'var(--radius-md)',
          padding: '4px 10px'
        }}>
          <Globe size={14} color="#60a5fa" />
          <select
            value={profile.language}
            onChange={(e) => handleLanguageChange(e.target.value as Language)}
            style={{
              background: 'transparent',
              color: 'var(--text-secondary)',
              border: 'none',
              fontSize: '0.78rem',
              fontWeight: 500,
              outline: 'none',
              cursor: 'pointer',
              fontFamily: 'var(--font-main)'
            }}
          >
            <option value="English" style={{ background: '#111418' }}>English</option>
            <option value="Hindi" style={{ background: '#111418' }}>हिन्दी</option>
            <option value="Telugu" style={{ background: '#111418' }}>తెలుగు</option>
          </select>
        </div>

        {/* Voice Mode Toggle */}
        <button
          onClick={() => setIsVoiceActive(!isVoiceActive)}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            background: isVoiceActive ? 'var(--accent-primary-subtle)' : 'var(--bg-secondary)',
            border: isVoiceActive ? '1px solid var(--accent-primary)' : '1px solid var(--border-color)',
            color: isVoiceActive ? '#60a5fa' : 'var(--text-muted)',
            padding: '5px 10px',
            borderRadius: 'var(--radius-md)',
            cursor: 'pointer',
            fontSize: '0.78rem',
            fontWeight: 500
          }}
          title="Toggle Spoken Tutor Voice Output"
        >
          {isVoiceActive ? <Volume2 size={15} color="#3b82f6" /> : <VolumeX size={15} color="var(--text-muted)" />}
          <span>{isVoiceActive ? 'Voice ON' : 'Voice Off'}</span>
        </button>

        {/* Gold Tokens Pill (matching reference screenshot icon & count) */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          padding: '5px 10px',
          borderRadius: 'var(--radius-md)',
          background: 'var(--bg-secondary)',
          border: '1px solid var(--border-color)',
          fontSize: '0.82rem',
          fontWeight: 600,
          color: 'var(--text-primary)'
        }}
        title="Mastery Points"
        >
          <Coins size={15} color="#fbbf24" />
          <span>{tokenPoints}</span>
        </div>

        {/* Fire Streak Badge (matching reference screenshot orange flame) */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          padding: '5px 10px',
          borderRadius: 'var(--radius-md)',
          background: 'var(--bg-secondary)',
          border: '1px solid var(--border-color)',
          fontSize: '0.82rem',
          fontWeight: 600,
          color: 'var(--text-primary)'
        }}
        title="Study Streak Days"
        >
          <Flame size={15} color="#f97316" />
          <span>{profile.studyStreakDays}</span>
        </div>
      </div>
    </header>
  );
};
