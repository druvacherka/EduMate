import React from 'react';
import { Language, LearningLevel, StudentProfile } from '../types';
import {
  Globe,
  Volume2,
  VolumeX,
  Flame,
  Coins,
  PanelLeftOpen,
  Sparkles,
} from 'lucide-react';

interface NavbarProps {
  profile: StudentProfile;
  setProfile: React.Dispatch<React.SetStateAction<StudentProfile>>;
  theme: 'dark' | 'light';
  setTheme: (theme: 'dark' | 'light') => void;
  isVoiceActive: boolean;
  setIsVoiceActive: (active: boolean) => void;
  isSidebarCollapsed?: boolean;
  onToggleSidebar?: () => void;
  onOpenOnboarding?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  profile,
  setProfile,
  theme,
  setTheme,
  isVoiceActive,
  setIsVoiceActive,
  isSidebarCollapsed = false,
  onToggleSidebar,
  onOpenOnboarding,
}) => {
  const handleLanguageChange = (lang: Language) => {
    setProfile((prev) => ({ ...prev, language: lang }));
  };

  const handleLevelChange = (level: LearningLevel) => {
    setProfile((prev) => ({ ...prev, level: level }));
  };

  const tokenPoints = Math.round(profile.masteryScore * 10);

  return (
    <header
      style={{
        height: '56px',
        width: '100%',
        padding: '0 20px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        backgroundColor: 'var(--bg-primary)',
        borderBottom: '1px solid var(--border-color)',
        zIndex: 5,
        userSelect: 'none',
      }}
    >
      {/* Left: Sidebar Toggle & Academic Context Action */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        {isSidebarCollapsed && onToggleSidebar && (
          <button
            onClick={onToggleSidebar}
            className="btn btn-ghost"
            style={{
              padding: '6px',
              color: 'var(--text-secondary)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              borderRadius: '6px',
              cursor: 'pointer',
              border: 'none',
              background: 'transparent',
            }}
            title="Expand sidebar"
          >
            <PanelLeftOpen size={18} color="#60a5fa" />
          </button>
        )}

        {onOpenOnboarding && (
          <button
            onClick={onOpenOnboarding}
            style={{
              background: 'rgba(255, 255, 255, 0.05)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '16px',
              padding: '4px 10px',
              fontSize: '0.75rem',
              color: '#cbd5e1',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: 4,
            }}
          >
            <Sparkles size={12} color="#fbbf24" /> Customize
          </button>
        )}
      </div>

      {/* Right Controls */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        {/* Level Selector Pills */}
        <div
          style={{
            display: 'flex',
            background: 'var(--bg-secondary)',
            padding: '3px',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--border-color)',
          }}
        >
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
                  transition: 'var(--transition-fast)',
                }}
              >
                {lvl}
              </button>
            );
          })}
        </div>

        {/* Language Selector */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            background: 'var(--bg-secondary)',
            border: '1px solid var(--border-color)',
            borderRadius: 'var(--radius-md)',
            padding: '4px 10px',
          }}
        >
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
              fontFamily: 'var(--font-main)',
            }}
          >
            <option value="English" style={{ background: '#111418' }}>
              English
            </option>
            <option value="Hindi" style={{ background: '#111418' }}>
              Hindi
            </option>
            <option value="Telugu" style={{ background: '#111418' }}>
              Telugu
            </option>
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
            fontWeight: 500,
          }}
          title="Toggle Spoken Tutor Voice Output"
        >
          {isVoiceActive ? <Volume2 size={15} color="#3b82f6" /> : <VolumeX size={15} color="var(--text-muted)" />}
          <span>{isVoiceActive ? 'Voice ON' : 'Voice Off'}</span>
        </button>

        {/* Gold Tokens Pill */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '5px 10px',
            borderRadius: 'var(--radius-md)',
            background: 'var(--bg-secondary)',
            border: '1px solid var(--border-color)',
            fontSize: '0.82rem',
            fontWeight: 600,
            color: 'var(--text-primary)',
          }}
          title="Mastery Points"
        >
          <Coins size={15} color="#fbbf24" />
          <span>{tokenPoints}</span>
        </div>

        {/* Fire Streak Badge */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '5px 10px',
            borderRadius: 'var(--radius-md)',
            background: 'var(--bg-secondary)',
            border: '1px solid var(--border-color)',
            fontSize: '0.82rem',
            fontWeight: 600,
            color: 'var(--text-primary)',
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
