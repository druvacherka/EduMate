import React from 'react';
import { ActiveTab, StudentProfile } from '../types';
import { 
  MessageSquare, 
  BookOpen, 
  Award, 
  BarChart3, 
  Settings, 
  GraduationCap, 
  Flame,
  Globe
} from 'lucide-react';

interface SidebarProps {
  activeTab: ActiveTab;
  setActiveTab: (tab: ActiveTab) => void;
  profile: StudentProfile;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab, profile }) => {
  const navItems = [
    { id: 'tutor' as ActiveTab, label: 'AI Tutor Session', icon: MessageSquare, badge: 'Live' },
    { id: 'materials' as ActiveTab, label: 'Study Material (RAG)', icon: BookOpen },
    { id: 'quizzes' as ActiveTab, label: 'Practice & Quizzes', icon: Award },
    { id: 'analytics' as ActiveTab, label: 'Progress & Weak Areas', icon: BarChart3 },
    { id: 'settings' as ActiveTab, label: 'Tutor Settings', icon: Settings },
  ];

  const getLevelBadgeClass = (level: string) => {
    switch (level) {
      case 'Beginner': return 'badge-beginner';
      case 'Intermediate': return 'badge-intermediate';
      case 'Advanced': return 'badge-advanced';
      default: return 'badge-beginner';
    }
  };

  return (
    <aside className="glass-panel" style={{
      width: '280px',
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'space-between',
      padding: '24px 16px',
      borderRight: '1px solid var(--border-color)',
      zIndex: 10
    }}>
      <div>
        {/* Brand Logo */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '0 8px 24px 8px' }}>
          <div style={{
            width: '42px',
            height: '42px',
            borderRadius: 'var(--radius-md)',
            background: 'var(--accent-gradient)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: 'var(--accent-glow)'
          }}>
            <GraduationCap size={24} color="#ffffff" />
          </div>
          <div>
            <h1 style={{ fontSize: '1.25rem', fontWeight: 700, letterSpacing: '-0.5px' }}>
              Edu<span style={{ color: 'var(--accent-cyan)' }}>Mate</span>
            </h1>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 500 }}>
              AI Multilingual Personal Tutor
            </p>
          </div>
        </div>

        {/* Navigation Menu */}
        <nav style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`btn ${isActive ? 'btn-primary' : 'btn-ghost'}`}
                style={{
                  justifyContent: 'flex-start',
                  width: '100%',
                  padding: '12px 16px',
                  borderRadius: 'var(--radius-md)',
                  background: isActive ? 'var(--accent-gradient)' : 'transparent',
                  color: isActive ? '#ffffff' : 'var(--text-secondary)',
                  fontWeight: isActive ? 600 : 500
                }}
              >
                <Icon size={18} color={isActive ? '#ffffff' : 'var(--text-secondary)'} />
                <span style={{ flex: 1, textAlign: 'left', fontSize: '0.9rem' }}>{item.label}</span>
                {item.badge && (
                  <span style={{
                    fontSize: '0.65rem',
                    padding: '2px 6px',
                    borderRadius: 'var(--radius-full)',
                    background: 'rgba(255, 255, 255, 0.2)',
                    fontWeight: 700
                  }}>
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Student Learning Context Card */}
      <div className="glass-panel" style={{
        padding: '16px',
        borderRadius: 'var(--radius-lg)',
        background: 'rgba(255, 255, 255, 0.03)',
        display: 'flex',
        flexDirection: 'column',
        gap: '12px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
            <Flame size={16} color="var(--accent-amber)" />
            <span>{profile.studyStreakDays} Day Streak</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.8rem' }}>
            <Globe size={14} color="var(--accent-cyan)" />
            <span className="badge badge-lang">{profile.language}</span>
          </div>
        </div>

        <div>
          <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)' }}>
            {profile.name}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '8px' }}>
            {profile.currentSubject}
          </div>
          <span className={`badge ${getLevelBadgeClass(profile.level)}`}>
            Level: {profile.level}
          </span>
        </div>
      </div>
    </aside>
  );
};
