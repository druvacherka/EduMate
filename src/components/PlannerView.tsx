import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  CheckCircle2,
  RotateCw,
  ArrowRight,
} from 'lucide-react';
import { StudyPlan, StudentGoal } from '../types';
import { generateAdaptiveStudyPlan, fetchStudentGoals } from '../services/api';

interface PlannerViewProps {
  onNavigateToTab: (tab: any, topicContext?: string) => void;
}

export const PlannerView: React.FC<PlannerViewProps> = ({ onNavigateToTab }) => {
  const [goals, setGoals] = useState<StudentGoal[]>([]);
  const [selectedGoalName, setSelectedGoalName] = useState<string>('');
  const [targetDate, setTargetDate] = useState<string>('');
  const [dailyHours, setDailyHours] = useState<number>(2.0);
  const [studyPlan, setStudyPlan] = useState<StudyPlan | null>(null);
  const [generating, setGenerating] = useState<boolean>(false);

  useEffect(() => {
    loadGoalsAndDefaultPlan();
  }, []);

  const loadGoalsAndDefaultPlan = async () => {
    const goalsList = await fetchStudentGoals();
    setGoals(goalsList);
    if (goalsList.length > 0) {
      setSelectedGoalName(goalsList[0].name);
      if (goalsList[0].target_date) {
        setTargetDate(goalsList[0].target_date);
      }
      setDailyHours(goalsList[0].available_hours_per_day || 2.0);
    }
    if (goalsList.length > 0) {
      handleGeneratePlan(
        goalsList[0].name,
        goalsList[0].target_date || '',
        goalsList[0].available_hours_per_day || 2.0
      );
    }
  };

  const handleGeneratePlan = async (name: string, dateStr: string, hours: number) => {
    setGenerating(true);
    const plan = await generateAdaptiveStudyPlan({
      goal_name: name,
      target_date: dateStr,
      available_hours_per_day: hours,
      current_level: '',
    });
    setStudyPlan(plan);
    setGenerating(false);
  };

  return (
    <div style={{ maxWidth: 1100, margin: '0 auto', paddingBottom: 40 }}>
      {/* Header */}
      <div style={{ marginBottom: 28 }}>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 700, color: '#f8fafc', margin: '0 0 6px 0' }}>
          EduMate Adaptive Planner
        </h1>
        <p style={{ color: '#94a3b8', fontSize: '0.95rem', margin: 0 }}>
          Algorithmic multi-week roadmap generator that dynamically adjusts based on retention, deadlines, and study velocity.
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
            value={selectedGoalName}
            onChange={(e) => setSelectedGoalName(e.target.value)}
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
              <option key={g.id} value={g.name} style={{ background: '#0f172a' }}>
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
            disabled={generating || !selectedGoalName.trim()}
            onClick={() => handleGeneratePlan(selectedGoalName, targetDate, dailyHours)}
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
