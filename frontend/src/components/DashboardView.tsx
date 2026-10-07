import React, { useState, useEffect } from 'react';
import {
  Calendar,
  CheckCircle2,
  Circle,
  Clock,
  Flame,
  Lightbulb,
  ArrowRight,
  Target,
  Sparkles,
  BookOpen,
  Award,
  AlertTriangle,
  RotateCw,
} from 'lucide-react';
import { DailyDashboardData, DailyStudyTask, StudentGoal } from '../types';
import { fetchDailyDashboard, toggleDailyTask, fetchStudentGoals, selectStudentGoal } from '../services/api';

interface DashboardViewProps {
  onNavigateToTab: (tab: any, topicContext?: string) => void;
  onOpenOnboarding: () => void;
}

export const DashboardView: React.FC<DashboardViewProps> = ({ onNavigateToTab, onOpenOnboarding }) => {
  const [dashboard, setDashboard] = useState<DailyDashboardData | null>(null);
  const [allGoals, setAllGoals] = useState<StudentGoal[]>([]);
  const [loading, setLoading] = useState(true);
  const [switchingGoalId, setSwitchingGoalId] = useState<string | null>(null);
  const [togglingTaskId, setTogglingTaskId] = useState<string | null>(null);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    setLoading(true);
    const [dashData, goalsData] = await Promise.all([
      fetchDailyDashboard(),
      fetchStudentGoals(),
    ]);
    setDashboard(dashData);
    setAllGoals(goalsData);
    setLoading(false);
  };

  const handleSwitchGoal = async (goalId: string) => {
    setSwitchingGoalId(goalId);
    await selectStudentGoal(goalId);
    const [dashData, goalsData] = await Promise.all([
      fetchDailyDashboard(),
      fetchStudentGoals(),
    ]);
    setDashboard(dashData);
    setAllGoals(goalsData);
    setSwitchingGoalId(null);
  };

  const handleToggleTask = async (task: DailyStudyTask) => {
    setTogglingTaskId(task.id);
    const updated = await toggleDailyTask(task.id);
    if (updated && dashboard) {
      setDashboard({
        ...dashboard,
        today_tasks: dashboard.today_tasks.map((t) => (t.id === task.id ? updated : t)),
        completed_tasks_count: updated.is_completed
          ? dashboard.completed_tasks_count + 1
          : Math.max(0, dashboard.completed_tasks_count - 1),
        study_streak_days: updated.is_completed
          ? dashboard.study_streak_days + 1
          : dashboard.study_streak_days,
      });
    }
    setTogglingTaskId(null);
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '60vh', color: '#94a3b8' }}>
        <RotateCw className="animate-spin" size={32} style={{ marginRight: 12 }} />
        <span>Loading your personalized daily study plan...</span>
      </div>
    );
  }

  if (!dashboard) {
    return (
      <div style={{ padding: 32, textAlign: 'center', color: '#94a3b8' }}>
        <p>Could not load daily dashboard. Please ensure backend is running.</p>
        <button className="btn-primary" onClick={loadDashboard} style={{ marginTop: 16 }}>
          Retry
        </button>
      </div>
    );
  }

  const completionPct =
    dashboard.total_tasks_count > 0
      ? Math.round((dashboard.completed_tasks_count / dashboard.total_tasks_count) * 100)
      : 0;

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', paddingBottom: 40 }}>
      {/* Hero Welcome Banner */}
      <div
        style={{
          background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%)',
          borderRadius: 20,
          padding: '28px 32px',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.25)',
          marginBottom: 28,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: 20,
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
            <span
              style={{
                background: 'rgba(56, 189, 248, 0.15)',
                color: '#38bdf8',
                padding: '4px 12px',
                borderRadius: 20,
                fontSize: '0.8rem',
                fontWeight: 600,
                border: '1px solid rgba(56, 189, 248, 0.3)',
              }}
            >
              {dashboard.education_level}
            </span>
            <span style={{ color: '#94a3b8', fontSize: '0.85rem' }}>• {dashboard.stream_branch}</span>
          </div>
          <h1 style={{ fontSize: '1.9rem', fontWeight: 700, color: '#f8fafc', margin: '0 0 6px 0' }}>
            {dashboard.greeting}
          </h1>
          <p style={{ color: '#94a3b8', margin: 0, fontSize: '0.95rem' }}>
            Today you have{' '}
            <strong style={{ color: '#38bdf8' }}>{dashboard.available_hours_today} hours</strong> allocated. You
            have completed{' '}
            <strong style={{ color: '#10b981' }}>
              {dashboard.completed_tasks_count} of {dashboard.total_tasks_count}
            </strong>{' '}
            scheduled tasks.
          </p>
        </div>

        {/* Quick Stats Badges */}
        <div style={{ display: 'flex', gap: 14 }}>
          <div
            style={{
              background: 'rgba(234, 88, 12, 0.12)',
              border: '1px solid rgba(234, 88, 12, 0.3)',
              borderRadius: 14,
              padding: '12px 18px',
              textAlign: 'center',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: '#f97316', fontWeight: 600, fontSize: '0.8rem' }}>
              <Flame size={16} /> STREAK
            </div>
            <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#fdba74', marginTop: 2 }}>
              {dashboard.study_streak_days} days
            </div>
          </div>

          <div
            style={{
              background: 'rgba(16, 185, 129, 0.12)',
              border: '1px solid rgba(16, 185, 129, 0.3)',
              borderRadius: 14,
              padding: '12px 18px',
              textAlign: 'center',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: '#10b981', fontWeight: 600, fontSize: '0.8rem' }}>
              <Award size={16} /> MASTERY
            </div>
            <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#6ee7b7', marginTop: 2 }}>
              {Math.round(dashboard.overall_mastery)}%
            </div>
          </div>
        </div>
      </div>

      {/* Single Active Goal Spotlight & Target Switcher */}
      <div style={{ marginBottom: 28 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 10, marginBottom: 12 }}>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#e2e8f0', margin: 0, display: 'flex', alignItems: 'center', gap: 8 }}>
            <Target size={18} color="#38bdf8" /> Active Target Goal
          </h3>

          {/* Quick Target Switcher Pills */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
            <span style={{ fontSize: '0.78rem', color: '#64748b', fontWeight: 600, textTransform: 'uppercase' }}>
              Switch Goal:
            </span>
            {allGoals.map((g) => {
              const isCurrent = dashboard.active_goals.some((ag) => ag.id === g.id) || g.is_active;
              return (
                <button
                  key={g.id}
                  onClick={() => !isCurrent && handleSwitchGoal(g.id)}
                  disabled={switchingGoalId === g.id}
                  style={{
                    background: isCurrent ? 'rgba(56, 189, 248, 0.2)' : 'rgba(15, 23, 42, 0.6)',
                    border: isCurrent ? '1px solid rgba(56, 189, 248, 0.5)' : '1px solid rgba(255, 255, 255, 0.08)',
                    color: isCurrent ? '#38bdf8' : '#94a3b8',
                    padding: '4px 10px',
                    borderRadius: 20,
                    fontSize: '0.78rem',
                    fontWeight: isCurrent ? 700 : 500,
                    cursor: isCurrent ? 'default' : 'pointer',
                    transition: 'all 0.15s ease',
                  }}
                >
                  {g.name.split('(')[0].trim()}
                </button>
              );
            })}
          </div>
        </div>

        {/* Selected Goal Banner */}
        {dashboard.active_goals.length > 0 && (
          <div
            style={{
              background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.8) 100%)',
              borderRadius: 16,
              padding: '18px 24px',
              border: '1px solid rgba(56, 189, 248, 0.25)',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              flexWrap: 'wrap',
              gap: 16,
            }}
          >
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4 }}>
                <span
                  style={{
                    fontSize: '0.72rem',
                    textTransform: 'uppercase',
                    fontWeight: 700,
                    letterSpacing: '0.05em',
                    padding: '2px 8px',
                    borderRadius: 6,
                    background: 'rgba(56, 189, 248, 0.15)',
                    color: '#38bdf8',
                  }}
                >
                  ★ ACTIVE PRIMARY FOCUS
                </span>
                {dashboard.active_goals[0].target_exam && (
                  <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
                    Target: {dashboard.active_goals[0].target_exam}
                  </span>
                )}
              </div>
              <h4 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#f8fafc', margin: '0 0 4px 0' }}>
                {dashboard.active_goals[0].name}
              </h4>
              <p style={{ fontSize: '0.82rem', color: '#94a3b8', margin: 0 }}>
                Daily study commitment: <strong style={{ color: '#38bdf8' }}>{dashboard.active_goals[0].available_hours_per_day} hours</strong>
                {dashboard.active_goals[0].target_date && ` • Target Date: ${dashboard.active_goals[0].target_date}`}
              </p>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <button
                onClick={() => onNavigateToTab('tutor', dashboard.active_goals[0].name)}
                style={{
                  background: 'rgba(56, 189, 248, 0.15)',
                  border: '1px solid rgba(56, 189, 248, 0.3)',
                  color: '#38bdf8',
                  borderRadius: 10,
                  padding: '8px 14px',
                  fontSize: '0.85rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 6,
                }}
              >
                <Sparkles size={14} />
                <span>Ask Socratic Tutor</span>
              </button>
              <button
                onClick={() => onNavigateToTab('goals')}
                style={{
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  color: '#e2e8f0',
                  borderRadius: 10,
                  padding: '8px 14px',
                  fontSize: '0.85rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 6,
                }}
              >
                <span>View Goal Details</span>
                <ArrowRight size={14} />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Main Grid: Today's Tasks + Recommendation/Weak Areas */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 24, alignItems: 'start' }}>
        {/* Left Column: Today's Action Tasks */}
        <div
          style={{
            background: 'rgba(30, 41, 59, 0.4)',
            borderRadius: 18,
            padding: 24,
            border: '1px solid rgba(255, 255, 255, 0.06)',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <div>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 600, color: '#f8fafc', margin: 0 }}>Today's Learning Tasks</h3>
              <p style={{ fontSize: '0.85rem', color: '#94a3b8', margin: '4px 0 0 0' }}>
                {dashboard.total_tasks_count > 0 ? (
                  <>Est. time remaining: <strong>{dashboard.estimated_time_remaining_minutes} min</strong></>
                ) : (
                  'No study tasks scheduled for today.'
                )}
              </p>
            </div>
            {dashboard.total_tasks_count > 0 && (
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <div
                  style={{
                    width: 120,
                    height: 8,
                    background: 'rgba(255, 255, 255, 0.1)',
                    borderRadius: 4,
                    overflow: 'hidden',
                  }}
                >
                  <div
                    style={{
                      width: `${completionPct}%`,
                      height: '100%',
                      background: 'linear-gradient(90deg, #38bdf8, #10b981)',
                      transition: 'width 0.4s ease',
                    }}
                  />
                </div>
                <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#10b981' }}>{completionPct}%</span>
              </div>
            )}
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {dashboard.today_tasks.length === 0 ? (
              <p style={{ color: '#94a3b8', fontSize: '0.85rem', margin: 0 }}>
                Your scheduled tasks will appear here once you have a study plan.
              </p>
            ) : dashboard.today_tasks.map((task) => {
              const isBusy = togglingTaskId === task.id;
              return (
                <div
                  key={task.id}
                  style={{
                    background: task.is_completed ? 'rgba(16, 185, 129, 0.06)' : 'rgba(15, 23, 42, 0.6)',
                    border: task.is_completed
                      ? '1px solid rgba(16, 185, 129, 0.25)'
                      : '1px solid rgba(255, 255, 255, 0.05)',
                    borderRadius: 14,
                    padding: '14px 18px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 14,
                    transition: 'all 0.2s',
                  }}
                >
                  <button
                    onClick={() => handleToggleTask(task)}
                    disabled={isBusy}
                    style={{
                      background: 'none',
                      border: 'none',
                      cursor: 'pointer',
                      padding: 0,
                      color: task.is_completed ? '#10b981' : '#64748b',
                      display: 'flex',
                      alignItems: 'center',
                    }}
                  >
                    {task.is_completed ? (
                      <CheckCircle2 size={22} color="#10b981" />
                    ) : (
                      <Circle size={22} color="#64748b" />
                    )}
                  </button>

                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 2 }}>
                      <span
                        style={{
                          fontSize: '0.7rem',
                          fontWeight: 700,
                          textTransform: 'uppercase',
                          color:
                            task.task_type === 'REVISE'
                              ? '#f59e0b'
                              : task.task_type === 'QUIZ'
                              ? '#a855f7'
                              : task.task_type === 'REVIEW_MISTAKES'
                              ? '#ef4444'
                              : '#38bdf8',
                        }}
                      >
                        {task.task_type.replace('_', ' ')}
                      </span>
                      <span style={{ color: '#475569', fontSize: '0.75rem' }}>• {task.subject}</span>
                    </div>

                    <div
                      style={{
                        fontSize: '0.95rem',
                        fontWeight: 600,
                        color: task.is_completed ? '#94a3b8' : '#f8fafc',
                        textDecoration: task.is_completed ? 'line-through' : 'none',
                      }}
                    >
                      {task.title}
                    </div>

                    {task.reason && (
                      <div style={{ fontSize: '0.78rem', color: '#64748b', marginTop: 2 }}>
                        {task.reason}
                      </div>
                    )}
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <span
                      style={{
                        fontSize: '0.8rem',
                        color: '#94a3b8',
                        display: 'flex',
                        alignItems: 'center',
                        gap: 4,
                      }}
                    >
                      <Clock size={14} /> {task.estimated_minutes}m
                    </span>

                    <button
                      onClick={() => {
                        if (task.task_type === 'QUIZ') {
                          onNavigateToTab('quizzes', task.topic);
                        } else {
                          onNavigateToTab('tutor', task.topic);
                        }
                      }}
                      style={{
                        background: 'rgba(56, 189, 248, 0.1)',
                        border: '1px solid rgba(56, 189, 248, 0.25)',
                        color: '#38bdf8',
                        borderRadius: 8,
                        padding: '6px 12px',
                        fontSize: '0.8rem',
                        fontWeight: 600,
                        cursor: 'pointer',
                      }}
                    >
                      Launch
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Column: AI Next Action & Priority Weak Areas */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          {/* Next Best Learning Action Card */}
          {dashboard.recent_recommendation && (
            <div
              style={{
                background: 'linear-gradient(135deg, rgba(56, 189, 248, 0.12) 0%, rgba(30, 41, 59, 0.7) 100%)',
                border: '1px solid rgba(56, 189, 248, 0.3)',
                borderRadius: 18,
                padding: 22,
                boxShadow: '0 8px 24px rgba(56, 189, 248, 0.1)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#38bdf8', fontWeight: 700, fontSize: '0.85rem', marginBottom: 8 }}>
                <Sparkles size={18} /> NEXT BEST LEARNING ACTION
              </div>
              <h4 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#f8fafc', margin: '0 0 6px 0' }}>
                {dashboard.recent_recommendation.topic}
              </h4>
              <p style={{ fontSize: '0.85rem', color: '#cbd5e1', margin: '0 0 14px 0', lineHeight: 1.4 }}>
                {dashboard.recent_recommendation.reason}
              </p>
              <button
                className="btn-primary"
                onClick={() => onNavigateToTab('tutor', dashboard.recent_recommendation?.topic)}
                style={{ width: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 8 }}
              >
                <span>Start Session ({dashboard.recent_recommendation.estimated_minutes} min)</span>
                <ArrowRight size={16} />
              </button>
            </div>
          )}

          {/* Weak Areas Revision Priority */}
          <div
            style={{
              background: 'rgba(30, 41, 59, 0.4)',
              borderRadius: 18,
              padding: 22,
              border: '1px solid rgba(255, 255, 255, 0.06)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#f43f5e', fontWeight: 600, fontSize: '0.95rem', marginBottom: 12 }}>
              <AlertTriangle size={18} /> Priority Reinforcement Areas
            </div>
            <p style={{ fontSize: '0.8rem', color: '#94a3b8', margin: '0 0 14px 0' }}>
              Concepts with recorded misconceptions needing targeted remediation.
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {dashboard.priority_weak_areas.length > 0 ? (
                dashboard.priority_weak_areas.map((weak, idx) => (
                  <div
                    key={idx}
                    style={{
                      background: 'rgba(244, 63, 94, 0.08)',
                      border: '1px solid rgba(244, 63, 94, 0.2)',
                      borderRadius: 10,
                      padding: '10px 14px',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                    }}
                  >
                    <span style={{ fontSize: '0.85rem', color: '#fda4af', fontWeight: 500 }}>{weak}</span>
                    <button
                      onClick={() => onNavigateToTab('tutor', weak)}
                      style={{
                        background: 'none',
                        border: 'none',
                        color: '#f43f5e',
                        cursor: 'pointer',
                        fontSize: '0.8rem',
                        fontWeight: 600,
                      }}
                    >
                      Revise →
                    </button>
                  </div>
                ))
              ) : (
                <div style={{ color: '#94a3b8', fontSize: '0.85rem' }}>No quiz-based weak areas recorded yet.</div>
              )}
            </div>

            <button
              onClick={() => onNavigateToTab('revision')}
              style={{
                width: '100%',
                marginTop: 14,
                background: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                color: '#cbd5e1',
                padding: '8px 12px',
                borderRadius: 8,
                fontSize: '0.82rem',
                cursor: 'pointer',
              }}
            >
              Open Spaced Revision Queue
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
