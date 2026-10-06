import React, { useState, useEffect } from 'react';
import {
  Calendar,
  Clock,
  Sparkles,
  CheckCircle2,
  Circle,
  RotateCw,
  ArrowRight,
  BookOpen,
  Zap,
  Check,
  Compass,
} from 'lucide-react';
import { StudentGoal, DailyStudyTask } from '../types';
import {
  fetchStudentGoals,
  selectStudentGoal,
  fetchDailyDashboard,
  toggleDailyTask,
} from '../services/api';

type GoalDetailSection = {
  name: string;
  weight: string;
  desc: string;
};

type GoalDetails = {
  badge: string;
  color: string;
  examPattern: string;
  sections: GoalDetailSection[];
  strategy: string;
};

interface GoalsViewProps {
  onNavigateToTab: (tab: any, topicContext?: string) => void;
}

export const GoalsView: React.FC<GoalsViewProps> = ({ onNavigateToTab }) => {
  const [goals, setGoals] = useState<StudentGoal[]>([]);
  const [activeGoal, setActiveGoal] = useState<StudentGoal | null>(null);
  const [tasks, setTasks] = useState<DailyStudyTask[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    loadGoalData();
  }, []);

  const loadGoalData = async () => {
    setLoading(true);
    const goalsData = await fetchStudentGoals();
    setGoals(goalsData);

    const active = goalsData.find((g) => g.is_active) || goalsData[0] || null;
    setActiveGoal(active);

    const dash = await fetchDailyDashboard();
    if (dash) {
      setTasks(dash.today_tasks || []);
    }
    setLoading(false);
  };

  const handleSelectGoal = async (goalId: string) => {
    const updated = await selectStudentGoal(goalId);
    if (updated) {
      setGoals((prev) =>
        prev.map((g) => ({
          ...g,
          is_active: g.id === goalId,
        }))
      );
      setActiveGoal(updated);

      // Refresh daily tasks which adapt to the new goal
      const dash = await fetchDailyDashboard();
      if (dash) {
        setTasks(dash.today_tasks || []);
      }
    }
  };

  const handleToggleTask = async (taskId: string) => {
    const updated = await toggleDailyTask(taskId);
    if (updated) {
      setTasks((prev) => prev.map((t) => (t.id === taskId ? updated : t)));
    }
  };

  // Helper for countdown
  const getDaysRemaining = (targetDateStr?: string) => {
    if (!targetDateStr) return null;
    const target = new Date(targetDateStr).getTime();
    const now = new Date().getTime();
    const diffDays = Math.ceil((target - now) / (1000 * 60 * 60 * 24));
    return diffDays > 0 ? diffDays : 0;
  };

  // Goal metadata derived from the user's saved goal fields.
  const getGoalDetails = (goalName: string): GoalDetails => {
    return {
      badge: goalName || 'Learning Goal',
      color: '#38bdf8',
      examPattern: activeGoal?.target_exam || activeGoal?.goal_type || 'Self-paced learning target',
      sections: [],
      strategy: 'Use EduMate to create tasks, generate quizzes, revise weak areas, and ask the tutor about this goal.',
    };
  };

  const currentDetails = activeGoal ? getGoalDetails(activeGoal.name) : null;
  const daysLeft = activeGoal ? getDaysRemaining(activeGoal.target_date) : null;

  return (
    <div style={{ maxWidth: 1080, margin: '0 auto', paddingBottom: 40 }}>
      {/* Header */}
      <div style={{ marginBottom: 28 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
          <div
            style={{
              padding: '6px 12px',
              borderRadius: 20,
              background: 'rgba(56, 189, 248, 0.12)',
              border: '1px solid rgba(56, 189, 248, 0.3)',
              color: '#38bdf8',
              fontSize: '0.8rem',
              fontWeight: 700,
              display: 'flex',
              alignItems: 'center',
              gap: 6,
            }}
          >
            <Compass size={14} />
            <span>GOAL WORKSPACE</span>
          </div>
        </div>
        <h1 style={{ fontSize: '1.9rem', fontWeight: 800, color: '#f8fafc', margin: '0 0 6px 0' }}>
          Select Your Target Goal
        </h1>
        <p style={{ color: '#94a3b8', fontSize: '0.95rem', margin: 0 }}>
          Choose your primary target. EduMate uses your saved goals, revision data, and quiz history to guide the dashboard.
        </p>
      </div>

      {loading ? (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 260, color: '#94a3b8' }}>
          <RotateCw className="animate-spin" size={26} style={{ marginRight: 12 }} />
          <span>Configuring curriculum goals...</span>
        </div>
      ) : (
        <>
          {/* Goal Selector Segmented Grid */}
          <div style={{ marginBottom: 30 }}>
            <label
              style={{
                display: 'block',
                fontSize: '0.82rem',
                fontWeight: 700,
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
                color: '#64748b',
                marginBottom: 12,
              }}
            >
              Available Goals
            </label>
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
                gap: 14,
              }}
            >
              {goals.map((g) => {
                const isSelected = activeGoal?.id === g.id;
                const details = getGoalDetails(g.name);
                return (
                  <div
                    key={g.id}
                    onClick={() => handleSelectGoal(g.id)}
                    style={{
                      background: isSelected
                        ? 'linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%)'
                        : 'rgba(15, 23, 42, 0.5)',
                      border: isSelected
                        ? `2px solid ${details.color}`
                        : '1px solid rgba(255, 255, 255, 0.08)',
                      borderRadius: 16,
                      padding: '18px 20px',
                      cursor: 'pointer',
                      position: 'relative',
                      transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                      boxShadow: isSelected ? `0 8px 24px -4px ${details.color}25` : 'none',
                      transform: isSelected ? 'translateY(-2px)' : 'none',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 10 }}>
                      <span
                        style={{
                          fontSize: '0.72rem',
                          fontWeight: 700,
                          padding: '3px 8px',
                          borderRadius: 6,
                          background: `${details.color}20`,
                          color: details.color,
                        }}
                      >
                        {details.badge}
                      </span>
                      {isSelected ? (
                        <div
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: 4,
                            background: `${details.color}25`,
                            color: details.color,
                            fontSize: '0.75rem',
                            fontWeight: 700,
                            padding: '3px 8px',
                            borderRadius: 12,
                          }}
                        >
                          <Check size={12} strokeWidth={3} />
                          <span>ACTIVE</span>
                        </div>
                      ) : (
                        <span style={{ fontSize: '0.75rem', color: '#64748b' }}>Select</span>
                      )}
                    </div>

                    <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#f8fafc', margin: '0 0 6px 0', lineHeight: 1.35 }}>
                      {g.name}
                    </h3>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 14, fontSize: '0.8rem', color: '#94a3b8', marginTop: 10 }}>
                      <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                        <Clock size={13} /> {g.available_hours_per_day}h/day
                      </span>
                      {g.target_date && (
                        <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                          <Calendar size={13} /> {g.target_date}
                        </span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Active Goal Spotlight Section */}
          {activeGoal && currentDetails && (
            <div
              style={{
                background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.85) 100%)',
                borderRadius: 20,
                border: '1px solid rgba(255, 255, 255, 0.1)',
                padding: '28px 32px',
                marginBottom: 28,
                position: 'relative',
                overflow: 'hidden',
                boxShadow: '0 12px 36px rgba(0, 0, 0, 0.35)',
              }}
            >
              {/* Subtle accent glow */}
              <div
                style={{
                  position: 'absolute',
                  top: -60,
                  right: -60,
                  width: 220,
                  height: 220,
                  borderRadius: '50%',
                  background: currentDetails.color,
                  opacity: 0.08,
                  filter: 'blur(50px)',
                  pointerEvents: 'none',
                }}
              />

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 20, marginBottom: 20 }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
                    <span
                      style={{
                        fontSize: '0.78rem',
                        fontWeight: 800,
                        textTransform: 'uppercase',
                        padding: '4px 10px',
                        borderRadius: 8,
                        background: `${currentDetails.color}25`,
                        color: currentDetails.color,
                        letterSpacing: '0.05em',
                      }}
                    >
                      ★ CURRENT ACTIVE TARGET
                    </span>
                    <span style={{ color: '#94a3b8', fontSize: '0.85rem' }}>{currentDetails.examPattern}</span>
                  </div>

                  <h2 style={{ fontSize: '1.6rem', fontWeight: 800, color: '#f8fafc', margin: '0 0 8px 0' }}>
                    {activeGoal.name}
                  </h2>
                  <p style={{ color: '#cbd5e1', fontSize: '0.92rem', margin: 0, maxWidth: 640 }}>
                    {currentDetails.strategy}
                  </p>
                </div>

                {/* Quick Countdown / Stat Box */}
                <div style={{ display: 'flex', gap: 14 }}>
                  {daysLeft !== null && (
                    <div
                      style={{
                        background: 'rgba(15, 23, 42, 0.7)',
                        border: '1px solid rgba(255, 255, 255, 0.08)',
                        borderRadius: 14,
                        padding: '12px 18px',
                        textAlign: 'center',
                        minWidth: 100,
                      }}
                    >
                      <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase' }}>
                        Countdown
                      </div>
                      <div style={{ fontSize: '1.6rem', fontWeight: 800, color: currentDetails.color, marginTop: 2 }}>
                        {daysLeft} <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>days</span>
                      </div>
                    </div>
                  )}

                  <div
                    style={{
                      background: 'rgba(15, 23, 42, 0.7)',
                      border: '1px solid rgba(255, 255, 255, 0.08)',
                      borderRadius: 14,
                      padding: '12px 18px',
                      textAlign: 'center',
                      minWidth: 100,
                    }}
                  >
                    <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase' }}>
                      Daily Budget
                    </div>
                    <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#38bdf8', marginTop: 2 }}>
                      {activeGoal.available_hours_per_day} <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>hrs</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Sections & Weightage Breakdown */}
              {currentDetails.sections.length > 0 && (
              <div style={{ marginBottom: 24 }}>
                <h4 style={{ fontSize: '0.88rem', fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.04em', margin: '0 0 12px 0' }}>
                  Syllabus Focus & Marks Weightage
                </h4>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 12 }}>
                  {currentDetails.sections.map((sec, idx) => (
                    <div
                      key={idx}
                      style={{
                        background: 'rgba(15, 23, 42, 0.6)',
                        border: '1px solid rgba(255, 255, 255, 0.06)',
                        borderRadius: 12,
                        padding: '14px 16px',
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                        <span style={{ fontSize: '0.9rem', fontWeight: 700, color: '#f8fafc' }}>{sec.name}</span>
                        <span style={{ fontSize: '0.78rem', fontWeight: 700, color: currentDetails.color }}>{sec.weight}</span>
                      </div>
                      <p style={{ fontSize: '0.8rem', color: '#94a3b8', margin: 0, lineHeight: 1.4 }}>
                        {sec.desc}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
              )}

              {/* Quick Action Buttons */}
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12, paddingTop: 16, borderTop: '1px solid rgba(255, 255, 255, 0.08)' }}>
                <button
                  className="btn-primary"
                  onClick={() => onNavigateToTab('tutor', activeGoal.name)}
                  style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '10px 18px', fontSize: '0.9rem' }}
                >
                  <Sparkles size={16} />
                  <span>Start AI Tutor for {activeGoal.name.split('(')[0]}</span>
                </button>

                <button
                  onClick={() => onNavigateToTab('curriculum')}
                  style={{
                    background: 'rgba(255, 255, 255, 0.06)',
                    border: '1px solid rgba(255, 255, 255, 0.12)',
                    color: '#e2e8f0',
                    borderRadius: 10,
                    padding: '10px 18px',
                    fontSize: '0.9rem',
                    fontWeight: 600,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 8,
                  }}
                >
                  <BookOpen size={16} />
                  <span>View Chapter Syllabus</span>
                </button>

                <button
                  onClick={() => onNavigateToTab('quizzes')}
                  style={{
                    background: 'rgba(255, 255, 255, 0.06)',
                    border: '1px solid rgba(255, 255, 255, 0.12)',
                    color: '#e2e8f0',
                    borderRadius: 10,
                    padding: '10px 18px',
                    fontSize: '0.9rem',
                    fontWeight: 600,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 8,
                  }}
                >
                  <Zap size={16} />
                  <span>Take Practice Test</span>
                </button>
              </div>
            </div>
          )}

          {/* Today's Tasks Dynamically Scheduled for This Goal */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
              <div>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#f8fafc', margin: '0 0 4px 0' }}>
                  Today's Scheduled Tasks (Tailored to Active Goal)
                </h3>
                <p style={{ color: '#94a3b8', fontSize: '0.85rem', margin: 0 }}>
                  These tasks come from your planner, revision queue, quizzes, and saved study activity.
                </p>
              </div>
              <span
                style={{
                  fontSize: '0.85rem',
                  fontWeight: 600,
                  color: '#38bdf8',
                  background: 'rgba(56, 189, 248, 0.1)',
                  padding: '4px 12px',
                  borderRadius: 12,
                }}
              >
                {tasks.filter((t) => t.is_completed).length} of {tasks.length} Done
              </span>
            </div>

            {tasks.length === 0 ? (
              <div
                style={{
                  background: 'rgba(15, 23, 42, 0.4)',
                  border: '1px dashed rgba(255, 255, 255, 0.1)',
                  borderRadius: 16,
                  padding: 32,
                  textAlign: 'center',
                  color: '#94a3b8',
                }}
              >
                <CheckCircle2 size={32} color="#10b981" style={{ margin: '0 auto 8px auto' }} />
                <p style={{ margin: 0 }}>All daily tasks completed for this goal! Take a test or ask the AI Tutor a question.</p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                {tasks.map((task) => (
                  <div
                    key={task.id}
                    style={{
                      background: task.is_completed ? 'rgba(15, 23, 42, 0.4)' : 'rgba(30, 41, 59, 0.5)',
                      border: task.is_completed
                        ? '1px solid rgba(255, 255, 255, 0.05)'
                        : '1px solid rgba(255, 255, 255, 0.08)',
                      borderRadius: 14,
                      padding: '16px 20px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      gap: 16,
                      opacity: task.is_completed ? 0.65 : 1,
                      transition: 'all 0.2s',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: 14, flex: 1 }}>
                      <button
                        onClick={() => handleToggleTask(task.id)}
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
                        {task.is_completed ? <CheckCircle2 size={22} /> : <Circle size={22} />}
                      </button>

                      <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                          <span
                            style={{
                              fontSize: '0.7rem',
                              fontWeight: 700,
                              textTransform: 'uppercase',
                              padding: '2px 6px',
                              borderRadius: 4,
                              background:
                                task.task_type === 'QUIZ'
                                  ? 'rgba(168, 85, 247, 0.15)'
                                  : task.task_type === 'PRACTICE'
                                  ? 'rgba(56, 189, 248, 0.15)'
                                  : 'rgba(245, 158, 11, 0.15)',
                              color:
                                task.task_type === 'QUIZ'
                                  ? '#c084fc'
                                  : task.task_type === 'PRACTICE'
                                  ? '#38bdf8'
                                  : '#fbbf24',
                            }}
                          >
                            {task.task_type}
                          </span>
                          <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>{task.subject}</span>
                        </div>

                        <div
                          style={{
                            fontSize: '0.96rem',
                            fontWeight: 600,
                            color: task.is_completed ? '#94a3b8' : '#f8fafc',
                            textDecoration: task.is_completed ? 'line-through' : 'none',
                          }}
                        >
                          {task.title}
                        </div>

                        {task.reason && (
                          <div style={{ fontSize: '0.78rem', color: '#64748b', marginTop: 3 }}>
                            🎯 {task.reason}
                          </div>
                        )}
                      </div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                      <span style={{ fontSize: '0.82rem', color: '#94a3b8', whiteSpace: 'nowrap' }}>
                        {task.estimated_minutes} mins
                      </span>

                      {!task.is_completed && (
                        <button
                          onClick={() => {
                            if (task.task_type === 'QUIZ') {
                              onNavigateToTab('quizzes');
                            } else {
                              onNavigateToTab('tutor', `${task.subject}: ${task.topic}`);
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
                            display: 'flex',
                            alignItems: 'center',
                            gap: 4,
                          }}
                        >
                          <span>{task.task_type === 'QUIZ' ? 'Quiz' : 'Study'}</span>
                          <ArrowRight size={13} />
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};
