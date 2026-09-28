import React, { useState } from 'react';
import { StudentProfile } from '../types';
import { 
  generateQuizQuestions, 
  submitQuizAnswers, 
  QuizQuestionData, 
  QuizSubmissionResponse 
} from '../services/api';
import { 
  Award, 
  CheckCircle2, 
  XCircle, 
  HelpCircle, 
  RotateCcw, 
  ArrowRight, 
  Clock, 
  Sparkles,
  Zap,
  Loader2,
  AlertTriangle
} from 'lucide-react';

interface QuizViewProps {
  profile: StudentProfile;
}

export const QuizView: React.FC<QuizViewProps> = ({ profile }) => {
  const [topic, setTopic] = useState(profile.currentTopic || '');
  const [difficulty, setDifficulty] = useState<'Easy' | 'Medium' | 'Hard'>('Medium');
  const [isGenerating, setIsGenerating] = useState(false);
  const [sessionId, setSessionId] = useState<string>('');
  const [questions, setQuestions] = useState<QuizQuestionData[]>([]);
  const [error, setError] = useState<string | null>(null);

  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState<{ [key: string]: any }>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submissionResult, setSubmissionResult] = useState<QuizSubmissionResponse | null>(null);

  const currentQ = questions[currentIndex] || null;

  const handleGenerateQuiz = async () => {
    if (!topic.trim()) {
      setError('Please specify a topic to generate a quiz.');
      return;
    }

    setIsGenerating(true);
    setError(null);
    try {
      const data = await generateQuizQuestions({
        topic,
        difficulty,
        num_questions: 3,
      });
      setSessionId(data.session_id);
      setQuestions(data.questions || []);
      setCurrentIndex(0);
      setSelectedAnswers({});
      setSubmissionResult(null);
    } catch (err: any) {
      console.error('Quiz generation failed:', err);
      setError(err.message || 'Failed to generate quiz. Please verify backend connection.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleOptionSelect = (optionIdx: number) => {
    if (submissionResult || !currentQ) return;
    setSelectedAnswers(prev => ({ ...prev, [currentQ.id]: optionIdx }));
  };

  const handleSubmitQuiz = async () => {
    if (!sessionId) return;
    setIsSubmitting(true);
    setError(null);
    try {
      const result = await submitQuizAnswers(sessionId, selectedAnswers);
      setSubmissionResult(result);
    } catch (err: any) {
      console.error('Quiz submission failed:', err);
      setError(err.message || 'Failed to evaluate quiz submission.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReset = () => {
    setCurrentIndex(0);
    setSelectedAnswers({});
    setSubmissionResult(null);
  };

  return (
    <div style={{
      padding: '32px',
      height: 'calc(100vh - 70px)',
      overflowY: 'auto',
      display: 'flex',
      flexDirection: 'column',
      gap: '24px',
      background: 'var(--bg-primary)'
    }}>
      {/* Quiz Generator Toolbar */}
      <div className="glass-panel" style={{
        padding: '20px 24px',
        borderRadius: 'var(--radius-lg)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '16px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flex: 1 }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', flex: 1, minWidth: '220px' }}>
            <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
              Quiz Topic
            </label>
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g. Binary Search Trees, Graph Algorithms"
              style={{
                background: 'var(--bg-tertiary)',
                color: 'var(--text-primary)',
                border: '1px solid var(--border-color)',
                padding: '8px 14px',
                borderRadius: 'var(--radius-md)',
                fontSize: '0.9rem',
                outline: 'none'
              }}
            />
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
              Difficulty
            </label>
            <select
              value={difficulty}
              onChange={(e) => setDifficulty(e.target.value as any)}
              style={{
                background: 'var(--bg-tertiary)',
                color: 'var(--text-primary)',
                border: '1px solid var(--border-color)',
                padding: '8px 14px',
                borderRadius: 'var(--radius-md)',
                fontSize: '0.9rem',
                outline: 'none'
              }}
            >
              <option value="Easy">Easy</option>
              <option value="Medium">Medium</option>
              <option value="Hard">Hard</option>
            </select>
          </div>
        </div>

        <button
          onClick={handleGenerateQuiz}
          disabled={isGenerating}
          className="btn btn-primary"
          style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
        >
          {isGenerating ? <Loader2 size={16} className="spin-slow" /> : <Sparkles size={16} />}
          <span>{isGenerating ? 'Generating Quiz...' : 'Generate AI Quiz'}</span>
        </button>
      </div>

      {/* Error Alert Banner */}
      {error && (
        <div style={{
          padding: '14px 18px',
          borderRadius: 'var(--radius-md)',
          background: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          color: 'var(--accent-rose)',
          fontSize: '0.9rem',
          display: 'flex',
          alignItems: 'center',
          gap: '10px'
        }}>
          <AlertTriangle size={18} />
          <span>{error}</span>
        </div>
      )}

      {/* Main Quiz Taking Interface or Result Screen */}
      {questions.length === 0 ? (
        <div className="glass-panel" style={{
          padding: '48px 24px',
          borderRadius: 'var(--radius-xl)',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          textAlign: 'center',
          gap: '16px'
        }}>
          <div style={{
            width: '64px',
            height: '64px',
            borderRadius: 'var(--radius-full)',
            background: 'rgba(99, 102, 241, 0.1)',
            border: '1px solid var(--border-color-glow)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--accent-primary)'
          }}>
            <Award size={32} />
          </div>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-primary)' }}>
            No Active Quiz Session
          </h3>
          <p style={{ maxWidth: '480px', fontSize: '0.9rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>
            Enter a topic in the field above (e.g. "Binary Search Trees", "Database Normalization") and click "Generate AI Quiz" to start practicing.
          </p>
        </div>
      ) : !submissionResult && currentQ ? (
        <div className="glass-panel" style={{
          padding: '32px',
          borderRadius: 'var(--radius-xl)',
          display: 'flex',
          flexDirection: 'column',
          gap: '24px'
        }}>
          {/* Question Stepper Header */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--border-color)', paddingBottom: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <span className="badge badge-beginner">
                Question {currentIndex + 1} of {questions.length}
              </span>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                {currentQ.topic} ({currentQ.difficulty})
              </span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              <Clock size={16} color="var(--accent-amber)" />
              <span>Self-Paced Practice</span>
            </div>
          </div>

          {/* Question Text */}
          <h3 style={{ fontSize: '1.2rem', fontWeight: 600, color: 'var(--text-primary)', lineHeight: 1.5 }}>
            {currentQ.question}
          </h3>

          {/* Answer Options or Short Answer Input */}
          {currentQ.type === 'short' || (!currentQ.options || currentQ.options.length === 0) ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <label style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                Type your concise conceptual explanation:
              </label>
              <textarea
                rows={4}
                value={selectedAnswers[currentQ.id] || ''}
                onChange={(e) => setSelectedAnswers(prev => ({ ...prev, [currentQ.id]: e.target.value }))}
                placeholder="Type your answer (e.g. In-order successor replaces the deleted node)..."
                style={{
                  width: '100%',
                  background: 'var(--bg-tertiary)',
                  border: '1px solid var(--border-color)',
                  color: 'var(--text-primary)',
                  padding: '14px 18px',
                  borderRadius: 'var(--radius-md)',
                  fontSize: '0.95rem',
                  fontFamily: 'var(--font-main)',
                  outline: 'none',
                  resize: 'vertical'
                }}
              />
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {currentQ.options.map((option, idx) => {
                const isSelected = selectedAnswers[currentQ.id] === idx;
                return (
                  <div
                    key={idx}
                    onClick={() => handleOptionSelect(idx)}
                    className="glass-panel"
                    style={{
                      padding: '16px 20px',
                      borderRadius: 'var(--radius-md)',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      border: isSelected ? '2px solid var(--accent-primary)' : '1px solid var(--border-color)',
                      background: isSelected ? 'rgba(99, 102, 241, 0.12)' : 'var(--bg-secondary)',
                      transition: 'var(--transition-smooth)'
                    }}
                  >
                    <span style={{ fontSize: '0.95rem', color: isSelected ? 'var(--accent-primary)' : 'var(--text-primary)', fontWeight: isSelected ? 600 : 400 }}>
                      {option}
                    </span>
                    <div style={{
                      width: '20px',
                      height: '20px',
                      borderRadius: '50%',
                      border: isSelected ? '6px solid var(--accent-primary)' : '2px solid var(--border-color)',
                      background: isSelected ? '#ffffff' : 'transparent'
                    }} />
                  </div>
                );
              })}
            </div>
          )}

          {/* Navigation & Submit Toolbar */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '12px', paddingTop: '16px', borderTop: '1px solid var(--border-color)' }}>
            <button
              onClick={() => setCurrentIndex(prev => Math.max(0, prev - 1))}
              disabled={currentIndex === 0}
              className="btn btn-secondary"
            >
              Previous
            </button>

            {currentIndex < questions.length - 1 ? (
              <button
                onClick={() => setCurrentIndex(prev => Math.min(questions.length - 1, prev + 1))}
                className="btn btn-primary"
              >
                <span>Next Question</span>
                <ArrowRight size={16} />
              </button>
            ) : (
              <button
                onClick={handleSubmitQuiz}
                disabled={isSubmitting || Object.keys(selectedAnswers).length === 0}
                className="btn btn-primary"
                style={{ background: 'var(--accent-emerald)' }}
              >
                {isSubmitting ? <Loader2 size={16} className="spin-slow" /> : <Award size={16} />}
                <span>{isSubmitting ? 'Evaluating...' : 'Submit Answers'}</span>
              </button>
            )}
          </div>
        </div>
      ) : (
        /* Quiz Evaluation & Corrective Feedback Screen */
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {/* Score Summary Banner */}
          <div className="glass-panel" style={{
            padding: '28px',
            borderRadius: 'var(--radius-xl)',
            background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(16, 185, 129, 0.15))',
            border: '1px solid var(--border-color-glow)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '20px'
          }}>
            <div>
              <span className="badge badge-beginner" style={{ marginBottom: '8px' }}>
                Evaluation Complete
              </span>
              <h2 style={{ fontSize: '1.8rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                You Scored {submissionResult.score} / {submissionResult.total_questions} ({submissionResult.percentage}%)
              </h2>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginTop: '4px' }}>
                {submissionResult.percentage >= 70 
                  ? 'Excellent mastery! Your performance has increased your student mastery score.' 
                  : 'Good effort! Areas needing revision have been logged to your Weak Topics tracker.'}
              </p>
            </div>

            <button
              onClick={handleReset}
              className="btn btn-primary"
              style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
            >
              <RotateCcw size={16} />
              <span>Take Another Quiz</span>
            </button>
          </div>

          {/* Weak Topics Warning Alert if mistakes occurred */}
          {submissionResult.mistaken_topics && submissionResult.mistaken_topics.length > 0 && (
            <div style={{
              padding: '16px 20px',
              borderRadius: 'var(--radius-lg)',
              background: 'rgba(239, 68, 68, 0.08)',
              border: '1px solid rgba(239, 68, 68, 0.25)',
              display: 'flex',
              alignItems: 'center',
              gap: '14px',
              color: 'var(--accent-rose)'
            }}>
              <AlertTriangle size={24} style={{ flexShrink: 0 }} />
              <div>
                <div style={{ fontWeight: 600 }}>
                  Weak Area Identified & Tracked
                </div>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                  Topics requiring reinforcement: <strong>{submissionResult.mistaken_topics.join(', ')}</strong>. EduMate will emphasize these in your next Socratic chat.
                </div>
              </div>
            </div>
          )}

          {/* Question Breakdown and Step-by-Step Corrective Feedback */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 600 }}>
              Question-by-Question Review
            </h3>

            {questions.map((q, idx) => {
              const userAns = selectedAnswers[q.id];
              const isCorrect = userAns !== undefined && (userAns === q.correctAnswer || String(userAns) === String(q.correctAnswer));

              return (
                <div
                  key={idx}
                  className="glass-panel"
                  style={{
                    padding: '24px',
                    borderRadius: 'var(--radius-lg)',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '14px',
                    borderLeft: isCorrect ? '4px solid var(--accent-emerald)' : '4px solid var(--accent-rose)'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <span style={{ fontWeight: 600, fontSize: '0.9rem', color: isCorrect ? 'var(--accent-emerald)' : 'var(--accent-rose)' }}>
                      {isCorrect ? '✓ Correct' : '✗ Incorrect'}
                    </span>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      {q.topic}
                    </span>
                  </div>

                  <h4 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                    {q.question}
                  </h4>

                  <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                    <div>Your answer: <strong>{q.options ? q.options[userAns] || 'None' : String(userAns)}</strong></div>
                    <div>Correct answer: <strong style={{ color: 'var(--accent-emerald)' }}>{q.options ? q.options[q.correctAnswer] || String(q.correctAnswer) : String(q.correctAnswer)}</strong></div>
                  </div>

                  {/* Step-by-Step Explanation */}
                  <div style={{
                    padding: '12px 16px',
                    background: 'rgba(99, 102, 241, 0.08)',
                    borderRadius: 'var(--radius-md)',
                    border: '1px solid var(--border-color)',
                    fontSize: '0.85rem',
                    color: 'var(--text-primary)',
                    lineHeight: 1.5
                  }}>
                    <strong>Explanation:</strong> {q.explanation}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
