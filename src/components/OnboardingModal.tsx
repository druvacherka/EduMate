import React, { useState } from 'react';
import {
  Sparkles,
  ArrowRight,
  ArrowLeft,
} from 'lucide-react';
import { submitStudentOnboarding } from '../services/api';

interface OnboardingModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCompleted: () => void;
}

export const OnboardingModal: React.FC<OnboardingModalProps> = ({ isOpen, onClose, onCompleted }) => {
  const [step, setStep] = useState<number>(1);
  const [name, setName] = useState<string>('');
  const [language, setLanguage] = useState<string>('');
  const [educationLevel, setEducationLevel] = useState<string>('');

  // Academic details
  const [institution, setInstitution] = useState<string>('');
  const [streamBranch, setStreamBranch] = useState<string>('');
  const [academicYearSemester, setAcademicYearSemester] = useState<string>('');

  // Goals & hours
  const [dailyHours, setDailyHours] = useState<number>(2.0);
  const [selectedGoals, setSelectedGoals] = useState<string[]>([]);
  const [submitting, setSubmitting] = useState<boolean>(false);

  if (!isOpen) return null;

  const isClass10 = educationLevel.includes('10');
  const isIntermediate = educationLevel.includes('11') || educationLevel.includes('12') || educationLevel.includes('Intermediate');
  const isBTech = educationLevel.includes('B.Tech') || educationLevel.includes('Engineering');

  const toggleGoal = (goalName: string) => {
    if (selectedGoals.includes(goalName)) {
      setSelectedGoals(selectedGoals.filter((g) => g !== goalName));
    } else {
      setSelectedGoals([...selectedGoals, goalName]);
    }
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      await submitStudentOnboarding({
        name: name.trim(),
        preferred_language: language || 'English',
        education_level: educationLevel,
        institution: institution.trim(),
        stream_branch: streamBranch,
        academic_year_semester: academicYearSemester,
        daily_study_hours: dailyHours,
        initial_goals: selectedGoals,
      });
      onCompleted();
      onClose();
    } catch (err) {
      console.error('Onboarding failed:', err);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        background: 'rgba(0, 0, 0, 0.8)',
        backdropFilter: 'blur(10px)',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        zIndex: 200,
        padding: 20,
      }}
    >
      <div
        style={{
          background: '#0f172a',
          border: '1px solid rgba(255, 255, 255, 0.12)',
          borderRadius: 24,
          padding: 32,
          width: '100%',
          maxWidth: 620,
          boxShadow: '0 25px 60px rgba(0, 0, 0, 0.6)',
        }}
      >
        {/* Progress indicator */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span
              style={{
                width: 28,
                height: 28,
                borderRadius: '50%',
                background: step >= 1 ? '#38bdf8' : 'rgba(255, 255, 255, 0.1)',
                color: step >= 1 ? '#0f172a' : '#94a3b8',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '0.85rem',
                fontWeight: 700,
              }}
            >
              1
            </span>
            <span style={{ fontSize: '0.85rem', color: step >= 1 ? '#f8fafc' : '#64748b' }}>Basics</span>
            <span style={{ color: '#475569' }}>—</span>
            <span
              style={{
                width: 28,
                height: 28,
                borderRadius: '50%',
                background: step >= 2 ? '#38bdf8' : 'rgba(255, 255, 255, 0.1)',
                color: step >= 2 ? '#0f172a' : '#94a3b8',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '0.85rem',
                fontWeight: 700,
              }}
            >
              2
            </span>
            <span style={{ fontSize: '0.85rem', color: step >= 2 ? '#f8fafc' : '#64748b' }}>Academics</span>
            <span style={{ color: '#475569' }}>—</span>
            <span
              style={{
                width: 28,
                height: 28,
                borderRadius: '50%',
                background: step >= 3 ? '#38bdf8' : 'rgba(255, 255, 255, 0.1)',
                color: step >= 3 ? '#0f172a' : '#94a3b8',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '0.85rem',
                fontWeight: 700,
              }}
            >
              3
            </span>
            <span style={{ fontSize: '0.85rem', color: step >= 3 ? '#f8fafc' : '#64748b' }}>Goals</span>
          </div>

          <button
            onClick={onClose}
            style={{ background: 'none', border: 'none', color: '#64748b', fontSize: '1.2rem', cursor: 'pointer' }}
          >
            ✕
          </button>
        </div>

        {/* Step 1: Basic Profile & Education Tier */}
        {step === 1 && (
          <div>
            <h2 style={{ fontSize: '1.45rem', fontWeight: 700, color: '#f8fafc', margin: '0 0 6px 0' }}>
              Welcome to EduMate! Let's tailor your experience.
            </h2>
            <p style={{ color: '#94a3b8', fontSize: '0.88rem', margin: '0 0 20px 0' }}>
              EduMate adapts curriculum, AI tutor explanations, and quiz difficulty to your education level.
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', color: '#cbd5e1', marginBottom: 6 }}>
                  Your Name:
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  style={{
                    width: '100%',
                    background: 'rgba(30, 41, 59, 0.8)',
                    border: '1px solid rgba(255, 255, 255, 0.12)',
                    borderRadius: 10,
                    padding: '10px 14px',
                    color: '#f8fafc',
                    fontSize: '0.95rem',
                    outline: 'none',
                  }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', color: '#cbd5e1', marginBottom: 6 }}>
                  Preferred Learning Language:
                </label>
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  style={{
                    width: '100%',
                    background: 'rgba(30, 41, 59, 0.8)',
                    border: '1px solid rgba(255, 255, 255, 0.12)',
                    borderRadius: 10,
                    padding: '10px 14px',
                    color: '#f8fafc',
                    fontSize: '0.95rem',
                    outline: 'none',
                  }}
                >
                  <option value="" style={{ background: '#0f172a' }}>Select a language</option>
                  <option value="English" style={{ background: '#0f172a' }}>English</option>
                  <option value="Hindi" style={{ background: '#0f172a' }}>Hindi</option>
                  <option value="Telugu" style={{ background: '#0f172a' }}>Telugu</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', color: '#cbd5e1', marginBottom: 8 }}>
                  Current Education Level:
                </label>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))', gap: 10 }}>
                  {[
                    'Class 10',
                    'Class 11',
                    'Class 12 / Intermediate',
                    'Diploma / Polytechnic',
                    'B.Tech / Engineering',
                    'Undergraduate / Degree',
                    'Postgraduate (M.Tech / MCA)',
                    'Competitive / Govt Exams',
                    'General Skill Development',
                  ].map((lvl) => {
                    const isSelected = educationLevel === lvl;
                    return (
                      <button
                        key={lvl}
                        type="button"
                        onClick={() => {
                          setEducationLevel(lvl);
                          setStreamBranch('');
                        }}
                        style={{
                          background: isSelected ? 'rgba(56, 189, 248, 0.18)' : 'rgba(30, 41, 59, 0.6)',
                          border: isSelected ? '1px solid #38bdf8' : '1px solid rgba(255, 255, 255, 0.08)',
                          borderRadius: 10,
                          padding: '10px 12px',
                          color: isSelected ? '#38bdf8' : '#cbd5e1',
                          fontSize: '0.85rem',
                          fontWeight: 600,
                          cursor: 'pointer',
                          textAlign: 'left',
                        }}
                      >
                        {lvl}
                      </button>
                    );
                  })}
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 14 }}>
                <button
                  type="button"
                  className="btn-primary"
                  onClick={() => setStep(2)}
                  style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '10px 22px' }}
                >
                  <span>Continue</span> <ArrowRight size={16} />
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Step 2: Academic Info Scoped to Education Level */}
        {step === 2 && (
          <div>
            <h2 style={{ fontSize: '1.45rem', fontWeight: 700, color: '#f8fafc', margin: '0 0 6px 0' }}>
              Academic Context ({educationLevel})
            </h2>
            <p style={{ color: '#94a3b8', fontSize: '0.88rem', margin: '0 0 20px 0' }}>
              Providing academic context helps EduMate align with your specific board or syllabus.
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', color: '#cbd5e1', marginBottom: 6 }}>
                  {isClass10 || isIntermediate
                    ? 'Board / School Name:'
                    : isBTech
                    ? 'College / University Name:'
                    : 'Institution / Organization:'}
                </label>
                <input
                  type="text"
                  placeholder={
                    isClass10
                      ? 'e.g. CBSE, ICSE, State Board'
                      : isBTech
                      ? 'e.g. IIT, NIT, JNTU, Anna University'
                      : 'e.g. State University'
                  }
                  value={institution}
                  onChange={(e) => setInstitution(e.target.value)}
                  style={{
                    width: '100%',
                    background: 'rgba(30, 41, 59, 0.8)',
                    border: '1px solid rgba(255, 255, 255, 0.12)',
                    borderRadius: 10,
                    padding: '10px 14px',
                    color: '#f8fafc',
                    fontSize: '0.95rem',
                    outline: 'none',
                  }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', color: '#cbd5e1', marginBottom: 6 }}>
                  {isClass10
                    ? 'Curriculum Stream:'
                    : isIntermediate
                    ? 'Stream (MPC / BiPC / Commerce):'
                    : isBTech
                    ? 'Engineering Branch / Specialization:'
                    : 'Target Domain / Field:'}
                </label>
                <input
                  type="text"
                  value={streamBranch}
                  onChange={(e) => setStreamBranch(e.target.value)}
                  style={{
                    width: '100%',
                    background: 'rgba(30, 41, 59, 0.8)',
                    border: '1px solid rgba(255, 255, 255, 0.12)',
                    borderRadius: 10,
                    padding: '10px 14px',
                    color: '#f8fafc',
                    fontSize: '0.95rem',
                    outline: 'none',
                  }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', color: '#cbd5e1', marginBottom: 6 }}>
                  {isClass10 ? 'Academic Year:' : 'Current Semester / Year:'}
                </label>
                <input
                  type="text"
                  value={academicYearSemester}
                  onChange={(e) => setAcademicYearSemester(e.target.value)}
                  placeholder="e.g. 3rd Year / 5th Sem, 10th Standard"
                  style={{
                    width: '100%',
                    background: 'rgba(30, 41, 59, 0.8)',
                    border: '1px solid rgba(255, 255, 255, 0.12)',
                    borderRadius: 10,
                    padding: '10px 14px',
                    color: '#f8fafc',
                    fontSize: '0.95rem',
                    outline: 'none',
                  }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 14 }}>
                <button
                  type="button"
                  onClick={() => setStep(1)}
                  style={{
                    background: 'rgba(255, 255, 255, 0.08)',
                    border: 'none',
                    color: '#cbd5e1',
                    borderRadius: 10,
                    padding: '10px 18px',
                    fontSize: '0.9rem',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 6,
                  }}
                >
                  <ArrowLeft size={16} /> Back
                </button>

                <button
                  type="button"
                  className="btn-primary"
                  onClick={() => setStep(3)}
                  style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '10px 22px' }}
                >
                  <span>Continue</span> <ArrowRight size={16} />
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Step 3: Goals & Study Budget */}
        {step === 3 && (
          <div>
            <h2 style={{ fontSize: '1.45rem', fontWeight: 700, color: '#f8fafc', margin: '0 0 6px 0' }}>
              Your Target Goals & Study Commitment
            </h2>
            <p style={{ color: '#94a3b8', fontSize: '0.88rem', margin: '0 0 20px 0' }}>
              Select target goals to populate your daily dashboard and study planner.
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', color: '#cbd5e1', marginBottom: 8 }}>
                  Select Initial Target Goals:
                </label>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {(isClass10
                    ? ['Board Exam Preparation', 'Entrance Exam Preparation', 'Scholarship Exam Preparation']
                    : isIntermediate
                    ? ['Class 12 Board Exams', 'Engineering Entrance Prep', 'Medical Entrance Prep', 'Aptitude & Logic']
                    : isBTech
                    ? [
                        'Semester Academics',
                        'Graduate Entrance Preparation',
                        'Placement Preparation',
                        'Technical Skill Development',
                      ]
                    : ['Competitive Exam Preparation', 'General Aptitude Mastery', 'Skill Development']
                  ).map((goalOption) => {
                    const isChecked = selectedGoals.includes(goalOption);
                    return (
                      <div
                        key={goalOption}
                        onClick={() => toggleGoal(goalOption)}
                        style={{
                          background: isChecked ? 'rgba(56, 189, 248, 0.12)' : 'rgba(30, 41, 59, 0.5)',
                          border: isChecked ? '1px solid #38bdf8' : '1px solid rgba(255, 255, 255, 0.06)',
                          borderRadius: 10,
                          padding: '10px 14px',
                          display: 'flex',
                          alignItems: 'center',
                          gap: 12,
                          cursor: 'pointer',
                        }}
                      >
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={() => {}}
                          style={{ accentColor: '#38bdf8' }}
                        />
                        <span style={{ fontSize: '0.9rem', color: isChecked ? '#f8fafc' : '#cbd5e1' }}>
                          {goalOption}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', color: '#cbd5e1', marginBottom: 6 }}>
                  Available Daily Study Time: <strong style={{ color: '#38bdf8' }}>{dailyHours} hours/day</strong>
                </label>
                <input
                  type="range"
                  min="1.0"
                  max="6.0"
                  step="0.5"
                  value={dailyHours}
                  onChange={(e) => setDailyHours(parseFloat(e.target.value))}
                  style={{ width: '100%', accentColor: '#38bdf8' }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 14 }}>
                <button
                  type="button"
                  onClick={() => setStep(2)}
                  style={{
                    background: 'rgba(255, 255, 255, 0.08)',
                    border: 'none',
                    color: '#cbd5e1',
                    borderRadius: 10,
                    padding: '10px 18px',
                    fontSize: '0.9rem',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 6,
                  }}
                >
                  <ArrowLeft size={16} /> Back
                </button>

                <button
                  type="button"
                  className="btn-primary"
                  disabled={submitting}
                  onClick={handleSubmit}
                  style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '10px 24px' }}
                >
                  <Sparkles size={16} />
                  <span>{submitting ? 'Setting Up...' : 'Complete & Launch'}</span>
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
