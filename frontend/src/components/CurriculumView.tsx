import React, { useState, useEffect } from 'react';
import {
  BookOpen,
  GraduationCap,
  Cpu,
  Award,
  Briefcase,
  Target,
} from 'lucide-react';
import { CurriculumLevel } from '../types';
import { fetchCurriculumLevels } from '../services/api';

export const CurriculumView: React.FC = () => {
  const [levels, setLevels] = useState<CurriculumLevel[]>([]);
  const [activeLevelId, setActiveLevelId] = useState<string>('');
  const [activeStream, setActiveStream] = useState<string>('');

  useEffect(() => {
    loadLevels();
  }, []);

  const loadLevels = async () => {
    const data = await fetchCurriculumLevels();
    setLevels(data);
    if (data.length > 0) {
      setActiveLevelId(data[0].id);
      setActiveStream(data[0].streams[0] || '');
    }
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

      <div style={{ padding: 40, textAlign: 'center', color: '#94a3b8' }}>
        Curriculum topics are not available here.
      </div>
    </div>
  );
};
