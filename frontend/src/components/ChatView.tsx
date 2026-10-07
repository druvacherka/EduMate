import React, { useState, useRef, useEffect, useCallback } from 'react';
import { ChatMessage, LearningLevel, Language, StudentProfile } from '../types';
import { sendSocraticChatMessage, logVoiceSession } from '../services/api';
import { 
  Send, 
  Mic, 
  MicOff, 
  Sparkles, 
  Volume2, 
  VolumeX,
  Code, 
  CheckCircle2,
  FileText,
  HelpCircle,
  Lightbulb,
  Loader2,
  Layers,
  GraduationCap,
  Zap,
} from 'lucide-react';

interface ChatViewProps {
  profile: StudentProfile;
  isVoiceActive: boolean;
}

export const ChatView: React.FC<ChatViewProps> = ({ profile, isVoiceActive }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [speechTranscript, setSpeechTranscript] = useState('');
  
  // Pedagogical Mode: Beginner, Intermediate, Advanced
  const [selectedMode, setSelectedMode] = useState<LearningLevel>(
    (profile.level as LearningLevel) || 'Beginner'
  );

  // Audio Playback State
  const [activeAudioMessageId, setActiveAudioMessageId] = useState<string | null>(null);
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<any>(null);

  // Keep selected mode in sync with profile if profile updates
  useEffect(() => {
    if (profile.level && ['Beginner', 'Intermediate', 'Advanced'].includes(profile.level)) {
      setSelectedMode(profile.level as LearningLevel);
    }
  }, [profile.level]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Clean raw markdown and KaTeX blocks for clear, natural speech output
  const cleanTextForSpeech = useCallback((raw: string): string => {
    return raw
      .replace(/\$\$.*?\$\$/gs, ' mathematical equation ')
      .replace(/\$.*?\$/g, ' formula ')
      .replace(/```[\s\S]*?```/g, ' code snippet provided in explanation. ')
      .replace(/`([^`]+)`/g, '$1')
      .replace(/[*#_~>]/g, '')
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
      .replace(/\n+/g, ' ')
      .trim();
  }, []);

  // Text-To-Speech (Audio Output) Engine
  const stopAudio = useCallback(() => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
    setActiveAudioMessageId(null);
    setIsPlayingAudio(false);
  }, []);

  const playAudioForText = useCallback((text: string, language?: string, messageId?: string) => {
    if (!('speechSynthesis' in window)) {
      console.warn('Speech synthesis not supported in this browser.');
      return;
    }

    // Stop existing audio if playing
    window.speechSynthesis.cancel();

    const spokenText = cleanTextForSpeech(text);
    if (!spokenText) return;

    const utterance = new SpeechSynthesisUtterance(spokenText);
    
    // Select language
    const lang = language || profile.language || 'English';
    if (lang === 'Telugu') {
      utterance.lang = 'te-IN';
    } else if (lang === 'Hindi') {
      utterance.lang = 'hi-IN';
    } else {
      utterance.lang = 'en-US';
    }

    // Attempt to match installed voice for target language
    const voices = window.speechSynthesis.getVoices();
    const matchedVoice = voices.find(v => v.lang.toLowerCase().startsWith(utterance.lang.toLowerCase().slice(0, 2)));
    if (matchedVoice) {
      utterance.voice = matchedVoice;
    }

    utterance.rate = 1.0;
    utterance.pitch = 1.0;

    utterance.onstart = () => {
      setIsPlayingAudio(true);
      if (messageId) setActiveAudioMessageId(messageId);
    };

    utterance.onend = () => {
      setIsPlayingAudio(false);
      setActiveAudioMessageId(null);
    };

    utterance.onerror = (e) => {
      console.warn('Speech synthesis error:', e);
      setIsPlayingAudio(false);
      setActiveAudioMessageId(null);
    };

    window.speechSynthesis.speak(utterance);

    // Record voice activity
    logVoiceSession({
      language: lang,
      topic: profile.currentTopic || text.slice(0, 100),
      duration_seconds: Math.max(10, Math.round(spokenText.split(' ').length / 2.5)),
      transcript_summary: text.slice(0, 100),
    });
  }, [cleanTextForSpeech, profile.language, profile.currentTopic]);

  // Clean up audio synthesis on unmount
  useEffect(() => {
    return () => {
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  const handleSend = async (textToSend?: string) => {
    const query = textToSend || inputText;
    if (!query.trim() || isLoading) return;

    // Stop current audio before sending new query
    stopAudio();

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      sender: 'student',
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      level: selectedMode,
    };

    setMessages(prev => [...prev, userMsg]);
    if (!textToSend) setInputText('');
    setIsLoading(true);

    try {
      // Pass selected mode (Beginner, Intermediate, Advanced) directly to backend & Gemini
      const res = await sendSocraticChatMessage({
        query,
        level: selectedMode,
        language: profile.language || 'English',
        conversation_history: messages.map(m => ({ sender: m.sender, text: m.text })),
      });

      const aiMsgId = (Date.now() + 1).toString();
      const aiMsg: ChatMessage = {
        id: aiMsgId,
        sender: 'tutor',
        text: res.response,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        level: (res.level as LearningLevel) || selectedMode,
        language: (res.language as Language) || profile.language,
        isAudio: isVoiceActive,
        quickActions: res.quick_actions,
      };

      setMessages(prev => [...prev, aiMsg]);

      // If voice output is enabled (Voice ON), automatically play audio speech
      if (isVoiceActive) {
        playAudioForText(res.response, res.language || profile.language, aiMsgId);
      }
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'tutor',
        text: `⚠️ **Connection Error**: ${err.message || 'Unable to connect to the EduMate AI service.'}`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        level: selectedMode,
        language: profile.language,
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleRecording = () => {
    if (isRecording) {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      setIsRecording(false);
      setSpeechTranscript('');
      return;
    }

    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setSpeechTranscript('Web Speech API is not supported in this browser. Please type your query.');
      setTimeout(() => setSpeechTranscript(''), 3000);
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = profile.language === 'Telugu' ? 'te-IN' : profile.language === 'Hindi' ? 'hi-IN' : 'en-US';

      recognition.onstart = () => {
        setIsRecording(true);
        setSpeechTranscript('Listening to your speech...');
      };

      recognition.onresult = (event: any) => {
        const transcript = Array.from(event.results)
          .map((result: any) => result[0].transcript)
          .join('');
        setSpeechTranscript(transcript);
        setInputText(transcript);
      };

      recognition.onerror = (event: any) => {
        console.warn('Speech recognition error:', event.error);
        setIsRecording(false);
        setSpeechTranscript(`Microphone error: ${event.error}`);
        setTimeout(() => setSpeechTranscript(''), 3000);
      };

      recognition.onend = () => {
        setIsRecording(false);
        setSpeechTranscript('');
      };

      recognitionRef.current = recognition;
      recognition.start();
    } catch (err: any) {
      console.error('Failed to start speech recognition:', err);
      setIsRecording(false);
      setSpeechTranscript('Could not access microphone.');
      setTimeout(() => setSpeechTranscript(''), 3000);
    }
  };

  const modeDescriptions: Record<LearningLevel, { badge: string; icon: any; summary: string }> = {
    Beginner: {
      badge: '🌱 Beginner',
      icon: Layers,
      summary: 'Relatable analogies, foundational concepts & gentle step-by-step guidance',
    },
    Intermediate: {
      badge: '⚡ Intermediate',
      icon: Zap,
      summary: 'Technical precision, Big-O complexity, code examples & problem trade-offs',
    },
    Advanced: {
      badge: '🚀 Advanced',
      icon: GraduationCap,
      summary: 'Formal rigor, mathematical proofs, edge cases & deep architectural analysis',
    },
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: 'calc(100vh - 56px)',
      width: '100%',
      position: 'relative',
      background: 'var(--bg-primary)'
    }}>
      {/* Pedagogical Mode & Audio Bar */}
      <div style={{
        padding: '10px 20px',
        backgroundColor: 'var(--bg-secondary)',
        borderBottom: '1px solid var(--border-color)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '10px',
        zIndex: 10,
      }}>
        {/* Left: Interactive Mode Pills */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginRight: '4px' }}>
            Tutor Mode:
          </span>
          {(['Beginner', 'Intermediate', 'Advanced'] as LearningLevel[]).map((mode) => {
            const isSelected = selectedMode === mode;
            const meta = modeDescriptions[mode];
            const Icon = meta.icon;
            const badgeColor = mode === 'Beginner' ? '#10b981' : mode === 'Intermediate' ? '#3b82f6' : '#a855f7';
            const badgeBg = mode === 'Beginner' 
              ? 'rgba(16, 185, 129, 0.16)' 
              : mode === 'Intermediate' 
              ? 'rgba(59, 130, 246, 0.16)' 
              : 'rgba(168, 85, 247, 0.16)';

            return (
              <button
                key={mode}
                onClick={() => setSelectedMode(mode)}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '5px 12px',
                  borderRadius: 'var(--radius-full)',
                  fontSize: '0.78rem',
                  fontWeight: isSelected ? 600 : 500,
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  border: isSelected ? `1.5px solid ${badgeColor}` : '1px solid var(--border-color)',
                  background: isSelected ? badgeBg : 'var(--bg-tertiary)',
                  color: isSelected ? badgeColor : 'var(--text-secondary)',
                  boxShadow: isSelected ? `0 0 10px ${badgeBg}` : 'none',
                }}
                title={meta.summary}
              >
                <Icon size={13} />
                <span>{mode}</span>
              </button>
            );
          })}
        </div>

        {/* Right: Active Mode Summary & Audio Status */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
          <div style={{ fontSize: '0.76rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ color: 'var(--text-secondary)' }}>Strategy:</span>
            <span>{modeDescriptions[selectedMode].summary}</span>
          </div>
          {isPlayingAudio && (
            <button
              onClick={stopAudio}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '5px',
                padding: '4px 10px',
                borderRadius: 'var(--radius-full)',
                background: 'rgba(239, 68, 68, 0.15)',
                border: '1px solid rgba(239, 68, 68, 0.4)',
                color: '#f87171',
                fontSize: '0.74rem',
                cursor: 'pointer',
                fontWeight: 600,
              }}
              title="Stop audio playback"
            >
              <VolumeX size={12} />
              <span>Stop Audio</span>
            </button>
          )}
        </div>
      </div>

      {/* Message Feed */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '24px',
        display: 'flex',
        flexDirection: 'column',
        gap: '20px'
      }}>
        {messages.length === 0 ? (
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            height: '100%',
            textAlign: 'center',
            padding: '40px 20px',
            color: 'var(--text-secondary)'
          }}>
            <div style={{
              width: '64px',
              height: '64px',
              borderRadius: 'var(--radius-xl)',
              background: 'rgba(99, 102, 241, 0.1)',
              border: '1px solid var(--border-color-glow)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '16px',
              color: 'var(--accent-primary)'
            }}>
              <Sparkles size={32} />
            </div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '8px' }}>
              Welcome to EduMate AI Tutor
            </h3>
            <p style={{ maxWidth: '520px', fontSize: '0.9rem', lineHeight: 1.6, color: 'var(--text-muted)', marginBottom: '12px' }}>
              Ask a question to begin an interactive Socratic tutoring session in <strong>{selectedMode}</strong> mode.
            </p>
            <div style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              padding: '6px 14px',
              borderRadius: 'var(--radius-md)',
              background: 'var(--bg-secondary)',
              border: '1px solid var(--border-color)',
              fontSize: '0.78rem',
              color: 'var(--text-secondary)'
            }}>
              <span>Active Mode:</span>
              <strong style={{ color: 'var(--accent-primary)' }}>{selectedMode}</strong>
              <span>• Voice Audio:</span>
              <strong style={{ color: isVoiceActive ? '#34d399' : 'var(--text-muted)' }}>
                {isVoiceActive ? 'Auto-speak ON' : 'Manual Listen Only'}
              </strong>
            </div>
          </div>
        ) : (
          messages.map((msg) => (
          <div
            key={msg.id}
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: msg.sender === 'student' ? 'flex-end' : 'flex-start',
              maxWidth: '85%',
              alignSelf: msg.sender === 'student' ? 'flex-end' : 'flex-start'
            }}
          >
            {/* Sender Metadata */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              marginBottom: '6px',
              fontSize: '0.75rem',
              color: 'var(--text-muted)'
            }}>
              <span style={{ fontWeight: 600, color: msg.sender === 'tutor' ? 'var(--accent-primary)' : 'var(--text-secondary)' }}>
                {msg.sender === 'tutor' ? 'EduMate Tutor' : 'You (Student)'}
              </span>
              <span>•</span>
              <span>{msg.timestamp}</span>
              {msg.level && (
                <span 
                  className={`badge badge-${msg.level.toLowerCase()}`} 
                  style={{ fontSize: '0.65rem', textTransform: 'capitalize' }}
                >
                  {msg.level}
                </span>
              )}
              {msg.isAudio && (
                <span style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--accent-cyan)' }}>
                  <Volume2 size={12} /> Voice
                </span>
              )}

              {/* Message Audio Player Button for Tutor Responses */}
              {msg.sender === 'tutor' && (
                <button
                  onClick={() => {
                    if (activeAudioMessageId === msg.id && isPlayingAudio) {
                      stopAudio();
                    } else {
                      playAudioForText(msg.text, msg.language || profile.language, msg.id);
                    }
                  }}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '4px',
                    marginLeft: '4px',
                    padding: '2px 8px',
                    borderRadius: 'var(--radius-full)',
                    fontSize: '0.7rem',
                    cursor: 'pointer',
                    fontWeight: 600,
                    transition: 'all 0.2s ease',
                    border: activeAudioMessageId === msg.id && isPlayingAudio 
                      ? '1px solid rgba(239, 68, 68, 0.4)' 
                      : '1px solid rgba(59, 130, 246, 0.3)',
                    background: activeAudioMessageId === msg.id && isPlayingAudio 
                      ? 'rgba(239, 68, 68, 0.15)' 
                      : 'rgba(59, 130, 246, 0.12)',
                    color: activeAudioMessageId === msg.id && isPlayingAudio ? '#f87171' : '#60a5fa',
                  }}
                  title={activeAudioMessageId === msg.id && isPlayingAudio ? 'Stop reading' : 'Listen to this explanation'}
                >
                  {activeAudioMessageId === msg.id && isPlayingAudio ? (
                    <>
                      <VolumeX size={11} />
                      <span>Stop</span>
                    </>
                  ) : (
                    <>
                      <Volume2 size={11} />
                      <span>Listen</span>
                    </>
                  )}
                </button>
              )}
            </div>

            {/* Message Card */}
            <div style={{
              padding: '16px 20px',
              borderRadius: msg.sender === 'student' ? '12px 12px 2px 12px' : '12px 12px 12px 2px',
              background: msg.sender === 'student' 
                ? '#1d4ed8' 
                : 'var(--bg-secondary)',
              color: msg.sender === 'student' ? '#ffffff' : 'var(--text-primary)',
              boxShadow: 'var(--shadow-card)',
              border: msg.sender === 'student' ? 'none' : '1px solid var(--border-color)',
              lineHeight: 1.6
            }}>
              {/* Main Text Content */}
              <div style={{ whiteSpace: 'pre-line', fontSize: '0.92rem' }}>
                {msg.text}
              </div>

              {/* Active Audio Waveform Indicator */}
              {activeAudioMessageId === msg.id && isPlayingAudio && (
                <div style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '8px',
                  marginTop: '12px',
                  padding: '6px 12px',
                  background: 'rgba(59, 130, 246, 0.12)',
                  border: '1px solid rgba(59, 130, 246, 0.3)',
                  borderRadius: 'var(--radius-md)',
                  fontSize: '0.76rem',
                  color: '#93c5fd',
                }}>
                  <Volume2 size={14} className="pulse-active" />
                  <span>Speaking in {msg.language || profile.language || 'English'} ({msg.level || selectedMode} mode)...</span>
                </div>
              )}

              {/* Formula Block preview if present */}
              {msg.formula && (
                <div style={{
                  margin: '12px 0',
                  padding: '10px 14px',
                  background: 'rgba(37, 99, 235, 0.08)',
                  borderLeft: '3px solid var(--accent-primary)',
                  borderRadius: 'var(--radius-sm)',
                  fontFamily: 'var(--font-mono)',
                  fontSize: '0.88rem',
                  color: '#60a5fa'
                }}>
                  {`$$\\mathbf{Complexity:}\\ ${msg.formula}$$`}
                </div>
              )}

              {/* Code Snippet preview if present */}
              {msg.codeSnippet && (
                <div style={{
                  margin: '12px 0',
                  borderRadius: 'var(--radius-md)',
                  overflow: 'hidden',
                  border: '1px solid var(--border-color)'
                }}>
                  <div style={{
                    background: 'var(--bg-tertiary)',
                    padding: '6px 12px',
                    fontSize: '0.75rem',
                    fontFamily: 'var(--font-mono)',
                    color: 'var(--text-secondary)',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                  }}>
                    <span>{msg.codeSnippet.language.toUpperCase()}</span>
                    <Code size={14} />
                  </div>
                  <pre style={{
                    background: '#0d1117',
                    padding: '12px 16px',
                    fontFamily: 'var(--font-mono)',
                    fontSize: '0.85rem',
                    color: '#e6edf3',
                    overflowX: 'auto'
                  }}>
                    <code>{msg.codeSnippet.code}</code>
                  </pre>
                </div>
              )}

              {/* RAG Document Grounding Attribution Card */}
              {msg.documentRef && (
                <div style={{
                  marginTop: '12px',
                  padding: '8px 12px',
                  background: 'rgba(16, 185, 129, 0.08)',
                  border: '1px solid rgba(16, 185, 129, 0.25)',
                  borderRadius: 'var(--radius-sm)',
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '8px',
                  fontSize: '0.8rem',
                  color: 'var(--accent-emerald)'
                }}>
                  <FileText size={16} style={{ flexShrink: 0, marginTop: '2px' }} />
                  <div>
                    <div style={{ fontWeight: 600 }}>
                      Grounded in uploaded material: {msg.documentRef.name} (Page {msg.documentRef.page})
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontStyle: 'italic' }}>
                      "{msg.documentRef.snippet}"
                    </div>
                  </div>
                </div>
              )}

              {/* Verified Study Material Grounding Citations */}
              {msg.citations && msg.citations.length > 0 && (
                <div style={{
                  marginTop: '12px',
                  padding: '10px 14px',
                  background: 'rgba(16, 185, 129, 0.08)',
                  border: '1px solid rgba(16, 185, 129, 0.25)',
                  borderRadius: 'var(--radius-sm)',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '6px',
                  fontSize: '0.8rem',
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--accent-emerald)', fontWeight: 600 }}>
                    <CheckCircle2 size={15} />
                    <span>Verified Study Material Citations ({msg.citations.length})</span>
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '4px' }}>
                    {msg.citations.map((cit, idx) => (
                      <span
                        key={idx}
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '5px',
                          background: 'rgba(16, 185, 129, 0.15)',
                          border: '1px solid rgba(16, 185, 129, 0.35)',
                          borderRadius: 'var(--radius-full)',
                          padding: '3px 10px',
                          fontSize: '0.75rem',
                          color: 'var(--accent-emerald)',
                        }}
                      >
                        <FileText size={12} />
                        {cit.document_name} • Page {cit.page_number}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Ungrounded Fallback Alert */}
              {msg.text.includes("Information not found in study material") && (
                <div style={{
                  marginTop: '12px',
                  padding: '8px 12px',
                  background: 'rgba(239, 68, 68, 0.08)',
                  border: '1px solid rgba(239, 68, 68, 0.25)',
                  borderRadius: 'var(--radius-sm)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  fontSize: '0.8rem',
                  color: 'var(--accent-rose)',
                }}>
                  <HelpCircle size={16} />
                  <span>Document Grounding Alert: Topic not found in uploaded study material.</span>
                </div>
              )}
            </div>

            {/* Socratic Quick Action Chips */}
            {!!msg.quickActions?.length && msg.sender === 'tutor' && (
              <div style={{ display: 'flex', gap: '8px', marginTop: '10px', flexWrap: 'wrap' }}>
                {msg.quickActions.map((action, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSend(action)}
                    style={{
                      padding: '5px 12px',
                      fontSize: '0.74rem',
                      borderRadius: 'var(--radius-md)',
                      border: '1px solid var(--border-color)',
                      background: 'var(--bg-tertiary)',
                      color: '#60a5fa',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                      fontWeight: 500,
                      transition: 'var(--transition-fast)'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'var(--bg-card-hover)'}
                    onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'var(--bg-tertiary)'}
                  >
                    <Lightbulb size={12} />
                    <span>{action}</span>
                  </button>
                ))}
              </div>
            )}
          </div>
        ))
        )}
        {isLoading && (
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            padding: '8px 16px',
            borderRadius: 'var(--radius-full)',
            background: 'var(--bg-secondary)',
            border: '1px solid var(--border-color)',
            fontSize: '0.8rem',
            color: 'var(--text-muted)',
            alignSelf: 'flex-start'
          }}>
            <Loader2 size={14} className="spin-slow" color="var(--accent-primary)" />
            <span>EduMate is formulating your Socratic response...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Speech Audio Recording Banner overlay */}
      {isRecording && (
        <div style={{
          position: 'absolute',
          bottom: '80px',
          left: '50%',
          transform: 'translateX(-50%)',
          background: 'rgba(17, 24, 39, 0.95)',
          border: '1px solid var(--accent-primary)',
          boxShadow: 'var(--accent-glow)',
          padding: '12px 24px',
          borderRadius: 'var(--radius-full)',
          display: 'flex',
          alignItems: 'center',
          gap: '16px',
          zIndex: 20
        }}>
          <div className="pulse-active" style={{
            width: '14px',
            height: '14px',
            borderRadius: '50%',
            background: 'var(--accent-rose)'
          }} />
          <span style={{ fontSize: '0.9rem', color: 'var(--text-primary)', fontWeight: 500 }}>
            {speechTranscript}
          </span>
          <button onClick={toggleRecording} className="btn btn-ghost" style={{ padding: '4px' }}>
            <MicOff size={18} color="var(--accent-rose)" />
          </button>
        </div>
      )}

      {/* Multimodal Input Toolbar */}
      <div style={{
        padding: '12px 20px',
        backgroundColor: 'var(--bg-sidebar)',
        borderTop: '1px solid var(--border-color)',
        display: 'flex',
        alignItems: 'center',
        gap: '10px'
      }}>
        {/* Voice Speech Microphone Button */}
        <button
          onClick={toggleRecording}
          style={{
            width: '40px',
            height: '40px',
            borderRadius: 'var(--radius-md)',
            padding: 0,
            border: isRecording ? '1px solid var(--accent-rose)' : '1px solid var(--border-color)',
            background: isRecording ? 'rgba(244, 63, 94, 0.15)' : 'var(--bg-secondary)',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'var(--transition-fast)'
          }}
          title="Speak your question using Voice STT"
        >
          <Mic size={18} color={isRecording ? 'var(--accent-rose)' : '#60a5fa'} />
        </button>

        {/* Text Input Box */}
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder={`Ask EduMate a question or ask to explain in ${profile.language}...`}
          style={{
            flex: 1,
            background: 'var(--bg-secondary)',
            color: 'var(--text-primary)',
            border: '1px solid var(--border-color)',
            padding: '10px 14px',
            borderRadius: 'var(--radius-md)',
            fontSize: '0.88rem',
            fontFamily: 'var(--font-main)',
            outline: 'none'
          }}
          onFocus={(e) => e.currentTarget.style.borderColor = 'var(--accent-primary)'}
          onBlur={(e) => e.currentTarget.style.borderColor = 'var(--border-color)'}
        />

        {/* Send Button */}
        <button
          onClick={() => handleSend()}
          style={{
            width: '40px',
            height: '40px',
            borderRadius: 'var(--radius-md)',
            border: 'none',
            background: '#2563eb',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#ffffff',
            transition: 'var(--transition-fast)'
          }}
          onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#1d4ed8'}
          onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#2563eb'}
          title="Send Question"
        >
          <Send size={16} />
        </button>
      </div>
    </div>
  );
};
