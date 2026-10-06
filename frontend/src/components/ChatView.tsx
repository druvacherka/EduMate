import React, { useState, useRef, useEffect } from 'react';
import { ChatMessage, StudentProfile } from '../types';
import { sendSocraticChatMessage, logVoiceSession } from '../services/api';
import { 
  Send, 
  Mic, 
  MicOff, 
  Sparkles, 
  RotateCcw, 
  Volume2, 
  BookOpen, 
  HelpCircle, 
  Code, 
  CheckCircle2,
  FileText,
  Lightbulb,
  MessageSquare,
  Loader2,
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
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (textToSend?: string) => {
    const query = textToSend || inputText;
    if (!query.trim() || isLoading) return;

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      sender: 'student',
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMsg]);
    if (!textToSend) setInputText('');
    setIsLoading(true);

    try {
      const res = await sendSocraticChatMessage({
        query,
        level: profile.level,
        language: profile.language,
        conversation_history: messages.map(m => ({ sender: m.sender, text: m.text }))
      });

      const aiMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'tutor',
        text: res.response,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        level: profile.level,
        language: profile.language,
        isAudio: isVoiceActive,
        quickActions: res.quick_actions,
        citations: res.citations?.map(c => ({ document_name: c.document_name, page_number: c.page_number }))
      };

      setMessages(prev => [...prev, aiMsg]);

      // If voice active, log session metadata
      if (isVoiceActive) {
        logVoiceSession({
          language: profile.language,
          topic: profile.currentTopic || query.slice(0, 100),
          duration_seconds: 20,
          transcript_summary: query.slice(0, 100),
        });
      }
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'tutor',
        text: `⚠️ **Connection Error**: ${err.message || 'Unable to connect to the EduMate AI service.'}`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        level: profile.level,
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

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: 'calc(100vh - 56px)',
      width: '100%',
      position: 'relative',
      background: 'var(--bg-primary)'
    }}>
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
            <p style={{ maxWidth: '520px', fontSize: '0.9rem', lineHeight: 1.6, color: 'var(--text-muted)', marginBottom: '20px' }}>
              Ask a question to begin an interactive Socratic tutoring session.
            </p>
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
                <span className="badge badge-beginner" style={{ fontSize: '0.65rem' }}>
                  {msg.level}
                </span>
              )}
              {msg.isAudio && (
                <span style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--accent-cyan)' }}>
                  <Volume2 size={12} /> Voice Output
                </span>
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
