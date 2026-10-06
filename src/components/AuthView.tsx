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
    <main style={{ minHeight: '100vh', display: 'grid', placeItems: 'center', background: 'var(--bg-primary)', padding: 24 }}>
      <form onSubmit={handleSubmit} style={{ width: '100%', maxWidth: 420, padding: 32, borderRadius: 16, background: 'var(--bg-secondary)', border: '1px solid var(--border-color)' }}>
        <h1 style={{ color: 'var(--text-primary)', margin: '0 0 8px' }}>EduMate</h1>
        <p style={{ color: 'var(--text-secondary)', margin: '0 0 24px' }}>
          {mode === 'login' ? 'Sign in to your learning account.' : 'Create an account to get started.'}
        </p>
        <label style={{ display: 'block', color: 'var(--text-secondary)', marginBottom: 14 }}>
          Email
          <input
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            style={{ boxSizing: 'border-box', display: 'block', width: '100%', marginTop: 6, padding: 10 }}
          />
        </label>
        <label style={{ display: 'block', color: 'var(--text-secondary)', marginBottom: 16 }}>
          Password {mode === 'register' && '(at least 12 characters)'}
          <input
            type="password"
            autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
            minLength={mode === 'register' ? 12 : undefined}
            required
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            style={{ boxSizing: 'border-box', display: 'block', width: '100%', marginTop: 6, padding: 10 }}
          />
        </label>
        {error && <p role="alert" style={{ color: '#f87171' }}>{error}</p>}
        <button className="btn-primary" type="submit" disabled={submitting} style={{ width: '100%', padding: 11 }}>
          {submitting ? 'Please wait...' : mode === 'login' ? 'Sign in' : 'Create account'}
        </button>
        <button
          type="button"
          onClick={() => { setError(''); setMode(mode === 'login' ? 'register' : 'login'); }}
          style={{ display: 'block', margin: '16px auto 0', background: 'none', border: 0, color: 'var(--text-secondary)', cursor: 'pointer' }}
        >
          {mode === 'login' ? 'Need an account? Create one' : 'Already registered? Sign in'}
        </button>
      </form>
    </main>
  );
};
