import React, { useState, useEffect } from 'react';
import {
  BookOpen,
  GraduationCap,
  Cpu,
  Award,
  Briefcase,
  Target,
  ChevronRight,
  Sparkles,
  CheckCircle,
  HelpCircle,
  Play,
  RotateCw,
} from 'lucide-react';
import { CurriculumLevel, CurriculumSubject } from '../types';
import { fetchCurriculumLevels, fetchCurriculumHierarchy } from '../services/api';

interface CurriculumViewProps {
  onSelectTopicForChat: (topic: string, subject: string) => void;
  onSelectTopicForQuiz: (topic: string) => void;
}

export const CurriculumView: React.FC<CurriculumViewProps> = ({
  onSelectTopicForChat,
  onSelectTopicForQuiz,
}) => {
  const [levels, setLevels] = useState<CurriculumLevel[]>([]);
  const [activeLevelId, setActiveLevelId] = useState<string>('class_10');
  const [activeStream, setActiveStream] = useState<string>('General (All Subjects)');
  const [subjects, setSubjects] = useState<CurriculumSubject[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [expandedChapter, setExpandedChapter] = useState<string | null>(null);

  useEffect(() => {
    loadLevels();
  }, []);

  useEffect(() => {
    if (activeLevelId) {
      loadHierarchy(activeLevelId, activeStream);
    }
  }, [activeLevelId, activeStream]);

  const loadLevels = async () => {
    const data = await fetchCurriculumLevels();
    setLevels(data);
    if (data.length > 0) {
      const initial = data.find((d) => d.id === 'class_10') || data[0];
      setActiveLevelId(initial.id);
      setActiveStream(initial.streams[0] || 'General (All Subjects)');
    }
  };

  const loadHierarchy = async (levelId: string, stream: string) => {
    setLoading(true);
    const data = await fetchCurriculumHierarchy(levelId, stream);
    setSubjects(data.subjects || []);
    if (data.subjects && data.subjects.length > 0 && data.subjects[0].chapters.length > 0) {
      setExpandedChapter(data.subjects[0].chapters[0].name);
    }
    setLoading(false);
  };

  const activeLevel = levels.find((l) => l.id === activeLevelId);

  const getLevelIcon = (id: string) => {
    switch (id) {
      case 'class_10':
        return <GraduationCap size={20} />;
      case 'intermediate':
        return <BookOpen size={20} />;
      case 'btech':
        return <Cpu size={20} />;
      case 'gate':
        return <Award size={20} />;
      case 'govt_exams':
        return <Briefcase size={20} />;
      case 'placement_prep':
        return <Target size={20} />;
      default:
        return <GraduationCap size={20} />;
    }
  };

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', paddingBottom: 40 }}>
      {/* Header */}
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 700, color: '#f8fafc', margin: '0 0 6px 0' }}>
          Universal Curriculum & Concept Explorer
        </h1>
        <p style={{ color: '#94a3b8', fontSize: '0.95rem', margin: 0 }}>
          Explore structured curricula from secondary school to engineering, GATE, and competitive examinations.
        </p>
      </div>

      {/* Education Level Selector Tabs */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
          gap: 12,
          marginBottom: 24,
        }}
      >
        {levels.map((lvl) => {
          const isActive = lvl.id === activeLevelId;
          return (
            <button
              key={lvl.id}
              onClick={() => {
                setActiveLevelId(lvl.id);
                setActiveStream(lvl.streams[0] || '');
              }}
              style={{
                background: isActive
                  ? 'linear-gradient(135deg, rgba(56, 189, 248, 0.2) 0%, rgba(30, 41, 59, 0.9) 100%)'
                  : 'rgba(30, 41, 59, 0.4)',
                border: isActive
                  ? '1px solid rgba(56, 189, 248, 0.5)'
                  : '1px solid rgba(255, 255, 255, 0.06)',
                borderRadius: 14,
                padding: '14px 16px',
                color: isActive ? '#38bdf8' : '#94a3b8',
                cursor: 'pointer',
                textAlign: 'left',
                display: 'flex',
                flexDirection: 'column',
                gap: 6,
                transition: 'all 0.2s',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: isActive ? '#38bdf8' : '#64748b' }}>
                {getLevelIcon(lvl.id)}
                <span style={{ fontSize: '0.95rem', fontWeight: 700, color: isActive ? '#f8fafc' : '#cbd5e1' }}>
                  {lvl.title.split('(')[0]}
                </span>
              </div>
              <span style={{ fontSize: '0.75rem', color: '#64748b', lineHeight: 1.3 }}>
                {lvl.description.slice(0, 50)}...
              </span>
            </button>
          );
        })}
      </div>

      {/* Stream / Branch Selector */}
      {activeLevel && activeLevel.streams.length > 1 && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 24, flexWrap: 'wrap' }}>
          <span style={{ fontSize: '0.85rem', color: '#94a3b8', fontWeight: 600 }}>Stream / Discipline:</span>
          {activeLevel.streams.map((stream) => {
            const isStreamActive = stream === activeStream;
            return (
              <button
                key={stream}
                onClick={() => setActiveStream(stream)}
                style={{
                  background: isStreamActive ? 'rgba(56, 189, 248, 0.15)' : 'rgba(255, 255, 255, 0.05)',
                  border: isStreamActive
                    ? '1px solid rgba(56, 189, 248, 0.4)'
                    : '1px solid rgba(255, 255, 255, 0.08)',
                  borderRadius: 20,
                  padding: '6px 14px',
                  color: isStreamActive ? '#38bdf8' : '#94a3b8',
                  fontSize: '0.82rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                }}
              >
                {stream}
              </button>
            );
          })}
        </div>
      )}

      {/* Hierarchy Subjects & Chapters */}
      {loading ? (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 200, color: '#94a3b8' }}>
          <RotateCw className="animate-spin" size={24} style={{ marginRight: 10 }} />
          <span>Loading curriculum hierarchy...</span>
        </div>
      ) : subjects.length === 0 ? (
        <div style={{ padding: 40, textAlign: 'center', color: '#94a3b8' }}>
          No subjects listed for this stream yet.
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          {subjects.map((subj, subjIdx) => (
            <div
              key={subjIdx}
              style={{
                background: 'rgba(30, 41, 59, 0.4)',
                borderRadius: 18,
                padding: 24,
                border: '1px solid rgba(255, 255, 255, 0.06)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
                <BookOpen size={20} color="#38bdf8" />
                <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#f8fafc', margin: 0 }}>
                  {subj.subject}
                </h2>
                <span
                  style={{
                    background: 'rgba(255, 255, 255, 0.08)',
                    padding: '2px 8px',
                    borderRadius: 12,
                    fontSize: '0.75rem',
                    color: '#94a3b8',
                  }}
                >
                  {subj.chapters.length} chapters
                </span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                {subj.chapters.map((ch, chIdx) => {
                  const isExpanded = expandedChapter === ch.name;
                  return (
                    <div
                      key={chIdx}
                      style={{
                        background: 'rgba(15, 23, 42, 0.6)',
                        border: '1px solid rgba(255, 255, 255, 0.05)',
                        borderRadius: 12,
                        overflow: 'hidden',
                      }}
                    >
                      <button
                        onClick={() => setExpandedChapter(isExpanded ? null : ch.name)}
                        style={{
                          width: '100%',
                          background: 'none',
                          border: 'none',
                          padding: '14px 18px',
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          color: '#f8fafc',
                          cursor: 'pointer',
                          fontSize: '0.95rem',
                          fontWeight: 600,
                          textAlign: 'left',
                        }}
                      >
                        <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <ChevronRight
                            size={16}
                            style={{
                              transform: isExpanded ? 'rotate(90deg)' : 'none',
                              transition: 'transform 0.2s',
                              color: '#38bdf8',
                            }}
                          />
                          Chapter: {ch.name}
                        </span>
                        <span style={{ fontSize: '0.8rem', color: '#64748b' }}>
                          {ch.topics.length} topics
                        </span>
                      </button>

                      {isExpanded && (
                        <div
                          style={{
                            padding: '6px 18px 18px 18px',
                            borderTop: '1px solid rgba(255, 255, 255, 0.04)',
                            display: 'flex',
                            flexDirection: 'column',
                            gap: 10,
                          }}
                        >
                          {ch.topics.map((top, topIdx) => (
                            <div
                              key={topIdx}
                              style={{
                                background: 'rgba(30, 41, 59, 0.5)',
                                borderRadius: 10,
                                padding: '12px 16px',
                                display: 'flex',
                                justifyContent: 'space-between',
                                alignItems: 'center',
                                flexWrap: 'wrap',
                                gap: 12,
                              }}
                            >
                              <div style={{ flex: 1, minWidth: 260 }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                                  <span style={{ fontSize: '0.95rem', fontWeight: 600, color: '#f8fafc' }}>
                                    {top.name}
                                  </span>
                                  <span
                                    style={{
                                      fontSize: '0.7rem',
                                      padding: '2px 6px',
                                      borderRadius: 6,
                                      fontWeight: 600,
                                      background:
                                        top.difficulty === 'Hard'
                                          ? 'rgba(244, 63, 94, 0.15)'
                                          : top.difficulty === 'Medium'
                                          ? 'rgba(245, 158, 11, 0.15)'
                                          : 'rgba(16, 185, 129, 0.15)',
                                      color:
                                        top.difficulty === 'Hard'
                                          ? '#f43f5e'
                                          : top.difficulty === 'Medium'
                                          ? '#f59e0b'
                                          : '#10b981',
                                    }}
                                  >
                                    {top.difficulty}
                                  </span>
                                </div>

                                <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                                  {top.concepts.map((concept, cIdx) => (
                                    <span
                                      key={cIdx}
                                      style={{
                                        fontSize: '0.75rem',
                                        color: '#94a3b8',
                                        background: 'rgba(255, 255, 255, 0.04)',
                                        padding: '2px 8px',
                                        borderRadius: 6,
                                      }}
                                    >
                                      {concept}
                                    </span>
                                  ))}
                                </div>
                              </div>

                              <div style={{ display: 'flex', gap: 8 }}>
                                <button
                                  onClick={() => onSelectTopicForChat(top.name, subj.subject)}
                                  style={{
                                    background: 'rgba(56, 189, 248, 0.12)',
                                    border: '1px solid rgba(56, 189, 248, 0.3)',
                                    color: '#38bdf8',
                                    borderRadius: 8,
                                    padding: '6px 12px',
                                    fontSize: '0.8rem',
                                    fontWeight: 600,
                                    cursor: 'pointer',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: 6,
                                  }}
                                >
                                  <Sparkles size={14} /> Tutor Me
                                </button>

                                <button
                                  onClick={() => onSelectTopicForQuiz(top.name)}
                                  style={{
                                    background: 'rgba(168, 85, 247, 0.12)',
                                    border: '1px solid rgba(168, 85, 247, 0.3)',
                                    color: '#c084fc',
                                    borderRadius: 8,
                                    padding: '6px 12px',
                                    fontSize: '0.8rem',
                                    fontWeight: 600,
                                    cursor: 'pointer',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: 6,
                                  }}
                                >
                                  <Play size={14} /> Quiz
                                </button>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
