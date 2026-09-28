import React, { useState, useEffect } from 'react';
import { StudentProfile } from '../types';
import { fetchStudentProfile } from '../services/api';
import { 
  BarChart3, 
  AlertTriangle, 
  CheckCircle2, 
  TrendingUp, 
  Target, 
  Sparkles,
  BookOpen,
  ArrowUpRight,
  ShieldAlert,
  Loader2
} from 'lucide-react';

interface AnalyticsViewProps {
  profile: StudentProfile;
}

export const AnalyticsView: React.FC<AnalyticsViewProps> = ({ profile: initialProfile }) => {
  const [profile, setProfile] = useState<StudentProfile>(initialProfile);
  const [subjectProgress, setSubjectProgress] = useState<any[]>([
    { name: 'Data Structures', progress: 85, topicsCompleted: 12, totalTopics: 14, status: 'Strong' },
    { name: 'Database Management', progress: 72, topicsCompleted: 8, totalTopics: 11, status: 'Moderate' },
    { name: 'Algorithms', progress: 60, topicsCompleted: 6, totalTopics: 10, status: 'Needs Review' },
    { name: 'Operating Systems', progress: 45, topicsCompleted: 4, totalTopics: 9, status: 'Needs Review' },
  ]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    setIsLoading(true);
    try {
      const data = await fetchStudentProfile();
      setProfile(data);
      if (data.subjectProgress && data.subjectProgress.length > 0) {
        setSubjectProgress(data.subjectProgress);
      }
    } catch (err) {
      console.error('Failed to load profile analytics:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{
      padding: '32px',
      height: 'calc(100vh - 70px)',
      overflowY: 'auto',
      display: 'flex',
      flexDirection: 'column',
      gap: '28px',
      background: 'var(--bg-primary)'
    }}>
      {/* Analytics Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '10px' }}>
            <BarChart3 color="var(--accent-primary)" /> Learning Progress & Weak Area Identification
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginTop: '4px' }}>
            Real-time student mastery metrics inferred dynamically from quiz evaluation scores, mistakes, and study material interactions.
          </p>
        </div>
        {isLoading && <Loader2 size={20} className="spin-slow" color="var(--accent-cyan)" />}
      </div>

      {/* Top Overview Metric Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px' }}>
        <div className="glass-panel" style={{ padding: '20px', borderRadius: 'var(--radius-lg)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: 'var(--text-muted)' }}>
            <span style={{ fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: 600 }}>Overall Mastery</span>
            <TrendingUp size={18} color="var(--accent-emerald)" />
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--text-primary)', marginTop: '8px' }}>
            {profile.masteryScore}%
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--accent-emerald)', marginTop: '4px' }}>
            +5% increase this week
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '20px', borderRadius: 'var(--radius-lg)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: 'var(--text-muted)' }}>
            <span style={{ fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: 600 }}>Study Streak</span>
            <Target size={18} color="var(--accent-amber)" />
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--text-primary)', marginTop: '8px' }}>
            {profile.studyStreakDays} Days
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Active tutoring streak
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '20px', borderRadius: 'var(--radius-lg)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: 'var(--text-muted)' }}>
            <span style={{ fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: 600 }}>Strong Topics</span>
            <CheckCircle2 size={18} color="var(--accent-emerald)" />
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--accent-emerald)', marginTop: '8px' }}>
            {profile.strongAreas.length}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
            {profile.strongAreas.slice(0, 2).join(', ')}
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '20px', borderRadius: 'var(--radius-lg)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: 'var(--text-muted)' }}>
            <span style={{ fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: 600 }}>Identified Weak Areas</span>
            <AlertTriangle size={18} color="var(--accent-rose)" />
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--accent-rose)', marginTop: '8px' }}>
            {profile.weakAreas.length}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Requires targeted practice
          </div>
        </div>
      </div>

      {/* Weak Area Identification Alert Banner */}
      {profile.weakAreas.length > 0 && (
        <div className="glass-panel" style={{
          padding: '20px 24px',
          borderRadius: 'var(--radius-lg)',
          background: 'rgba(244, 63, 94, 0.08)',
          border: '1px solid rgba(244, 63, 94, 0.3)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '16px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <ShieldAlert size={28} color="var(--accent-rose)" />
            <div>
              <h4 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                Weak Areas Tracked: {profile.weakAreas.join(' • ')}
              </h4>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                EduMate identified persistent errors during quiz questions on these topics. Targeted revision sessions are recommended.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Subject Progress Breakdown & Personalized Recommendations */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px' }}>
        {/* Subject Mastery Progress Bars */}
        <div className="glass-panel" style={{ padding: '24px', borderRadius: 'var(--radius-lg)' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '18px' }}>
            Subject Mastery & Topic Completion
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            {subjectProgress.map((subject, idx) => (
              <div key={idx} style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem' }}>
                  <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{subject.name}</span>
                  <span style={{ color: 'var(--text-muted)' }}>
                    {subject.topicsCompleted}/{subject.totalTopics} Topics ({subject.progress}%)
                  </span>
                </div>
                <div style={{
                  height: '8px',
                  background: 'var(--bg-tertiary)',
                  borderRadius: 'var(--radius-full)',
                  overflow: 'hidden'
                }}>
                  <div style={{
                    height: '100%',
                    width: `${subject.progress}%`,
                    background: subject.progress > 75 
                      ? 'var(--accent-emerald)' 
                      : subject.progress > 50 
                        ? 'var(--accent-gradient)' 
                        : 'var(--accent-rose)',
                    borderRadius: 'var(--radius-full)',
                    transition: 'var(--transition-smooth)'
                  }} />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* AI Recommendations Panel */}
        <div className="glass-panel" style={{ padding: '24px', borderRadius: 'var(--radius-lg)' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Sparkles size={18} color="var(--accent-cyan)" /> AI Next Recommendations
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {profile.weakAreas.length > 0 && (
              <div style={{
                padding: '14px',
                borderRadius: 'var(--radius-md)',
                background: 'rgba(244, 63, 94, 0.08)',
                border: '1px solid rgba(244, 63, 94, 0.25)'
              }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--accent-rose)', fontWeight: 700, textTransform: 'uppercase' }}>
                  Priority 1 (Targeted Revision)
                </div>
                <div style={{ fontWeight: 600, fontSize: '0.9rem', marginTop: '4px' }}>
                  Practice {profile.weakAreas[0]}
                </div>
                <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                  Focus on underlying invariant properties before proceeding to complex topics.
                </p>
              </div>
            )}

            <div style={{
              padding: '14px',
              borderRadius: 'var(--radius-md)',
              background: 'rgba(16, 185, 129, 0.08)',
              border: '1px solid rgba(16, 185, 129, 0.25)'
            }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--accent-emerald)', fontWeight: 700, textTransform: 'uppercase' }}>
                Priority 2 (Next Advance Topic)
              </div>
              <div style={{ fontWeight: 600, fontSize: '0.9rem', marginTop: '4px' }}>
                Proceed to {profile.currentTopic}
              </div>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                You have maintained a {profile.studyStreakDays}-day streak with {profile.masteryScore}% mastery!
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
