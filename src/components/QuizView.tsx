import React, { useState } from 'react';
import { QuizQuestion, StudentProfile } from '../types';
import { 
  Award, 
  CheckCircle2, 
  XCircle, 
  HelpCircle, 
  RotateCcw, 
  ArrowRight, 
  Clock, 
  Sparkles,
  Zap
} from 'lucide-react';

interface QuizViewProps {
  profile: StudentProfile;
}

export const QuizView: React.FC<QuizViewProps> = ({ profile }) => {
  const sampleQuestions: QuizQuestion[] = [
    {
      id: 'q1',
      type: 'mcq',
      topic: 'Binary Search Tree',
      difficulty: 'Easy',
      question: 'What is the average time complexity for searching an element in a balanced Binary Search Tree?',
      options: ['O(1)', 'O(log N)', 'O(N)', 'O(N log N)'],
      correctAnswer: 1,
      explanation: 'Because half of the nodes are eliminated at each comparison level, the search time complexity is logarithmic O(log N).'
    },
    {
      id: 'q2',
      type: 'tf',
      topic: 'Binary Search Tree',
      difficulty: 'Medium',
      question: 'True or False: An In-Order Traversal of a Binary Search Tree always yields keys in ascending sorted order.',
      options: ['True', 'False'],
      correctAnswer: 0,
      explanation: 'True! In-Order traversal visits Left Subtree -> Root -> Right Subtree, which processes keys in non-decreasing order.'
    },
    {
      id: 'q3',
      type: 'mcq',
      topic: 'BST Deletion',
      difficulty: 'Hard',
      question: 'When deleting a node with TWO children in a BST, which node can replace the deleted node to maintain BST properties?',
      options: [
        'Root Node',
        'In-Order Successor (Smallest node in right subtree)',
        'Largest node in left subtree only',
        'Any random leaf node'
      ],
      correctAnswer: 1,
      explanation: 'You can replace it with either the In-Order Successor (minimum in right subtree) or In-Order Predecessor (maximum in left subtree).'
    }
  ];

  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState<{ [key: string]: number }>({});
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [score, setScore] = useState(0);

  const currentQ = sampleQuestions[currentIndex];

  const handleOptionSelect = (optionIdx: number) => {
    if (isSubmitted) return;
    setSelectedAnswers(prev => ({ ...prev, [currentQ.id]: optionIdx }));
  };

  const handleSubmitQuiz = () => {
    let totalScore = 0;
    sampleQuestions.forEach((q) => {
      if (selectedAnswers[q.id] === q.correctAnswer) {
        totalScore += 1;
      }
    });
    setScore(totalScore);
    setIsSubmitted(true);
  };

  const handleReset = () => {
    setCurrentIndex(0);
    setSelectedAnswers({});
    setIsSubmitted(false);
    setScore(0);
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
      {/* Quiz Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Award color="var(--accent-amber)" /> Adaptive Practice & AI Quiz Generator
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginTop: '4px' }}>
            AI-generated questions customized for target topic <strong>{profile.currentTopic}</strong> ({profile.level} Level).
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            <Clock size={16} color="var(--accent-cyan)" />
            <span>Time: 02:45</span>
          </div>
          <span className="badge badge-intermediate">
            Adaptive Difficulty: {currentQ.difficulty}
          </span>
        </div>
      </div>

      {!isSubmitted ? (
        /* Active Question Card */
        <div className="glass-panel" style={{
          padding: '32px',
          borderRadius: 'var(--radius-lg)',
          display: 'flex',
          flexDirection: 'column',
          gap: '24px',
          maxWidth: '800px',
          margin: '0 auto',
          width: '100%'
        }}>
          {/* Question Progress Bar */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            <span>Question {currentIndex + 1} of {sampleQuestions.length}</span>
            <span>Topic: {currentQ.topic}</span>
          </div>

          <div style={{
            height: '6px',
            background: 'var(--bg-tertiary)',
            borderRadius: 'var(--radius-full)',
            overflow: 'hidden'
          }}>
            <div style={{
              height: '100%',
              width: `${((currentIndex + 1) / sampleQuestions.length) * 100}%`,
              background: 'var(--accent-gradient)',
              transition: 'var(--transition-smooth)'
            }} />
          </div>

          {/* Question Text */}
          <h3 style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--text-primary)', lineHeight: 1.4 }}>
            {currentQ.question}
          </h3>

          {/* Answer Options */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {currentQ.options?.map((option, idx) => {
              const isSelected = selectedAnswers[currentQ.id] === idx;
              return (
                <button
                  key={idx}
                  onClick={() => handleOptionSelect(idx)}
                  className="glass-panel"
                  style={{
                    padding: '16px 20px',
                    borderRadius: 'var(--radius-md)',
                    textAlign: 'left',
                    fontSize: '0.95rem',
                    fontFamily: 'var(--font-main)',
                    color: isSelected ? '#ffffff' : 'var(--text-primary)',
                    background: isSelected ? 'var(--accent-gradient)' : 'var(--bg-secondary)',
                    border: isSelected ? '1px solid var(--accent-primary)' : '1px solid var(--border-color)',
                    cursor: 'pointer',
                    transition: 'var(--transition-fast)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between'
                  }}
                >
                  <span>{option}</span>
                  {isSelected && <CheckCircle2 size={18} color="#ffffff" />}
                </button>
              );
            })}
          </div>

          {/* Question Navigation Controls */}
          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '16px' }}>
            <button
              disabled={currentIndex === 0}
              onClick={() => setCurrentIndex(prev => prev - 1)}
              className="btn btn-secondary"
              style={{ opacity: currentIndex === 0 ? 0.5 : 1 }}
            >
              Previous
            </button>

            {currentIndex < sampleQuestions.length - 1 ? (
              <button
                onClick={() => setCurrentIndex(prev => prev + 1)}
                className="btn btn-primary"
              >
                <span>Next Question</span>
                <ArrowRight size={16} />
              </button>
            ) : (
              <button
                onClick={handleSubmitQuiz}
                className="btn btn-primary"
                style={{ background: 'linear-gradient(135deg, #10b981 0%, #06b6d4 100%)' }}
              >
                <span>Submit Quiz for AI Evaluation</span>
                <Zap size={16} />
              </button>
            )}
          </div>
        </div>
      ) : (
        /* Quiz Evaluation & Feedback Screen */
        <div className="glass-panel" style={{
          padding: '36px',
          borderRadius: 'var(--radius-lg)',
          display: 'flex',
          flexDirection: 'column',
          gap: '24px',
          maxWidth: '850px',
          margin: '0 auto',
          width: '100%'
        }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{
              width: '64px',
              height: '64px',
              borderRadius: '50%',
              background: 'rgba(16, 185, 129, 0.15)',
              border: '2px solid var(--accent-emerald)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 16px auto'
            }}>
              <Award size={36} color="var(--accent-emerald)" />
            </div>

            <h3 style={{ fontSize: '1.5rem', fontWeight: 700 }}>
              Quiz Evaluation Completed!
            </h3>
            <p style={{ color: 'var(--text-secondary)', marginTop: '4px' }}>
              Your Score: <strong style={{ color: 'var(--accent-cyan)', fontSize: '1.2rem' }}>{score} / {sampleQuestions.length}</strong> ({Math.round((score / sampleQuestions.length) * 100)}%)
            </p>
          </div>

          {/* Detailed Question Explanations */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {sampleQuestions.map((q, idx) => {
              const userAns = selectedAnswers[q.id];
              const isCorrect = userAns === q.correctAnswer;
              return (
                <div
                  key={q.id}
                  style={{
                    padding: '18px',
                    borderRadius: 'var(--radius-md)',
                    background: 'rgba(255, 255, 255, 0.02)',
                    border: isCorrect ? '1px solid rgba(16, 185, 129, 0.3)' : '1px solid rgba(244, 63, 94, 0.3)'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                    {isCorrect ? (
                      <CheckCircle2 size={18} color="var(--accent-emerald)" />
                    ) : (
                      <XCircle size={18} color="var(--accent-rose)" />
                    )}
                    <span style={{ fontWeight: 600, fontSize: '0.95rem' }}>
                      Q{idx + 1}: {q.question}
                    </span>
                  </div>

                  <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginLeft: '26px' }}>
                    <div>Your Answer: <strong>{q.options ? q.options[userAns] || 'Not answered' : 'N/A'}</strong></div>
                    {!isCorrect && (
                      <div style={{ color: 'var(--accent-emerald)', marginTop: '2px' }}>
                        Correct Answer: <strong>{q.options ? q.options[q.correctAnswer as number] : 'N/A'}</strong>
                      </div>
                    )}
                    <div style={{
                      marginTop: '8px',
                      padding: '8px 12px',
                      background: 'rgba(99, 102, 241, 0.08)',
                      borderRadius: 'var(--radius-sm)',
                      color: 'var(--accent-cyan)'
                    }}>
                      💡 <strong>Tutor Explanation:</strong> {q.explanation}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Action Buttons */}
          <div style={{ display: 'flex', justifyContent: 'center', gap: '16px', marginTop: '12px' }}>
            <button onClick={handleReset} className="btn btn-secondary">
              <RotateCcw size={16} />
              <span>Retake Practice Quiz</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
