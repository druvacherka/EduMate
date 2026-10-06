import React, { useState, useEffect } from 'react';
import { StudentProfile } from '../types';
import { fetchStudentProfile } from '../services/api';
import { 
  CheckCircle2, 
  Circle,
  ArrowRight,
  Code2,
  Clock,
  Calendar,
  BarChart2,
  AlertTriangle,
  Loader2,
  Sparkles
} from 'lucide-react';

interface AnalyticsViewProps {
  profile: StudentProfile;
}

export const AnalyticsView: React.FC<AnalyticsViewProps> = ({ profile: initialProfile }) => {
  const [profile, setProfile] = useState<StudentProfile>(initialProfile);
  const [subjectProgress, setSubjectProgress] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    setIsLoading(true);
    try {
      const data = await fetchStudentProfile();
      setProfile(data);
      if (data.subjectProgress) {
        setSubjectProgress(data.subjectProgress);
      }
    } catch (err) {
      console.error('Failed to load profile analytics:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  return (
    <div style={{
      padding: '28px 36px',
      height: 'calc(100vh - 56px)',
      overflowY: 'auto',
      display: 'flex',
      flexDirection: 'column',
      gap: '24px',
      backgroundColor: 'var(--bg-primary)',
      color: 'var(--text-primary)'
    }}>
      {/* Hero Greeting matching reference screenshot */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <h1 style={{ fontSize: '1.45rem', fontWeight: 700, color: 'var(--text-primary)', letterSpacing: '-0.3px' }}>
            {getGreeting()}, {profile.name || 'Learner'} 👋
          </h1>
          {isLoading && <Loader2 size={18} className="spin-slow" color="#3b82f6" />}
        </div>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.86rem', marginTop: '4px' }}>
          The day gets heavy around now. Good to see you still going.
        </p>
      </div>

      {/* Weak Areas Alert Banner if any mistakes logged */}
      {profile.weakAreas.length > 0 && (
        <div style={{
          padding: '14px 18px',
          borderRadius: 'var(--radius-lg)',
          background: 'rgba(239, 68, 68, 0.08)',
          border: '1px solid rgba(239, 68, 68, 0.25)',
          display: 'flex',
          alignItems: 'center',
          gap: '12px'
        }}>
          <AlertTriangle size={20} color="var(--accent-rose)" />
          <div>
            <div style={{ fontWeight: 600, fontSize: '0.88rem', color: 'var(--accent-rose)' }}>
              Weak Areas Requiring Revision ({profile.weakAreas.length})
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
              Identified topics: <strong>{profile.weakAreas.join(' • ')}</strong>
            </div>
          </div>
        </div>
      )}

      {/* Card 1: Today's Plan (matching reference screenshot layout) */}
      <div className="glass-panel" style={{
        padding: '24px',
        borderRadius: 'var(--radius-xl)',
        backgroundColor: 'var(--bg-secondary)',
        border: '1px solid var(--border-color)',
        display: 'flex',
        flexDirection: 'column',
        gap: '20px'
      }}>
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <h2 style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--text-primary)' }}>
            Today's Plan
          </h2>
          <span style={{
            fontSize: '0.82rem',
            color: '#3b82f6',
            fontWeight: 500,
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            cursor: 'pointer'
          }}>
            Planly Dashboard <ArrowRight size={14} />
          </span>
        </div>

        {/* 2-Column Split matching reference screenshot */}
        <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr', gap: '36px' }}>
          {/* Left Column: Tasks */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.78rem' }}>
              <div style={{
                background: 'var(--bg-tertiary)',
                padding: '3px 8px',
                borderRadius: 'var(--radius-sm)',
                color: 'var(--text-secondary)',
                fontWeight: 600
              }}>
                Tasks {profile.currentTopic ? '1 / 2' : '0 / 0'}
              </div>
              <span style={{ color: '#3b82f6', fontWeight: 500, cursor: 'pointer' }}>
                View all ({profile.currentTopic ? '2' : '0'}) &gt;
              </span>
            </div>

            {profile.currentTopic ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.85rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <CheckCircle2 size={16} color="#64748b" />
                    <span style={{ color: 'var(--text-primary)' }}>{profile.currentTopic} Concept Review</span>
                  </div>
                  <span style={{ color: 'var(--text-muted)', fontSize: '0.78rem' }}>15 min</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.85rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <Circle size={16} color="#64748b" />
                    <span style={{ color: 'var(--text-primary)' }}>Attempt Practice Quiz on {profile.currentTopic}</span>
                  </div>
                  <span style={{ color: 'var(--text-muted)', fontSize: '0.78rem' }}>20 min</span>
                </div>
              </div>
            ) : (
              <div style={{
                padding: '24px 16px',
                textAlign: 'center',
                color: 'var(--text-muted)',
                fontSize: '0.84rem',
                border: '1px dashed var(--border-color)',
                borderRadius: 'var(--radius-md)',
                background: 'rgba(255, 255, 255, 0.01)'
              }}>
                No tasks scheduled yet. Select an active topic in the top bar to initialize today's learning plan.
              </div>
            )}
          </div>

          {/* Right Column: Progress Metrics matching reference screenshot */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Progress
            </div>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.84rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-secondary)' }}>
                <Code2 size={15} color="var(--text-muted)" />
                <span>Strong Topics</span>
              </div>
              <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                {profile.strongAreas.length} <span style={{ color: 'var(--text-muted)', fontWeight: 400 }}>/ {Math.max(profile.strongAreas.length + profile.weakAreas.length, 1)}</span>
              </span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.84rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-secondary)' }}>
                <Clock size={15} color="var(--text-muted)" />
                <span>Time spent</span>
              </div>
              <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                {profile.studyStreakDays > 0 ? `${profile.studyStreakDays * 25} min` : '0 min'}
              </span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.84rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-secondary)' }}>
                <Calendar size={15} color="var(--text-muted)" />
                <span>Last active</span>
              </div>
              <span style={{ color: 'var(--text-secondary)' }}>
                {profile.studyStreakDays > 0 ? 'Today' : 'Never'}
              </span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.84rem', marginTop: '4px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-secondary)' }}>
                <BarChart2 size={15} color="var(--text-muted)" />
                <span>Mastery</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', width: '130px' }}>
                <div style={{
                  flex: 1,
                  height: '5px',
                  background: 'var(--bg-tertiary)',
                  borderRadius: 'var(--radius-full)',
                  overflow: 'hidden'
                }}>
                  <div style={{
                    height: '100%',
                    width: `${profile.masteryScore}%`,
                    background: '#2563eb',
                    borderRadius: 'var(--radius-full)'
                  }} />
                </div>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', minWidth: '32px', textAlign: 'right' }}>
                  {profile.masteryScore}%
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Section 2: Continue where you left off -> (matching reference screenshot) */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '14px' }}>
          <h2 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-primary)' }}>
            Continue where you left off
          </h2>
          <span style={{ color: 'var(--text-muted)' }}>&gt;</span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '18px' }}>
          {/* Module Card 1: Subject */}
          <div className="glass-panel" style={{
            padding: '18px 20px',
            borderRadius: 'var(--radius-xl)',
            backgroundColor: 'var(--bg-secondary)',
            border: '1px solid var(--border-color)',
            display: 'flex',
            flexDirection: 'column',
            gap: '14px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: 'var(--radius-md)',
                  background: 'var(--bg-tertiary)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#3b82f6'
                }}>
                  <Code2 size={16} />
                </div>
                <span style={{ fontWeight: 600, fontSize: '0.92rem', color: 'var(--text-primary)' }}>
                  {profile.currentSubject || 'No subject selected'}
                </span>
              </div>

              <button
                className="btn btn-primary"
                style={{
                  padding: '6px 14px',
                  fontSize: '0.78rem',
                  borderRadius: 'var(--radius-md)',
                  background: '#1d4ed8'
                }}
              >
                <span>Resume</span>
                <ArrowRight size={13} />
              </button>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div style={{
                flex: 1,
                height: '4px',
                background: 'var(--bg-tertiary)',
                borderRadius: 'var(--radius-full)',
                overflow: 'hidden'
              }}>
                <div style={{
                  height: '100%',
                  width: `${profile.masteryScore}%`,
                  background: '#2563eb',
                  borderRadius: 'var(--radius-full)'
                }} />
              </div>
              <span style={{ fontSize: '0.76rem', color: 'var(--text-muted)' }}>
                {profile.masteryScore}%
              </span>
            </div>
          </div>

          {/* Module Card 2: Topic */}
          <div className="glass-panel" style={{
            padding: '18px 20px',
            borderRadius: 'var(--radius-xl)',
            backgroundColor: 'var(--bg-secondary)',
            border: '1px solid var(--border-color)',
            display: 'flex',
            flexDirection: 'column',
            gap: '14px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: 'var(--radius-md)',
                  background: 'var(--bg-tertiary)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#3b82f6'
                }}>
                  <Code2 size={16} />
                </div>
                <span style={{ fontWeight: 600, fontSize: '0.92rem', color: 'var(--text-primary)' }}>
                  {profile.currentTopic || 'Practice Problems'}
                </span>
              </div>

              <button
                className="btn btn-primary"
                style={{
                  padding: '6px 14px',
                  fontSize: '0.78rem',
                  borderRadius: 'var(--radius-md)',
                  background: '#1d4ed8'
                }}
              >
                <span>Resume</span>
                <ArrowRight size={13} />
              </button>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div style={{
                flex: 1,
                height: '4px',
                background: 'var(--bg-tertiary)',
                borderRadius: 'var(--radius-full)',
                overflow: 'hidden'
              }}>
                <div style={{
                  height: '100%',
                  width: `${profile.masteryScore}%`,
                  background: '#2563eb',
                  borderRadius: 'var(--radius-full)'
                }} />
              </div>
              <span style={{ fontSize: '0.76rem', color: 'var(--text-muted)' }}>
                {profile.masteryScore}%
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Section 3: Your Progress matching reference screenshot */}
      <div>
        <h2 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '14px' }}>
          Your Progress
        </h2>

        <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1.8fr', gap: '18px' }}>
          {/* Donut/Progress Summary Card */}
          <div className="glass-panel" style={{
            padding: '24px',
            borderRadius: 'var(--radius-xl)',
            backgroundColor: 'var(--bg-secondary)',
            border: '1px solid var(--border-color)',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            gap: '20px'
          }}>
            <div style={{ fontSize: '0.84rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
              Overall Learning Mastery
            </div>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '16px 0' }}>
              <div style={{
                position: 'relative',
                width: '120px',
                height: '120px',
                borderRadius: 'var(--radius-full)',
                border: '6px solid var(--bg-tertiary)',
                borderTopColor: '#2563eb',
                borderRightColor: profile.masteryScore > 50 ? '#2563eb' : 'var(--bg-tertiary)',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <span style={{ fontSize: '1.6rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                  {profile.masteryScore}%
                </span>
                <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Mastery</span>
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-around', borderTop: '1px solid var(--border-subtle)', paddingTop: '14px' }}>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Strong Areas</div>
                <div style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--accent-emerald)', marginTop: '2px' }}>
                  {profile.strongAreas.length}
                </div>
              </div>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Weak Topics</div>
                <div style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--accent-rose)', marginTop: '2px' }}>
                  {profile.weakAreas.length}
                </div>
              </div>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Streak</div>
                <div style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--accent-amber)', marginTop: '2px' }}>
                  {profile.studyStreakDays}d
                </div>
              </div>
            </div>
          </div>

          {/* Category-wise Progress Card */}
          <div className="glass-panel" style={{
            padding: '24px',
            borderRadius: 'var(--radius-xl)',
            backgroundColor: 'var(--bg-secondary)',
            border: '1px solid var(--border-color)',
            display: 'flex',
            flexDirection: 'column',
            gap: '16px'
          }}>
            <div style={{ fontSize: '0.84rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
              Category-wise Progress
            </div>

            {subjectProgress.length === 0 ? (
              <div style={{
                flex: 1,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                textAlign: 'center',
                color: 'var(--text-muted)',
                fontSize: '0.84rem',
                padding: '30px 16px',
                border: '1px dashed var(--border-color)',
                borderRadius: 'var(--radius-md)',
                background: 'rgba(255, 255, 255, 0.01)'
              }}>
                No category metrics recorded yet. Complete quizzes to track topic mastery.
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                {subjectProgress.map((sub, idx) => (
                  <div key={idx} style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '10px 12px',
                    borderRadius: 'var(--radius-md)',
                    background: 'var(--bg-tertiary)'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <Code2 size={16} color="#3b82f6" />
                      <div>
                        <div style={{ fontWeight: 600, fontSize: '0.85rem', color: 'var(--text-primary)' }}>
                          {sub.name}
                        </div>
                        <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                          {sub.topicsCompleted}/{sub.totalTopics} Topics
                        </div>
                      </div>
                    </div>
                    <span style={{ fontWeight: 600, fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                      {sub.progress}%
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
