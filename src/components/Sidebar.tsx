import React from 'react';
import { ActiveTab, StudentProfile } from '../types';
import { 
  LayoutDashboard,
  MessageSquare, 
  BookOpen, 
  Code2, 
  Settings, 
  GraduationCap, 
  PanelLeftClose,
  PanelLeftOpen,
  ChevronDown,
  ChevronUp,
  FileText,
  Compass,
  FolderClosed,
  ListTodo
} from 'lucide-react';

interface SidebarProps {
  activeTab: ActiveTab;
  setActiveTab: (tab: ActiveTab) => void;
  profile: StudentProfile;
  isCollapsed?: boolean;
  onToggleCollapse?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ 
  activeTab, 
  setActiveTab, 
  profile,
  isCollapsed = false,
  onToggleCollapse 
}) => {
  const getInitials = (name: string) => {
    if (!name || name === 'Student') return 'CD';
    const parts = name.trim().split(/\s+/);
    if (parts.length >= 2) return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
    return name.slice(0, 2).toUpperCase();
  };

  const navItems = [
    { id: 'analytics' as ActiveTab, label: 'Dashboard', icon: LayoutDashboard },
    { id: 'tutor' as ActiveTab, label: 'AI Tutor Session', icon: MessageSquare, badge: 'Live' },
    { id: 'quizzes' as ActiveTab, label: 'Practice & Quizzes', icon: Code2 },
    { id: 'materials' as ActiveTab, label: 'Study Material (RAG)', icon: BookOpen },
    { id: 'settings' as ActiveTab, label: 'Tutor Settings', icon: Settings },
  ];

  return (
    <aside style={{
      width: isCollapsed ? '68px' : '240px',
      minWidth: isCollapsed ? '68px' : '240px',
      height: '100%',
      backgroundColor: 'var(--bg-sidebar)',
      borderRight: '1px solid var(--border-color)',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'space-between',
      padding: isCollapsed ? '16px 8px' : '16px 12px',
      zIndex: 10,
      userSelect: 'none',
      transition: 'width 0.25s cubic-bezier(0.4, 0, 0.2, 1), min-width 0.25s cubic-bezier(0.4, 0, 0.2, 1), padding 0.2s ease',
      overflow: 'hidden'
    }}>
      <div>
        {/* Brand Header */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: isCollapsed ? 'center' : 'space-between',
          padding: isCollapsed ? '4px 0 16px 0' : '4px 8px 18px 8px',
          borderBottom: '1px solid var(--border-subtle)',
          minHeight: '44px'
        }}>
          {!isCollapsed && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div style={{
                width: '28px',
                height: '28px',
                borderRadius: '6px',
                background: 'var(--accent-primary)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#ffffff',
                flexShrink: 0
              }}>
                <GraduationCap size={16} />
              </div>
              <span style={{ fontSize: '0.98rem', fontWeight: 700, color: 'var(--text-primary)', letterSpacing: '-0.3px', whiteSpace: 'nowrap' }}>
                Edu<span style={{ color: '#60a5fa' }}>Mate</span>
              </span>
            </div>
          )}
          <button
            onClick={onToggleCollapse}
            className="btn btn-ghost"
            style={{ 
              padding: '6px', 
              color: 'var(--text-muted)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              borderRadius: '6px',
              cursor: 'pointer'
            }}
            title={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
            aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {isCollapsed ? <PanelLeftOpen size={18} color="#60a5fa" /> : <PanelLeftClose size={16} />}
          </button>
        </div>

        {/* Section: Prep & Learn */}
        <div style={{ marginTop: '16px' }}>
          {!isCollapsed ? (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '4px 8px',
              fontSize: '0.72rem',
              fontWeight: 600,
              textTransform: 'uppercase',
              color: 'var(--text-muted)',
              letterSpacing: '0.5px'
            }}>
              <span>Prep</span>
              <ChevronUp size={14} />
            </div>
          ) : (
            <div style={{ height: '1px', background: 'var(--border-subtle)', margin: '4px 6px 8px 6px' }} />
          )}

          <nav style={{ display: 'flex', flexDirection: 'column', gap: '3px', marginTop: '4px' }}>
            {navItems.slice(0, 3).map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  title={item.label}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: isCollapsed ? 'center' : 'flex-start',
                    gap: '10px',
                    width: '100%',
                    padding: isCollapsed ? '10px 0' : '8px 10px',
                    borderRadius: 'var(--radius-md)',
                    border: 'none',
                    background: isActive ? 'var(--accent-primary-subtle)' : 'transparent',
                    color: isActive ? '#60a5fa' : 'var(--text-secondary)',
                    fontWeight: isActive ? 600 : 500,
                    fontSize: '0.84rem',
                    cursor: 'pointer',
                    transition: 'var(--transition-fast)',
                    textAlign: 'left'
                  }}
                  onMouseEnter={(e) => {
                    if (!isActive) e.currentTarget.style.backgroundColor = 'var(--bg-tertiary)';
                  }}
                  onMouseLeave={(e) => {
                    if (!isActive) e.currentTarget.style.backgroundColor = 'transparent';
                  }}
                >
                  <Icon size={17} color={isActive ? '#3b82f6' : 'var(--text-muted)'} style={{ flexShrink: 0 }} />
                  {!isCollapsed && (
                    <>
                      <span style={{ flex: 1, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{item.label}</span>
                      {item.badge && (
                        <span style={{
                          fontSize: '0.62rem',
                          padding: '1px 6px',
                          borderRadius: 'var(--radius-full)',
                          background: 'rgba(37, 99, 235, 0.25)',
                          color: '#60a5fa',
                          fontWeight: 700
                        }}>
                          {item.badge}
                        </span>
                      )}
                    </>
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Section: Materials & RAG */}
        <div style={{ marginTop: '16px' }}>
          {!isCollapsed ? (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '4px 8px',
              fontSize: '0.72rem',
              fontWeight: 600,
              textTransform: 'uppercase',
              color: 'var(--text-muted)',
              letterSpacing: '0.5px'
            }}>
              <span>Knowledge</span>
              <ChevronUp size={14} />
            </div>
          ) : (
            <div style={{ height: '1px', background: 'var(--border-subtle)', margin: '8px 6px' }} />
          )}

          <nav style={{ display: 'flex', flexDirection: 'column', gap: '3px', marginTop: '4px' }}>
            {navItems.slice(3).map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  title={item.label}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: isCollapsed ? 'center' : 'flex-start',
                    gap: '10px',
                    width: '100%',
                    padding: isCollapsed ? '10px 0' : '8px 10px',
                    borderRadius: 'var(--radius-md)',
                    border: 'none',
                    background: isActive ? 'var(--accent-primary-subtle)' : 'transparent',
                    color: isActive ? '#60a5fa' : 'var(--text-secondary)',
                    fontWeight: isActive ? 600 : 500,
                    fontSize: '0.84rem',
                    cursor: 'pointer',
                    transition: 'var(--transition-fast)',
                    textAlign: 'left'
                  }}
                  onMouseEnter={(e) => {
                    if (!isActive) e.currentTarget.style.backgroundColor = 'var(--bg-tertiary)';
                  }}
                  onMouseLeave={(e) => {
                    if (!isActive) e.currentTarget.style.backgroundColor = 'transparent';
                  }}
                >
                  <Icon size={17} color={isActive ? '#3b82f6' : 'var(--text-muted)'} style={{ flexShrink: 0 }} />
                  {!isCollapsed && (
                    <span style={{ flex: 1, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{item.label}</span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Bottom Profile Footer matching reference image */}
      <div 
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: isCollapsed ? 'center' : 'flex-start',
          gap: '10px',
          padding: isCollapsed ? '8px 0' : '10px 8px',
          borderRadius: 'var(--radius-md)',
          background: 'var(--bg-secondary)',
          border: '1px solid var(--border-subtle)',
          cursor: 'pointer',
          transition: 'var(--transition-fast)'
        }}
        onClick={() => setActiveTab('settings')}
        title={isCollapsed ? (profile.name || 'Student') : "Open Profile Settings"}
      >
        <div style={{
          width: '32px',
          height: '32px',
          borderRadius: 'var(--radius-full)',
          background: '#1c222b',
          border: '1px solid #28313e',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '0.72rem',
          fontWeight: 700,
          color: 'var(--text-primary)',
          flexShrink: 0
        }}>
          {getInitials(profile.name)}
        </div>
        {!isCollapsed && (
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{
              fontSize: '0.82rem',
              fontWeight: 600,
              color: 'var(--text-primary)',
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis'
            }}>
              {profile.name || 'Student'}
            </div>
            <div style={{
              fontSize: '0.65rem',
              fontWeight: 700,
              color: 'var(--text-muted)',
              letterSpacing: '0.4px'
            }}>
              PLUS CORE
            </div>
          </div>
        )}
      </div>
    </aside>
  );
};
