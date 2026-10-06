import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  CheckCircle2,
  RotateCw,
  ArrowRight,
  AlertTriangle,
} from 'lucide-react';
import { StudyPlan, StudentGoal } from '../types';
import { generateAdaptiveStudyPlan, fetchStudentGoals } from '../services/api';

interface PlannerViewProps {
  onNavigateToTab: (tab: any, topicContext?: string) => void;
}

export const PlannerView: React.FC<PlannerViewProps> = ({ onNavigateToTab }) => {
  const [goals, setGoals] = useState<StudentGoal[]>([]);
  const [selectedGoalId, setSelectedGoalId] = useState<string>('');
  const [targetDate, setTargetDate] = useState<string>('');
  const [dailyHours, setDailyHours] = useState<number>(2.0);
  const [studyPlan, setStudyPlan] = useState<StudyPlan | null>(null);
  const [generating, setGenerating] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const selectedGoal = goals.find((goal) => goal.id === selectedGoalId);

  useEffect(() => {
    loadGoalsAndDefaultPlan();
  }, []);

  const loadGoalsAndDefaultPlan = async () => {
    const goalsList = await fetchStudentGoals();
    setGoals(goalsList);
    if (goalsList.length > 0) {
      setSelectedGoalId(goalsList[0].id);
      if (goalsList[0].target_date) {
        setTargetDate(goalsList[0].target_date);
      }
      setDailyHours(goalsList[0].available_hours_per_day);
    }
  };

  const handleGeneratePlan = async () => {
    if (!selectedGoal) {
      setError('Create or select a goal before generating a study plan.');
      return;
    }

    setGenerating(true);
    setError(null);
    try {
      const plan = await generateAdaptiveStudyPlan({
        goal_id: selectedGoal.id,
        goal_name: selectedGoal.name,
        target_date: targetDate,
        available_hours_per_day: dailyHours,
        current_level: selectedGoal.current_level || undefined,
        target_level: selectedGoal.target_level || undefined,
      });
      setStudyPlan(plan);
    } catch (generationError) {
      setError(
        generationError instanceof Error
          ? generationError.message
          : 'Could not generate the adaptive study plan.'
      );
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div style={{ maxWidth: 1100, margin: '0 auto', paddingBottom: 40 }}>
      {/* Header */}
      <div style={{ marginBottom: 28 }}>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 700, color: '#f8fafc', margin: '0 0 6px 0' }}>
          EduMate Adaptive Planner
        </h1>
        <p style={{ color: '#94a3b8', fontSize: '0.95rem', margin: 0 }}>
          Gemini generates a study roadmap from your goal, deadline, available hours, learning level, and recorded weak areas.
        </p>
      </div>

      {/* Configuration Card */}
      <div
        style={{
          background: 'rgba(30, 41, 59, 0.5)',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          borderRadius: 18,
          padding: 24,
          marginBottom: 32,
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: 20,
          alignItems: 'end',
        }}
      >
        <div>
          <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#cbd5e1', marginBottom: 8 }}>
            Target Goal / Examination:
          </label>
          <select
            value={selectedGoalId}
            onChange={(e) => {
              const goal = goals.find((item) => item.id === e.target.value);
              setSelectedGoalId(e.target.value);
              if (goal) {
                setTargetDate(goal.target_date || '');
                setDailyHours(goal.available_hours_per_day);
              }
              setStudyPlan(null);
              setError(null);
            }}
            style={{
              width: '100%',
              background: 'rgba(15, 23, 42, 0.8)',
              border: '1px solid rgba(255, 255, 255, 0.12)',
              borderRadius: 10,
              padding: '10px 14px',
              color: '#f8fafc',
              fontSize: '0.9rem',
              outline: 'none',
            }}
          >
            {goals.map((g) => (
              <option key={g.id} value={g.id} style={{ background: '#0f172a' }}>
                {g.name}
              </option>
            ))}
            {goals.length === 0 && (
              <option value="" style={{ background: '#0f172a' }}>
                Create a goal first
              </option>
            )}
          </select>
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#cbd5e1', marginBottom: 8 }}>
            Target Completion Date:
          </label>
          <input
            type="date"
            value={targetDate}
            onChange={(e) => setTargetDate(e.target.value)}
            style={{
              width: '100%',
              background: 'rgba(15, 23, 42, 0.8)',
              border: '1px solid rgba(255, 255, 255, 0.12)',
              borderRadius: 10,
              padding: '9px 14px',
              color: '#f8fafc',
              fontSize: '0.9rem',
              outline: 'none',
            }}
          />
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#cbd5e1', marginBottom: 8 }}>
            Daily Hours: <strong style={{ color: '#38bdf8' }}>{dailyHours}h / day</strong>
          </label>
          <input
            type="range"
            min="0.5"
            max="6.0"
            step="0.5"
            value={dailyHours}
            onChange={(e) => setDailyHours(parseFloat(e.target.value))}
            style={{ width: '100%', accentColor: '#38bdf8' }}
          />
        </div>

        <div>
          <button
            className="btn-primary"
            disabled={generating || !selectedGoalId}
            onClick={handleGeneratePlan}
            style={{
              width: '100%',
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              gap: 8,
              height: 42,
            }}
          >
            {generating ? <RotateCw className="animate-spin" size={16} /> : <Sparkles size={16} />}
            <span>{generating ? 'Calculating...' : 'Recalculate Plan'}</span>
          </button>
        </div>
      </div>

      {error && (
        <div
          role="alert"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            padding: '12px 16px',
            marginBottom: 24,
            borderRadius: 10,
            color: '#fb7185',
            background: 'rgba(244, 63, 94, 0.1)',
            border: '1px solid rgba(244, 63, 94, 0.25)',
          }}
        >
          <AlertTriangle size={17} />
          <span>{error}</span>
        </div>
      )}

      {/* Plan Status Overview */}
      {studyPlan && (
        <div>
          <div
            style={{
              background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(30, 41, 59, 0.6) 100%)',
              border: '1px solid rgba(16, 185, 129, 0.25)',
              borderRadius: 16,
              padding: '18px 24px',
              marginBottom: 28,
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              flexWrap: 'wrap',
              gap: 16,
            }}
          >
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#10b981', fontWeight: 700, fontSize: '0.85rem' }}>
                <CheckCircle2 size={18} /> ADAPTIVE ROADMAP ACTIVE
              </div>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#f8fafc', margin: '4px 0 0 0' }}>
                {studyPlan.title}
              </h3>
            </div>
            <div style={{ display: 'flex', gap: 20 }}>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 600 }}>
                  Planned Total
                </div>
                <div style={{ fontSize: '1.3rem', fontWeight: 800, color: '#38bdf8' }}>
                  {studyPlan.total_hours_planned} hrs
                </div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 600 }}>
                  Duration
                </div>
                <div style={{ fontSize: '1.3rem', fontWeight: 800, color: '#10b981' }}>
                  {studyPlan.weekly_breakdown.length} weeks
                </div>
              </div>
            </div>
          </div>

          {/* Weekly Breakdown Grid */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {studyPlan.weekly_breakdown.map((item) => (
              <div
                key={item.week_number}
                style={{
                  background: 'rgba(30, 41, 59, 0.4)',
                  border: '1px solid rgba(255, 255, 255, 0.06)',
                  borderRadius: 14,
                  padding: 20,
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'flex-start',
                  flexWrap: 'wrap',
                  gap: 16,
                }}
              >
                <div style={{ flex: 1, minWidth: 280 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
                    <span
                      style={{
                        background: 'rgba(56, 189, 248, 0.15)',
                        color: '#38bdf8',
                        padding: '4px 10px',
                        borderRadius: 8,
                        fontSize: '0.8rem',
                        fontWeight: 700,
                      }}
                    >
                      Week {item.week_number}
                    </span>
                    <h4 style={{ fontSize: '1.05rem', fontWeight: 600, color: '#f8fafc', margin: 0 }}>
                      {item.theme.split(': ')[1] || item.theme}
                    </h4>
                  </div>

                  <div style={{ fontSize: '0.85rem', color: '#94a3b8', marginBottom: 10 }}>
                    🎯 <strong>Milestone:</strong> {item.target_milestone}
                  </div>

                  <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                    {item.focus_topics.map((top, idx) => (
                      <span
                        key={idx}
                        onClick={() => onNavigateToTab('tutor', top)}
                        style={{
                          fontSize: '0.78rem',
                          color: '#cbd5e1',
                          background: 'rgba(255, 255, 255, 0.05)',
                          border: '1px solid rgba(255, 255, 255, 0.08)',
                          padding: '3px 10px',
                          borderRadius: 6,
                          cursor: 'pointer',
                        }}
                      >
                        {top} →
                      </span>
                    ))}
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '0.75rem', color: '#64748b' }}>Weekly Budget</div>
                    <div style={{ fontSize: '1rem', fontWeight: 700, color: '#e2e8f0' }}>
                      {item.estimated_hours}h
                    </div>
                  </div>

                  <button
                    onClick={() => onNavigateToTab('tutor', item.focus_topics[0])}
                    style={{
                      background: 'rgba(56, 189, 248, 0.12)',
                      border: '1px solid rgba(56, 189, 248, 0.3)',
                      color: '#38bdf8',
                      borderRadius: 8,
                      padding: '8px 14px',
                      fontSize: '0.82rem',
                      fontWeight: 600,
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 6,
                    }}
                  >
                    <span>Start Week</span> <ArrowRight size={14} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
