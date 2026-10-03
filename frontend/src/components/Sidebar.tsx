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
  ListTodo,
  Target,
  RotateCcw,
  BarChart3,
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
  onToggleCollapse,
}) => {
  const getInitials = (name: string) => {
    if (!name || name === 'Student') return 'EM';
    const parts = name.trim().split(/\s+/);
    if (parts.length >= 2) return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
    return name.slice(0, 2).toUpperCase();
  };

  const learningItems = [
    { id: 'dashboard' as ActiveTab, label: "Today's Hub", icon: LayoutDashboard },
    { id: 'curriculum' as ActiveTab, label: 'Curriculum & Learn', icon: BookOpen },
    { id: 'tutor' as ActiveTab, label: 'AI Socratic Tutor', icon: MessageSquare, badge: 'Live' },
    { id: 'quizzes' as ActiveTab, label: 'Adaptive Quizzes', icon: Code2 },
    { id: 'materials' as ActiveTab, label: 'Study Material (RAG)', icon: FileText },
  ];

  const planningItems = [
    { id: 'planner' as ActiveTab, label: 'Adaptive Planner', icon: ListTodo },
    { id: 'revision' as ActiveTab, label: 'Spaced Revision', icon: RotateCcw },
    { id: 'goals' as ActiveTab, label: 'Targets & Goals', icon: Target },
    { id: 'career' as ActiveTab, label: 'Career Explorer', icon: Compass },
  ];

  const insightItems = [
    { id: 'analytics' as ActiveTab, label: 'Mastery Analytics', icon: BarChart3 },
    { id: 'settings' as ActiveTab, label: 'Profile & Settings', icon: Settings },
  ];

  const renderNavGroup = (title: string, items: typeof learningItems) => (
    <div style={{ marginTop: '14px' }}>
      {!isCollapsed ? (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '4px 8px',
            fontSize: '0.68rem',
            fontWeight: 700,
            textTransform: 'uppercase',
            color: 'var(--text-muted)',
            letterSpacing: '0.6px',
          }}
        >
          <span>{title}</span>
        </div>
      ) : (
        <div style={{ height: '1px', background: 'var(--border-subtle)', margin: '6px 6px' }} />
      )}

      <nav style={{ display: 'flex', flexDirection: 'column', gap: '2px', marginTop: '4px' }}>
        {items.map((item) => {
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
                padding: isCollapsed ? '9px 0' : '7px 10px',
                borderRadius: 'var(--radius-md)',
                border: 'none',
                background: isActive ? 'var(--accent-primary-subtle)' : 'transparent',
                color: isActive ? '#60a5fa' : 'var(--text-secondary)',
                fontWeight: isActive ? 600 : 500,
                fontSize: '0.82rem',
                cursor: 'pointer',
                transition: 'var(--transition-fast)',
                textAlign: 'left',
              }}
              onMouseEnter={(e) => {
                if (!isActive) e.currentTarget.style.backgroundColor = 'var(--bg-tertiary)';
              }}
              onMouseLeave={(e) => {
                if (!isActive) e.currentTarget.style.backgroundColor = 'transparent';
              }}
            >
              <Icon size={16} color={isActive ? '#3b82f6' : 'var(--text-muted)'} style={{ flexShrink: 0 }} />
              {!isCollapsed && (
                <>
                  <span style={{ flex: 1, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {item.label}
                  </span>
                  {item.badge && (
                    <span
                      style={{
                        fontSize: '0.6rem',
                        padding: '1px 5px',
                        borderRadius: 'var(--radius-full)',
                        background: 'rgba(37, 99, 235, 0.25)',
                        color: '#60a5fa',
                        fontWeight: 700,
                      }}
                    >
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
  );

  return (
    <aside
      style={{
        width: isCollapsed ? '64px' : '230px',
        minWidth: isCollapsed ? '64px' : '230px',
        height: '100%',
        backgroundColor: 'var(--bg-sidebar)',
        borderRight: '1px solid var(--border-color)',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        padding: isCollapsed ? '14px 6px' : '14px 10px',
        zIndex: 10,
        userSelect: 'none',
        transition:
          'width 0.25s cubic-bezier(0.4, 0, 0.2, 1), min-width 0.25s cubic-bezier(0.4, 0, 0.2, 1), padding 0.2s ease',
        overflowY: 'auto',
        overflowX: 'hidden',
      }}
    >
      <div>
        {/* Brand Header */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: isCollapsed ? 'center' : 'space-between',
            padding: isCollapsed ? '4px 0 12px 0' : '4px 6px 14px 6px',
            borderBottom: '1px solid var(--border-subtle)',
            minHeight: '40px',
          }}
        >
          {!isCollapsed && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div
                style={{
                  width: '26px',
                  height: '26px',
                  borderRadius: '6px',
                  background: 'var(--accent-primary)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#ffffff',
                  flexShrink: 0,
                }}
              >
                <GraduationCap size={15} />
              </div>
              <span
                style={{
                  fontSize: '0.95rem',
                  fontWeight: 700,
                  color: 'var(--text-primary)',
                  letterSpacing: '-0.3px',
                  whiteSpace: 'nowrap',
                }}
              >
                Edu<span style={{ color: '#60a5fa' }}>Mate</span>
              </span>
            </div>
          )}
          <button
            onClick={onToggleCollapse}
            className="btn btn-ghost"
            style={{
              padding: '5px',
              color: 'var(--text-muted)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              borderRadius: '6px',
              cursor: 'pointer',
              border: 'none',
              background: 'transparent',
            }}
            title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {isCollapsed ? <PanelLeftOpen size={17} color="#60a5fa" /> : <PanelLeftClose size={15} />}
          </button>
        </div>

        {/* Navigation Sections */}
        {renderNavGroup('Learn', learningItems)}
        {renderNavGroup('Plan & Review', planningItems)}
        {renderNavGroup('Insights', insightItems)}
      </div>

      {/* User Mini Profile in Sidebar Footer */}
      {!isCollapsed ? (
        <div
          style={{
            padding: '10px 10px',
            marginTop: '16px',
            borderRadius: 'var(--radius-md)',
            background: 'var(--bg-tertiary)',
            border: '1px solid var(--border-subtle)',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
          }}
        >
          <div
            style={{
              width: '28px',
              height: '28px',
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #3b82f6, #10b981)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '0.75rem',
              fontWeight: 700,
              color: '#ffffff',
              flexShrink: 0,
            }}
          >
            {getInitials(profile.name)}
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div
              style={{
                fontSize: '0.82rem',
                fontWeight: 600,
                color: 'var(--text-primary)',
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
              }}
            >
              {profile.name || 'Student'}
            </div>
            <div
              style={{
                fontSize: '0.7rem',
                color: '#60a5fa',
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
              }}
            >
              {profile.educationLevel || 'Universal Learner'}
            </div>
          </div>
        </div>
      ) : (
        <div
          style={{
            display: 'flex',
            justifyContent: 'center',
            padding: '10px 0',
          }}
        >
          <div
            style={{
              width: '26px',
              height: '26px',
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #3b82f6, #10b981)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '0.7rem',
              fontWeight: 700,
              color: '#ffffff',
            }}
          >
            {getInitials(profile.name)}
          </div>
        </div>
      )}
    </aside>
  );
};
