import React, { useCallback, useEffect, useState } from 'react';
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
  documentQuizRequest: { id: string; name: string } | null;
}

export const QuizView: React.FC<QuizViewProps> = ({
  profile,
  documentQuizRequest,
}) => {
  const [topic, setTopic] = useState(documentQuizRequest?.name || profile.currentTopic || '');
  const [documentSource, setDocumentSource] = useState<{ id: string; name: string } | null>(documentQuizRequest);
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
  const isQuizGenerating = isGenerating || Boolean(documentQuizRequest && questions.length === 0 && !error);

  const generateQuiz = useCallback(async (
    requestedTopic = topic,
    sourceDocument: { id: string; name: string } | null = documentSource,
  ) => {
    if (!requestedTopic.trim()) {
      setError('Please specify a topic to generate a quiz.');
      return;
    }

    setIsGenerating(true);
    setError(null);
    setQuestions([]);
    setSubmissionResult(null);
    setTopic(requestedTopic);
    setDocumentSource(sourceDocument);
    try {
      const data = await generateQuizQuestions({
        topic: requestedTopic.trim(),
        difficulty,
        num_questions: 7,
        document_id: sourceDocument?.id,
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
  }, [difficulty, documentSource, topic]);

  useEffect(() => {
    if (!documentQuizRequest) return;
    let cancelled = false;
    generateQuizQuestions({
      topic: documentQuizRequest.name.trim(),
      difficulty,
      num_questions: 7,
      document_id: documentQuizRequest.id,
    }).then((data) => {
      if (cancelled) return;
      setSessionId(data.session_id);
      setQuestions(data.questions || []);
      setCurrentIndex(0);
      setSelectedAnswers({});
      setSubmissionResult(null);
    }).catch((err: unknown) => {
      if (cancelled) return;
      console.error('Document quiz generation failed:', err);
      setError(err instanceof Error ? err.message : 'Failed to generate a quiz from this study material.');
    });
    return () => {
      cancelled = true;
    };
  }, [documentQuizRequest, difficulty]);

  const handleGenerateQuiz = () => {
    void generateQuiz(topic, documentSource);
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
      padding: '24px 32px',
      height: 'calc(100vh - 56px)',
      overflowY: 'auto',
      display: 'flex',
      flexDirection: 'column',
      gap: '20px',
      background: 'var(--bg-primary)'
    }}>
      {/* Quiz Generator Toolbar */}
      <div style={{
        padding: '16px 20px',
        borderRadius: 'var(--radius-lg)',
        backgroundColor: 'var(--bg-secondary)',
        border: '1px solid var(--border-color)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '16px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flex: 1 }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', flex: 1, minWidth: '220px' }}>
            <label style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
              Quiz Topic
            </label>
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="Enter a quiz topic"
              style={{
                background: 'var(--bg-tertiary)',
                color: 'var(--text-primary)',
                border: '1px solid var(--border-color)',
                padding: '8px 12px',
                borderRadius: 'var(--radius-md)',
                fontSize: '0.86rem',
                outline: 'none'
              }}
              onFocus={(e) => e.currentTarget.style.borderColor = 'var(--accent-primary)'}
              onBlur={(e) => e.currentTarget.style.borderColor = 'var(--border-color)'}
            />
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <label style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
              Difficulty
            </label>
            <select
              value={difficulty}
              onChange={(e) => setDifficulty(e.target.value as any)}
              style={{
                background: 'var(--bg-tertiary)',
                color: 'var(--text-primary)',
                border: '1px solid var(--border-color)',
                padding: '8px 12px',
                borderRadius: 'var(--radius-md)',
                fontSize: '0.86rem',
                outline: 'none',
                cursor: 'pointer'
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
          disabled={isQuizGenerating}
          className="btn btn-primary"
          style={{ display: 'flex', alignItems: 'center', gap: '8px', borderRadius: 'var(--radius-md)', backgroundColor: 'var(--accent-primary)' }}
        >
          {isQuizGenerating ? <Loader2 size={15} className="spin-slow" /> : <Sparkles size={15} />}
          <span>{isQuizGenerating ? 'Generating Quiz...' : 'Generate AI Quiz'}</span>
        </button>
      </div>
      {documentSource && (
        <div style={{ color: 'var(--text-secondary)', fontSize: '0.84rem' }}>
          Questions will be generated from <strong style={{ color: 'var(--text-primary)' }}>{documentSource.name}</strong>.
        </div>
      )}

      {/* Error Alert Banner */}
      {error && (
        <div style={{
          padding: '12px 16px',
          borderRadius: 'var(--radius-md)',
          background: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid rgba(239, 68, 68, 0.25)',
          color: 'var(--accent-rose)',
          fontSize: '0.86rem',
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
        <div style={{
          padding: '56px 24px',
          borderRadius: 'var(--radius-lg)',
          backgroundColor: 'var(--bg-secondary)',
          border: '1px solid var(--border-color)',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          textAlign: 'center',
          gap: '16px'
        }}>
          <div style={{
            width: '56px',
            height: '56px',
            borderRadius: '50%',
            background: 'var(--accent-primary-subtle)',
            border: '1px solid rgba(37, 99, 235, 0.25)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#60a5fa'
          }}>
            <Award size={28} />
          </div>
          <h3 style={{ fontSize: '1.15rem', fontWeight: 600, color: 'var(--text-primary)' }}>
            No Active Quiz Session
          </h3>
          <p style={{ maxWidth: '440px', fontSize: '0.86rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
            Enter a topic and choose a difficulty above. Seven questions will be generated for your selection
            {documentSource ? ` from ${documentSource.name}` : ''}.
          </p>
        </div>
      ) : !submissionResult && currentQ ? (
        <div style={{
          padding: '28px',
          borderRadius: 'var(--radius-lg)',
          backgroundColor: 'var(--bg-secondary)',
          border: '1px solid var(--border-color)',
          display: 'flex',
          flexDirection: 'column',
          gap: '20px'
        }}>
          {/* Question Stepper Header */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--border-color)', paddingBottom: '14px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{
                fontSize: '0.75rem',
                fontWeight: 600,
                color: '#60a5fa',
                background: 'var(--accent-primary-subtle)',
                padding: '3px 10px',
                borderRadius: 'var(--radius-full)'
              }}>
                Question {currentIndex + 1} of {questions.length}
              </span>
              <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                {currentQ.topic} ({currentQ.difficulty})
              </span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
              <Clock size={15} color="var(--accent-amber)" />
              <span>Self-Paced Practice</span>
            </div>
          </div>

          {/* Question Text */}
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--text-primary)', lineHeight: 1.5 }}>
            {currentQ.question}
          </h3>

          {/* Answer Options or Short Answer Input */}
          {currentQ.type === 'short' || (!currentQ.options || currentQ.options.length === 0) ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <label style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
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
                  padding: '12px 16px',
                  borderRadius: 'var(--radius-md)',
                  fontSize: '0.9rem',
                  fontFamily: 'var(--font-main)',
                  outline: 'none',
                  resize: 'vertical'
                }}
              />
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {currentQ.options.map((option, idx) => {
                const isSelected = selectedAnswers[currentQ.id] === idx;
                return (
                  <div
                    key={idx}
                    onClick={() => handleOptionSelect(idx)}
                    style={{
                      padding: '14px 18px',
                      borderRadius: 'var(--radius-md)',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      border: isSelected ? '1px solid var(--accent-primary)' : '1px solid var(--border-color)',
                      background: isSelected ? 'var(--accent-primary-subtle)' : 'var(--bg-tertiary)',
                      transition: 'var(--transition-fast)'
                    }}
                    onMouseEnter={(e) => {
                      if (!isSelected) e.currentTarget.style.backgroundColor = 'var(--bg-elevated)';
                    }}
                    onMouseLeave={(e) => {
                      if (!isSelected) e.currentTarget.style.backgroundColor = 'var(--bg-tertiary)';
                    }}
                  >
                    <span style={{ fontSize: '0.9rem', color: isSelected ? '#60a5fa' : 'var(--text-primary)', fontWeight: isSelected ? 600 : 400 }}>
                      {option}
                    </span>
                    <div style={{
                      width: '18px',
                      height: '18px',
                      borderRadius: '50%',
                      border: isSelected ? '5px solid var(--accent-primary)' : '2px solid var(--border-color)',
                      background: isSelected ? '#ffffff' : 'transparent',
                      transition: 'var(--transition-fast)'
                    }} />
                  </div>
                );
              })}
            </div>
          )}

          {/* Navigation & Submit Toolbar */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '8px', paddingTop: '16px', borderTop: '1px solid var(--border-color)' }}>
            <button
              onClick={() => setCurrentIndex(prev => Math.max(0, prev - 1))}
              disabled={currentIndex === 0}
              className="btn btn-secondary"
              style={{
                backgroundColor: 'var(--bg-tertiary)',
                border: '1px solid var(--border-color)',
                color: 'var(--text-primary)'
              }}
            >
              Previous
            </button>

            {currentIndex < questions.length - 1 ? (
              <button
                onClick={() => setCurrentIndex(prev => Math.min(questions.length - 1, prev + 1))}
                className="btn btn-primary"
                style={{ backgroundColor: 'var(--accent-primary)', display: 'flex', alignItems: 'center', gap: '8px' }}
              >
                <span>Next Question</span>
                <ArrowRight size={15} />
              </button>
            ) : (
              <button
                onClick={handleSubmitQuiz}
                disabled={isSubmitting || Object.keys(selectedAnswers).length === 0}
                className="btn btn-primary"
                style={{ background: 'var(--accent-emerald)', display: 'flex', alignItems: 'center', gap: '8px' }}
              >
                {isSubmitting ? <Loader2 size={15} className="spin-slow" /> : <Award size={15} />}
                <span>{isSubmitting ? 'Evaluating...' : 'Submit Answers'}</span>
              </button>
            )}
          </div>
        </div>
      ) : (
        /* Quiz Evaluation & Corrective Feedback Screen */
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Score Summary Banner */}
          <div style={{
            padding: '24px',
            borderRadius: 'var(--radius-lg)',
            backgroundColor: 'var(--bg-secondary)',
            border: '1px solid var(--border-color)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '16px'
          }}>
            <div>
              <span style={{
                fontSize: '0.72rem',
                fontWeight: 600,
                color: 'var(--accent-emerald)',
                background: 'rgba(16, 185, 129, 0.1)',
                padding: '3px 10px',
                borderRadius: 'var(--radius-full)',
                display: 'inline-block',
                marginBottom: '8px'
              }}>
                Evaluation Complete
              </span>
              <h2 style={{ fontSize: '1.6rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                You Scored {submissionResult?.score} / {submissionResult?.total_questions} ({submissionResult?.percentage}%)
              </h2>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.86rem', marginTop: '4px' }}>
                {submissionResult && submissionResult.percentage >= 70 
                  ? 'Excellent mastery! Your performance has increased your student mastery score.' 
                  : 'Good effort! Areas needing revision have been logged to your Weak Topics tracker.'}
              </p>
            </div>

            <button
              onClick={handleReset}
              className="btn btn-primary"
              style={{ display: 'flex', alignItems: 'center', gap: '8px', backgroundColor: 'var(--accent-primary)' }}
            >
              <RotateCcw size={15} />
              <span>Take Another Quiz</span>
            </button>
          </div>

          {/* Weak Topics Warning Alert if mistakes occurred */}
          {submissionResult?.mistaken_topics && submissionResult.mistaken_topics.length > 0 && (
            <div style={{
              padding: '14px 18px',
              borderRadius: 'var(--radius-md)',
              background: 'rgba(239, 68, 68, 0.08)',
              border: '1px solid rgba(239, 68, 68, 0.25)',
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              color: 'var(--accent-rose)'
            }}>
              <AlertTriangle size={20} style={{ flexShrink: 0 }} />
              <div>
                <div style={{ fontWeight: 600, fontSize: '0.88rem' }}>
                  Weak Area Identified & Tracked
                </div>
                <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                  Topics requiring reinforcement: <strong>{submissionResult.mistaken_topics.join(', ')}</strong>. EduMate will emphasize these in your next Socratic chat.
                </div>
              </div>
            </div>
          )}

          {/* Question Breakdown and Step-by-Step Corrective Feedback */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--text-primary)' }}>
              Question-by-Question Review
            </h3>

            {questions.map((q, idx) => {
              const evaluation = submissionResult?.results.find((result) => result.id === q.id);
              const userAns = evaluation?.user_answer;
              const isCorrect = evaluation?.is_correct ?? false;
              const correctAnswer = evaluation?.correct_answer;
              const formatAnswer = (answer: unknown) => (
                q.options && typeof answer === 'number'
                  ? q.options[answer] || String(answer)
                  : answer == null
                    ? 'No answer'
                    : String(answer)
              );

              return (
                <div
                  key={idx}
                  style={{
                    padding: '20px',
                    borderRadius: 'var(--radius-lg)',
                    backgroundColor: 'var(--bg-secondary)',
                    border: '1px solid var(--border-color)',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '12px',
                    borderLeft: isCorrect ? '3px solid var(--accent-emerald)' : '3px solid var(--accent-rose)'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <span style={{ fontWeight: 600, fontSize: '0.85rem', color: isCorrect ? 'var(--accent-emerald)' : 'var(--accent-rose)' }}>
                      {isCorrect ? '✓ Correct' : '✗ Incorrect'}
                    </span>
                    <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                      {q.topic}
                    </span>
                  </div>

                  <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                    {q.question}
                  </h4>

                  <div style={{ fontSize: '0.84rem', color: 'var(--text-secondary)' }}>
                    <div>Your answer: <strong style={{ color: 'var(--text-primary)' }}>{formatAnswer(userAns)}</strong></div>
                    <div>Correct answer: <strong style={{ color: 'var(--accent-emerald)' }}>{formatAnswer(correctAnswer)}</strong></div>
                  </div>

                  {/* Step-by-Step Explanation */}
                  <div style={{
                    padding: '12px 14px',
                    background: 'var(--bg-tertiary)',
                    borderRadius: 'var(--radius-md)',
                    border: '1px solid var(--border-color)',
                    fontSize: '0.82rem',
                    color: 'var(--text-secondary)',
                    lineHeight: 1.5
                  }}>
                    <strong style={{ color: 'var(--text-primary)' }}>Explanation:</strong> {evaluation?.explanation || q.explanation}
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
