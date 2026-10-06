import React, { useState, useEffect } from 'react';
import {
  Compass,
  Briefcase,
  GraduationCap,
  Award,
  Layers,
  CheckCircle,
  ArrowRight,
  BookOpen,
  Sparkles,
  RotateCw,
} from 'lucide-react';
import { CareerPath } from '../types';
import { fetchCareerPaths, createStudentGoal } from '../services/api';

interface CareerExplorerViewProps {
  onNavigateToTab: (tab: any, topicContext?: string) => void;
}

export const CareerExplorerView: React.FC<CareerExplorerViewProps> = ({ onNavigateToTab }) => {
  const [paths, setPaths] = useState<CareerPath[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedPath, setSelectedPath] = useState<CareerPath | null>(null);
  const [adoptedMessage, setAdoptedMessage] = useState<string | null>(null);

  useEffect(() => {
    loadCareerPaths();
  }, []);

  const loadCareerPaths = async () => {
    setLoading(true);
    const data = await fetchCareerPaths();
    setPaths(data);
    if (data.length > 0) {
      setSelectedPath(data[0]);
    }
    setLoading(false);
  };

  const handleAdoptAsGoal = async (path: CareerPath) => {
    await createStudentGoal({
      name: `${path.title} Preparation`,
      goal_type: 'career',
      target_exam: path.primary_exams[0] || '',
      priority: 'HIGH',
      available_hours_per_day: 2.0,
      current_level: '',
      target_level: '',
    });
    setAdoptedMessage(`Successfully adopted "${path.title}" into your active goals!`);
    setTimeout(() => setAdoptedMessage(null), 4000);
  };

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', paddingBottom: 40 }}>
      {/* Header */}
      <div style={{ marginBottom: 28 }}>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 700, color: '#f8fafc', margin: '0 0 6px 0' }}>
          Career Explorer & Exam Blueprints
        </h1>
        <p style={{ color: '#94a3b8', fontSize: '0.95rem', margin: 0 }}>
          Here are available career trajectories, prerequisite degrees, essential syllabus subjects, and milestone roadmaps. You remain in complete control of your decisions.
        </p>
      </div>

      {adoptedMessage && (
        <div
          style={{
            background: 'rgba(16, 185, 129, 0.15)',
            border: '1px solid rgba(16, 185, 129, 0.3)',
            borderRadius: 12,
            padding: '12px 18px',
            color: '#6ee7b7',
            marginBottom: 20,
            display: 'flex',
            alignItems: 'center',
            gap: 10,
          }}
        >
          <CheckCircle size={18} />
          <span>{adoptedMessage}</span>
        </div>
      )}

      {loading ? (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 200, color: '#94a3b8' }}>
          <RotateCw className="animate-spin" size={24} style={{ marginRight: 10 }} />
          <span>Loading career blueprints...</span>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: 24, alignItems: 'start' }}>
          {/* Left Column: Career Cards */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {paths.map((p) => {
              const isSelected = selectedPath?.id === p.id;
              return (
                <div
                  key={p.id}
                  onClick={() => setSelectedPath(p)}
                  style={{
                    background: isSelected
                      ? 'linear-gradient(135deg, rgba(56, 189, 248, 0.18) 0%, rgba(30, 41, 59, 0.8) 100%)'
                      : 'rgba(30, 41, 59, 0.4)',
                    border: isSelected
                      ? '1px solid rgba(56, 189, 248, 0.4)'
                      : '1px solid rgba(255, 255, 255, 0.06)',
                    borderRadius: 14,
                    padding: '16px 18px',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                  }}
                >
                  <span
                    style={{
                      fontSize: '0.72rem',
                      fontWeight: 700,
                      textTransform: 'uppercase',
                      color: isSelected ? '#38bdf8' : '#94a3b8',
                    }}
                  >
                    {p.category}
                  </span>
                  <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: '#f8fafc', margin: '4px 0 6px 0' }}>
                    {p.title}
                  </h3>
                  <p style={{ fontSize: '0.8rem', color: '#94a3b8', margin: 0, lineHeight: 1.3 }}>
                    {p.description.slice(0, 85)}...
                  </p>
                </div>
              );
            })}
          </div>

          {/* Right Column: Path Detail */}
          {selectedPath && (
            <div
              style={{
                background: 'rgba(30, 41, 59, 0.45)',
                border: '1px solid rgba(255, 255, 255, 0.08)',
                borderRadius: 20,
                padding: 28,
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 14, marginBottom: 16 }}>
                <div>
                  <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#38bdf8', textTransform: 'uppercase' }}>
                    {selectedPath.category}
                  </span>
                  <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#f8fafc', margin: '4px 0 8px 0' }}>
                    {selectedPath.title}
                  </h2>
                </div>

                <button
                  className="btn-primary"
                  onClick={() => handleAdoptAsGoal(selectedPath)}
                  style={{ display: 'flex', alignItems: 'center', gap: 8 }}
                >
                  <Sparkles size={16} />
                  <span>Adopt as Target Goal</span>
                </button>
              </div>

              <p style={{ color: '#cbd5e1', fontSize: '0.92rem', lineHeight: 1.5, marginBottom: 24 }}>
                {selectedPath.description}
              </p>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 24 }}>
                {/* Degrees */}
                <div
                  style={{
                    background: 'rgba(15, 23, 42, 0.5)',
                    borderRadius: 12,
                    padding: 16,
                    border: '1px solid rgba(255, 255, 255, 0.05)',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#38bdf8', fontWeight: 600, fontSize: '0.85rem', marginBottom: 8 }}>
                    <GraduationCap size={16} /> Prerequisite Degrees
                  </div>
                  <ul style={{ margin: 0, paddingLeft: 18, color: '#cbd5e1', fontSize: '0.82rem', lineHeight: 1.5 }}>
                    {selectedPath.target_degrees.map((d, i) => (
                      <li key={i}>{d}</li>
                    ))}
                  </ul>
                </div>

                {/* Primary Exams */}
                <div
                  style={{
                    background: 'rgba(15, 23, 42, 0.5)',
                    borderRadius: 12,
                    padding: 16,
                    border: '1px solid rgba(255, 255, 255, 0.05)',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#f59e0b', fontWeight: 600, fontSize: '0.85rem', marginBottom: 8 }}>
                    <Award size={16} /> Primary Entrance / Screening Exams
                  </div>
                  <ul style={{ margin: 0, paddingLeft: 18, color: '#cbd5e1', fontSize: '0.82rem', lineHeight: 1.5 }}>
                    {selectedPath.primary_exams.map((ex, i) => (
                      <li key={i}>{ex}</li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Core Syllabus Subjects */}
              <div style={{ marginBottom: 24 }}>
                <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: '#f8fafc', marginBottom: 10, display: 'flex', alignItems: 'center', gap: 8 }}>
                  <BookOpen size={16} color="#38bdf8" /> Essential Syllabus Subjects
                </h4>
                <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                  {selectedPath.core_subjects.map((sub, i) => (
                    <span
                      key={i}
                      onClick={() => onNavigateToTab('tutor', sub)}
                      style={{
                        background: 'rgba(56, 189, 248, 0.1)',
                        border: '1px solid rgba(56, 189, 248, 0.25)',
                        color: '#38bdf8',
                        padding: '4px 12px',
                        borderRadius: 8,
                        fontSize: '0.82rem',
                        cursor: 'pointer',
                      }}
                    >
                      {sub} →
                    </span>
                  ))}
                </div>
              </div>

              {/* Key Skills */}
              <div style={{ marginBottom: 28 }}>
                <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: '#f8fafc', marginBottom: 10, display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Layers size={16} color="#10b981" /> Technical Skills & Tools
                </h4>
                <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                  {selectedPath.key_skills.map((skill, i) => (
                    <span
                      key={i}
                      style={{
                        background: 'rgba(16, 185, 129, 0.1)',
                        border: '1px solid rgba(16, 185, 129, 0.25)',
                        color: '#6ee7b7',
                        padding: '4px 12px',
                        borderRadius: 8,
                        fontSize: '0.82rem',
                      }}
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>

              {/* Typical Milestone Roadmap */}
              <div>
                <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: '#f8fafc', marginBottom: 14 }}>
                  Typical Preparation Roadmap
                </h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                  {selectedPath.typical_roadmap.map((step, i) => (
                    <div
                      key={i}
                      style={{
                        background: 'rgba(15, 23, 42, 0.6)',
                        border: '1px solid rgba(255, 255, 255, 0.05)',
                        borderRadius: 10,
                        padding: '12px 16px',
                        fontSize: '0.85rem',
                        color: '#cbd5e1',
                        lineHeight: 1.4,
                      }}
                    >
                      {step}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
