import React from 'react';
import { StudentProfile } from '../types';
import { 
  BarChart3, 
  AlertTriangle, 
  CheckCircle2, 
  TrendingUp, 
  Target, 
  Sparkles,
  BookOpen,
  ArrowUpRight,
  ShieldAlert
} from 'lucide-react';

interface AnalyticsViewProps {
  profile: StudentProfile;
}

export const AnalyticsView: React.FC<AnalyticsViewProps> = ({ profile }) => {
  const subjectsProgress = [
    { name: 'Data Structures', progress: 85, topicsCompleted: 12, totalTopics: 14, status: 'Strong' },
    { name: 'Database Management', progress: 72, topicsCompleted: 8, totalTopics: 11, status: 'Moderate' },
    { name: 'Algorithms', progress: 60, topicsCompleted: 6, totalTopics: 10, status: 'Needs Review' },
    { name: 'Operating Systems', progress: 45, topicsCompleted: 4, totalTopics: 9, status: 'Needs Review' },
  ];

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
      <div>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '10px' }}>
          <BarChart3 color="var(--accent-primary)" /> Learning Progress & Weak Area Identification
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginTop: '4px' }}>
          Real-time student mastery metrics inferred from quiz evaluation scores, clarification frequency, and tutoring interactions.
        </p>
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
            Active tutoring activity
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
            Arrays, Linked Lists, Traversals
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
      <div className="glass-panel" style={{
        padding: '20px 24px',
        borderRadius: 'var(--radius-lg)',
        background: 'rgba(244, 63, 94, 0.08)',
        border: '1px solid rgba(244, 63, 94, 0.3)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <ShieldAlert size={28} color="var(--accent-rose)" />
          <div>
            <h4 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-primary)' }}>
              Weak Area Alert: BST Deletion & 3NF Normalization
            </h4>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
              EduMate detected high clarification requests and 40% accuracy on deletion questions in recent practice quizzes.
            </p>
          </div>
        </div>
        <button className="btn btn-primary" style={{ background: 'var(--accent-rose)', whiteSpace: 'nowrap' }}>
          Start Focused Revision Session
        </button>
      </div>

      {/* Subject Progress Breakdown & Personalized Recommendations */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px' }}>
        {/* Subject Mastery Progress Bars */}
        <div className="glass-panel" style={{ padding: '24px', borderRadius: 'var(--radius-lg)' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '18px' }}>
            Subject Mastery & Topic Completion
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            {subjectsProgress.map((subject, idx) => (
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
            <div style={{
              padding: '14px',
              borderRadius: 'var(--radius-md)',
              background: 'rgba(99, 102, 241, 0.08)',
              border: '1px solid var(--border-color-glow)'
            }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--accent-primary)', fontWeight: 700, textTransform: 'uppercase' }}>
                Priority 1 (Revision)
              </div>
              <div style={{ fontWeight: 600, fontSize: '0.9rem', marginTop: '4px' }}>
                Revise Binary Search Tree Deletion
              </div>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                Review node replacement with in-order successors before moving to AVL Trees.
              </p>
            </div>

            <div style={{
              padding: '14px',
              borderRadius: 'var(--radius-md)',
              background: 'rgba(16, 185, 129, 0.08)',
              border: '1px solid rgba(16, 185, 129, 0.25)'
            }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--accent-emerald)', fontWeight: 700, textTransform: 'uppercase' }}>
                Priority 2 (Next Topic)
              </div>
              <div style={{ fontWeight: 600, fontSize: '0.9rem', marginTop: '4px' }}>
                Proceed to AVL Tree Rotations
              </div>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                You have achieved 85% mastery in BST fundamentals!
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
