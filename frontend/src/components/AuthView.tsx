import React, { useState } from 'react';
import { authenticateAccount } from '../services/api';

interface AuthViewProps {
  onAuthenticated: () => void;
}

export const AuthView: React.FC<AuthViewProps> = ({ onAuthenticated }) => {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      await authenticateAccount(mode, email, password);
      onAuthenticated();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to authenticate.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="auth-page">
      <div className="auth-shell">
        <aside className="auth-hero">
          <div className="brand-row">
            <div className="brand-mark" aria-label="EduMate logo">
              <img src="/favicon.svg" alt="EduMate logo" />
            </div>
            <div>
              <span className="eyebrow">AI Learning Companion</span>
              <h1>EduMate</h1>
            </div>
          </div>

          <p className="hero-copy">
            Turn study time into steady progress with adaptive guidance, practice, and revision built around how you learn.
          </p>

          <ul className="feature-list">
            <li>Personalised study plans</li>
            <li>Smarter revision loops</li>
            <li>Practice quizzes and topic insights</li>
          </ul>
        </aside>

        <section className="auth-card">
          <div className="auth-header">
            <div className="brand-row brand-row-small">
              <div className="brand-mark brand-mark-small" aria-label="EduMate logo">
                <img src="/favicon.svg" alt="EduMate logo" />
              </div>
              <div>
                <span className="eyebrow">Welcome</span>
                <h2>{mode === 'login' ? 'Welcome back' : 'Create your account'}</h2>
              </div>
            </div>
            <p>
              {mode === 'login'
                ? 'Sign in to continue your learning journey.'
                : 'Start your personalised learning journey with EduMate.'}
            </p>
          </div>

          <form className="auth-form" onSubmit={handleSubmit}>
            <label className="auth-field">
              <span>Email address</span>
              <input
                className="auth-input"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(event) => setEmail(event.target.value)}
              />
            </label>

            <label className="auth-field">
              <span>Password {mode === 'register' && '(12+ characters)'}</span>
              <input
                className="auth-input"
                type="password"
                autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
                minLength={mode === 'register' ? 12 : undefined}
                required
                value={password}
                onChange={(event) => setPassword(event.target.value)}
              />
            </label>

            {error && (
              <div className="auth-error" role="alert">
                {error}
              </div>
            )}

            <button className="btn btn-primary auth-submit" type="submit" disabled={submitting}>
              {submitting ? 'Please wait...' : mode === 'login' ? 'Sign in' : 'Create account'}
            </button>
          </form>

          <button
            type="button"
            className="auth-toggle"
            onClick={() => {
              setError('');
              setMode(mode === 'login' ? 'register' : 'login');
            }}
          >
            {mode === 'login' ? 'Need an account? Create one' : 'Already registered? Sign in'}
          </button>
        </section>
      </div>
    </main>
  );
};
