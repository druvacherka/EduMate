import React, { useState, useRef, useEffect } from 'react';
import { ChatMessage, StudentProfile } from '../types';
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
  Lightbulb
} from 'lucide-react';

interface ChatViewProps {
  profile: StudentProfile;
  isVoiceActive: boolean;
}

export const ChatView: React.FC<ChatViewProps> = ({ profile, isVoiceActive }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      sender: 'tutor',
      text: `Hello ${profile.name}! I'm EduMate, your AI Personal Tutor. We are currently focusing on **${profile.currentSubject}** (${profile.currentTopic}).\n\nHow would you like to start today? You can ask a question, request a step-by-step concept breakdown, or ask me to explain based on your uploaded notes!`,
      timestamp: '10:00 AM',
      level: profile.level,
      language: profile.language,
      quickActions: ['Explain BST Fundamentals', 'Give a real-world analogy', 'Test me with a problem']
    },
    {
      id: '2',
      sender: 'student',
      text: 'What is a Binary Search Tree (BST) and why is the left child always smaller?',
      timestamp: '10:01 AM'
    },
    {
      id: '3',
      sender: 'tutor',
      text: `Great question! Let's understand **Binary Search Trees (BST)** step-by-step for the **${profile.level}** level.\n\n### 💡 Core Concept\nA Binary Search Tree is a hierarchical node structure where every node follows one strict ordering rule:\n- **Left Subtree Rule**: Every value in the left subtree is strictly **smaller** than the root value.\n- **Right Subtree Rule**: Every value in the right subtree is strictly **greater** than the root value.\n\n### 🏢 Real-World Analogy\nThink of a dictionary! If you look for words starting with **"M"**, and you open a page at **"P"**, you immediately know that "M" must be in the **left half** of the book. You can ignore the entire right half! That is why search operation takes $O(\\log N)$ time on average.`,
      timestamp: '10:01 AM',
      level: profile.level,
      language: profile.language,
      isAudio: true,
      formula: 'T(n) = T(n/2) + O(1) \\implies O(\\log n)',
      codeSnippet: {
        language: 'cpp',
        code: `struct Node {\n    int data;\n    Node* left;\n    Node* right;\n    Node(int val) : data(val), left(nullptr), right(nullptr) {}\n};`
      },
      documentRef: {
        name: 'Data_Structures_Unit3_Trees.pdf',
        page: 14,
        snippet: 'A BST satisfies the binary-search property: let x be a node. If y is in left subtree of x, then y.key <= x.key.'
      },
      quickActions: ['Explain simpler', 'Show BST Insertion Example', 'Give me a practice quiz']
    }
  ]);

  const [inputText, setInputText] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [speechTranscript, setSpeechTranscript] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = (textToSend?: string) => {
    const query = textToSend || inputText;
    if (!query.trim()) return;

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      sender: 'student',
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMsg]);
    if (!textToSend) setInputText('');

    // Simulate Socratic AI Tutor Response
    setTimeout(() => {
      let aiResponseText = '';
      let codeSnippet;
      let formula;

      if (query.toLowerCase().includes('simpler') || query.toLowerCase().includes('easy')) {
        aiResponseText = `Here is a **simpler view**:\n\nImagine a line of students arranged by height. The teacher stands in the middle. Everyone shorter goes to the left line, and everyone taller goes to the right line!\n\nIf you want to find a student, you only look at one line. That halves your work every step!`;
      } else if (query.toLowerCase().includes('quiz') || query.toLowerCase().includes('test')) {
        aiResponseText = `Awesome! Let's test your understanding:\n\n**Question**: If we insert values \`[50, 30, 70, 20, 40]\` into an empty BST, which node becomes the right child of 30?`;
      } else {
        aiResponseText = `I understand you're asking about **"${query}"**.\n\nConsidering your level (**${profile.level}**) and target language (**${profile.language}**), let's break this down:\n1. **Fundamental Rule**: We maintain sorted structure upon insertion.\n2. **Key Advantage**: Searching takes logarithmic time $O(\\log N)$.\n\nWould you like an example problem or a step-by-step code demonstration?`;
      }

      const aiMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'tutor',
        text: aiResponseText,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        level: profile.level,
        language: profile.language,
        isAudio: isVoiceActive,
        quickActions: ['Explain simpler', 'Give another example', 'Test me with a quiz']
      };

      setMessages(prev => [...prev, aiMsg]);
    }, 800);
  };

  const toggleRecording = () => {
    if (!isRecording) {
      setIsRecording(true);
      setSpeechTranscript('Listening to your speech...');
      const speechSimulation = setTimeout(() => {
        setSpeechTranscript('Explain BST deletion step by step');
        setIsRecording(false);
        handleSend('Explain BST deletion step by step');
      }, 3000);
    } else {
      setIsRecording(false);
      setSpeechTranscript('');
    }
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: 'calc(100vh - 70px)',
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
        {messages.map((msg) => (
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
            <div className="glass-panel" style={{
              padding: '18px 22px',
              borderRadius: msg.sender === 'student' ? '20px 20px 4px 20px' : '20px 20px 20px 4px',
              background: msg.sender === 'student' 
                ? 'var(--accent-gradient)' 
                : 'var(--bg-secondary)',
              color: msg.sender === 'student' ? '#ffffff' : 'var(--text-primary)',
              boxShadow: 'var(--shadow-card)',
              border: msg.sender === 'student' ? 'none' : '1px solid var(--border-color)',
              lineHeight: 1.6
            }}>
              {/* Main Text Content */}
              <div style={{ whiteSpace: 'pre-line', fontSize: '0.95rem' }}>
                {msg.text}
              </div>

              {/* Formula Block preview if present */}
              {msg.formula && (
                <div style={{
                  margin: '12px 0',
                  padding: '10px 14px',
                  background: 'rgba(99, 102, 241, 0.1)',
                  borderLeft: '3px solid var(--accent-primary)',
                  borderRadius: 'var(--radius-sm)',
                  fontFamily: 'var(--font-mono)',
                  fontSize: '0.9rem',
                  color: 'var(--accent-cyan)'
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
            </div>

            {/* Socratic Quick Action Chips */}
            {msg.quickActions && msg.sender === 'tutor' && (
              <div style={{ display: 'flex', gap: '8px', marginTop: '10px', flexWrap: 'wrap' }}>
                {msg.quickActions.map((action, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSend(action)}
                    className="btn btn-ghost"
                    style={{
                      padding: '4px 12px',
                      fontSize: '0.75rem',
                      borderRadius: 'var(--radius-full)',
                      border: '1px solid var(--border-color-glow)',
                      background: 'rgba(99, 102, 241, 0.06)',
                      color: 'var(--accent-primary)'
                    }}
                  >
                    <Lightbulb size={12} />
                    <span>{action}</span>
                  </button>
                ))}
              </div>
            )}
          </div>
        ))}
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
      <div className="glass-panel" style={{
        padding: '16px 24px',
        borderTop: '1px solid var(--border-color)',
        display: 'flex',
        alignItems: 'center',
        gap: '12px'
      }}>
        {/* Voice Speech Microphone Button */}
        <button
          onClick={toggleRecording}
          className={`btn ${isRecording ? 'btn-primary pulse-active' : 'btn-secondary'}`}
          style={{
            width: '46px',
            height: '46px',
            borderRadius: 'var(--radius-full)',
            padding: 0,
            background: isRecording ? 'var(--accent-rose)' : 'var(--bg-tertiary)'
          }}
          title="Speak your question using Voice STT"
        >
          <Mic size={20} color={isRecording ? '#ffffff' : 'var(--accent-primary)'} />
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
            background: 'var(--bg-tertiary)',
            color: 'var(--text-primary)',
            border: '1px solid var(--border-color)',
            padding: '12px 18px',
            borderRadius: 'var(--radius-lg)',
            fontSize: '0.95rem',
            fontFamily: 'var(--font-main)',
            outline: 'none'
          }}
        />

        {/* Send Button */}
        <button
          onClick={() => handleSend()}
          className="btn btn-primary"
          style={{
            width: '46px',
            height: '46px',
            borderRadius: 'var(--radius-full)',
            padding: 0
          }}
          title="Send Question"
        >
          <Send size={18} color="#ffffff" />
        </button>
      </div>
    </div>
  );
};
