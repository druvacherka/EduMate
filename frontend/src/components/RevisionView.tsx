import React, { useState, useEffect } from 'react';
import {
  RotateCcw,
  CheckCircle2,
  Clock,
  Sparkles,
  AlertTriangle,
  Play,
  RotateCw,
  Calendar,
  Check,
} from 'lucide-react';
import { RevisionItem } from '../types';
import { fetchRevisionItems, completeRevisionItem } from '../services/api';

interface RevisionViewProps {
  onSelectTopicForChat: (topic: string, subject: string) => void;
  onSelectTopicForQuiz: (topic: string) => void;
}

export const RevisionView: React.FC<RevisionViewProps> = ({
  onSelectTopicForChat,
  onSelectTopicForQuiz,
}) => {
  const [items, setItems] = useState<RevisionItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [filterDueOnly, setFilterDueOnly] = useState<boolean>(false);
  const [completingId, setCompletingId] = useState<number | null>(null);

  useEffect(() => {
    loadItems(filterDueOnly);
  }, [filterDueOnly]);

  const loadItems = async (dueOnly: boolean) => {
    setLoading(true);
    const data = await fetchRevisionItems(dueOnly);
    setItems(data);
    setLoading(false);
  };

  const handleMarkReviewed = async (item: RevisionItem, score: number = 85.0) => {
    setCompletingId(item.id);
    const updated = await completeRevisionItem(item.id, score);
    if (updated) {
      setItems(items.map((i) => (i.id === item.id ? updated : i)));
    }
    setCompletingId(null);
  };

  const dueCount = items.filter((i) => i.status === 'DUE').length;

  return (
    <div style={{ maxWidth: 1100, margin: '0 auto', paddingBottom: 40 }}>
      {/* Header */}
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 16 }}>
        <div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 700, color: '#f8fafc', margin: '0 0 6px 0' }}>
            Spaced Repetition & Revision Queue
          </h1>
          <p style={{ color: '#94a3b8', fontSize: '0.95rem', margin: 0 }}>
            Reinforce long-term retention using Leitner interval expansion (1 → 3 → 7 → 14 → 30 days) and prevent memory decay.
          </p>
        </div>

        {/* Filter Toggle */}
        <div style={{ display: 'flex', gap: 10 }}>
          <button
            onClick={() => setFilterDueOnly(false)}
            style={{
              background: !filterDueOnly ? 'rgba(56, 189, 248, 0.2)' : 'rgba(255, 255, 255, 0.05)',
              border: !filterDueOnly ? '1px solid rgba(56, 189, 248, 0.4)' : '1px solid rgba(255, 255, 255, 0.08)',
              color: !filterDueOnly ? '#38bdf8' : '#94a3b8',
              borderRadius: 10,
              padding: '8px 16px',
              fontSize: '0.85rem',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            All Scheduled ({items.length})
          </button>
          <button
            onClick={() => setFilterDueOnly(true)}
            style={{
              background: filterDueOnly ? 'rgba(244, 63, 94, 0.2)' : 'rgba(255, 255, 255, 0.05)',
              border: filterDueOnly ? '1px solid rgba(244, 63, 94, 0.4)' : '1px solid rgba(255, 255, 255, 0.08)',
              color: filterDueOnly ? '#f43f5e' : '#94a3b8',
              borderRadius: 10,
              padding: '8px 16px',
              fontSize: '0.85rem',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            Due Today ({dueCount})
          </button>
        </div>
      </div>

      {loading ? (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 200, color: '#94a3b8' }}>
          <RotateCw className="animate-spin" size={24} style={{ marginRight: 10 }} />
          <span>Loading revision schedule...</span>
        </div>
      ) : items.length === 0 ? (
        <div
          style={{
            background: 'rgba(30, 41, 59, 0.4)',
            borderRadius: 16,
            padding: 40,
            textAlign: 'center',
            color: '#94a3b8',
          }}
        >
          <CheckCircle2 size={40} color="#10b981" style={{ marginBottom: 12 }} />
          <h3 style={{ color: '#f8fafc', margin: '0 0 6px 0' }}>All Caught Up!</h3>
          <p style={{ margin: 0, fontSize: '0.9rem' }}>No spaced revision items are overdue right now.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {items.map((item) => {
            const isDue = item.status === 'DUE';
            const isBusy = completingId === item.id;
            return (
              <div
                key={item.id}
                style={{
                  background: isDue ? 'rgba(244, 63, 94, 0.05)' : 'rgba(30, 41, 59, 0.4)',
                  border: isDue ? '1px solid rgba(244, 63, 94, 0.25)' : '1px solid rgba(255, 255, 255, 0.06)',
                  borderRadius: 16,
                  padding: '18px 24px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  flexWrap: 'wrap',
                  gap: 16,
                }}
              >
                <div style={{ flex: 1, minWidth: 280 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                    <span
                      style={{
                        fontSize: '0.72rem',
                        fontWeight: 700,
                        textTransform: 'uppercase',
                        padding: '2px 8px',
                        borderRadius: 6,
                        background: isDue ? 'rgba(244, 63, 94, 0.15)' : 'rgba(16, 185, 129, 0.15)',
                        color: isDue ? '#f43f5e' : '#10b981',
                      }}
                    >
                      {item.status}
                    </span>
                    <span style={{ fontSize: '0.8rem', color: '#64748b' }}>• {item.subject}</span>
                  </div>

                  <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: '#f8fafc', margin: '0 0 6px 0' }}>
                    {item.topic}
                  </h3>

                  <div style={{ display: 'flex', gap: 14, fontSize: '0.8rem', color: '#94a3b8' }}>
                    <span>
                      Interval: <strong style={{ color: '#38bdf8' }}>{item.interval_days} days</strong>
                    </span>
                    <span>
                      Retention Score: <strong style={{ color: '#10b981' }}>{Math.round(item.mastery_score)}%</strong>
                    </span>
                    {item.mistake_count > 0 && (
                      <span style={{ color: '#f43f5e', display: 'flex', alignItems: 'center', gap: 4 }}>
                        <AlertTriangle size={12} /> {item.mistake_count} errors logged
                      </span>
                    )}
                  </div>
                </div>

                {/* Actions */}
                <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
                  <button
                    onClick={() => onSelectTopicForChat(item.topic, item.subject)}
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
                    <Sparkles size={14} /> AI Review
                  </button>

                  <button
                    onClick={() => onSelectTopicForQuiz(item.topic)}
                    style={{
                      background: 'rgba(168, 85, 247, 0.12)',
                      border: '1px solid rgba(168, 85, 247, 0.3)',
                      color: '#c084fc',
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
                    <Play size={14} /> Test
                  </button>

                  <button
                    onClick={() => handleMarkReviewed(item, 90.0)}
                    disabled={isBusy}
                    style={{
                      background: 'rgba(16, 185, 129, 0.15)',
                      border: '1px solid rgba(16, 185, 129, 0.3)',
                      color: '#10b981',
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
                    <Check size={14} />
                    <span>Done (+Interval)</span>
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
