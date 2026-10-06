import React, { useState, useEffect, useRef } from 'react';
import { StudyDocument, StudentProfile } from '../types';
import {
  fetchStudyMaterials,
  uploadStudyDocument,
  deleteStudyDocument,
  performRagSearch,
  RagSearchAnswer,
} from '../services/api';
import { 
  UploadCloud, 
  FileText, 
  CheckCircle2, 
  Trash2, 
  Eye, 
  Database, 
  Layers, 
  Search,
  Sparkles,
  AlertCircle,
  Loader2
} from 'lucide-react';

interface StudyMaterialViewProps {
  profile: StudentProfile;
}

export const StudyMaterialView: React.FC<StudyMaterialViewProps> = ({ profile }) => {
  const [documents, setDocuments] = useState<StudyDocument[]>([]);
  const [selectedDoc, setSelectedDoc] = useState<StudyDocument | null>(null);
  const [ragSearchQuery, setRagSearchQuery] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [searchAnswer, setSearchAnswer] = useState<RagSearchAnswer | null>(null);
  const [searchError, setSearchError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Load study materials from API
  useEffect(() => {
    loadMaterials();
  }, []);

  const loadMaterials = async () => {
    const docs = await fetchStudyMaterials();
    setDocuments(docs);
    if (docs.length > 0 && !selectedDoc) {
      setSelectedDoc(docs[0]);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    try {
      const newDoc = await uploadStudyDocument(file, profile.currentSubject);
      setDocuments(prev => [newDoc, ...prev]);
      setSelectedDoc(newDoc);
    } catch (err) {
      console.error('File upload failed:', err);
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleDelete = async (docId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    await deleteStudyDocument(docId);
    setDocuments(prev => prev.filter(d => d.id !== docId));
    if (selectedDoc?.id === docId) {
      setSelectedDoc(documents.find(d => d.id !== docId) || null);
    }
  };

  const handleRagSearch = async () => {
    if (!ragSearchQuery.trim()) return;
    setIsSearching(true);
    setSearchError(null);
    setSearchAnswer(null);
    try {
      const answer = await performRagSearch(ragSearchQuery, selectedDoc?.id);
      setSearchAnswer(answer);
    } catch (err) {
      setSearchError(err instanceof Error ? err.message : 'Could not generate an answer from your study material.');
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div style={{
      padding: '28px 36px',
      height: 'calc(100vh - 56px)',
      overflowY: 'auto',
      display: 'flex',
      flexDirection: 'column',
      gap: '24px',
      background: 'var(--bg-primary)'
    }}>
      {/* Hidden file input */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileUpload}
        accept=".pdf"
        style={{ display: 'none' }}
      />

      {/* Page Header */}
      <div>
        <h2 style={{ fontSize: '1.35rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Database size={22} color="#3b82f6" /> Study Material & Grounded RAG Knowledge
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.86rem', marginTop: '4px' }}>
          Upload lecture notes, textbooks, and syllabus PDFs. EduMate chunks, embeds, and grounds all tutoring explanations with strict citations in your materials.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
        {/* PDF Upload Drop Zone & Uploaded Files */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Upload Dropzone */}
          <div
            onClick={() => fileInputRef.current?.click()}
            className="glass-panel"
            style={{
              border: '1px dashed rgba(37, 99, 235, 0.45)',
              borderRadius: 'var(--radius-xl)',
              padding: '32px 24px',
              textAlign: 'center',
              cursor: 'pointer',
              transition: 'var(--transition-fast)',
              background: 'var(--bg-secondary)'
            }}
            onMouseEnter={(e) => e.currentTarget.style.borderColor = '#2563eb'}
            onMouseLeave={(e) => e.currentTarget.style.borderColor = 'rgba(37, 99, 235, 0.45)'}
          >
            {isUploading ? (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
                <Loader2 size={36} className="spin-slow" color="#3b82f6" />
                <span style={{ fontSize: '0.9rem', color: 'var(--text-primary)', fontWeight: 600 }}>
                  Parsing & Indexing into PostgreSQL...
                </span>
              </div>
            ) : (
              <>
                <UploadCloud size={40} color="#3b82f6" style={{ marginBottom: '10px' }} />
                <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                  Click to Upload Lecture Notes (PDF)
                </h3>
                <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                  Supports PDF files up to 50MB. Text is semantically chunked, embedded, and indexed in PostgreSQL.
                </p>
                <button
                  className="btn btn-primary"
                  style={{ marginTop: '14px', padding: '6px 14px', fontSize: '0.8rem', borderRadius: 'var(--radius-md)' }}
                >
                  + Choose PDF File
                </button>
              </>
            )}
          </div>

          {/* Uploaded Documents List */}
          <div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '14px' }}>
              Indexed Materials ({documents.length})
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {documents.length === 0 ? (
                <div style={{
                  padding: '24px 16px',
                  borderRadius: 'var(--radius-md)',
                  background: 'var(--bg-secondary)',
                  border: '1px dashed var(--border-color)',
                  textAlign: 'center',
                  color: 'var(--text-muted)',
                  fontSize: '0.85rem'
                }}>
                  No study materials indexed yet. Click above to upload a PDF lecture note or syllabus to enable grounded RAG citations.
                </div>
              ) : (
                documents.map((doc) => (
                  <div
                    key={doc.id}
                    onClick={() => setSelectedDoc(doc)}
                    style={{
                      padding: '14px 16px',
                      borderRadius: 'var(--radius-lg)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      cursor: 'pointer',
                      border: selectedDoc?.id === doc.id ? '1px solid #2563eb' : '1px solid var(--border-color)',
                      background: selectedDoc?.id === doc.id ? 'rgba(37, 99, 235, 0.08)' : 'var(--bg-secondary)',
                      transition: 'var(--transition-fast)'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <FileText size={24} color="#60a5fa" />
                      <div>
                        <div style={{ fontWeight: 600, fontSize: '0.88rem', color: 'var(--text-primary)' }}>
                          {doc.name}
                        </div>
                        <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', display: 'flex', gap: '10px', marginTop: '2px' }}>
                          <span>{doc.subject}</span>
                          <span>•</span>
                          <span>{doc.pages} Pages</span>
                          <span>•</span>
                          <span>{doc.chunks} Chunks</span>
                        </div>
                      </div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span className={`badge ${doc.status === 'Ready' ? 'badge-beginner' : 'badge-intermediate'}`}>
                        {doc.status}
                      </span>
                      <button
                        onClick={(e) => handleDelete(doc.id, e)}
                        className="btn btn-ghost"
                        style={{ padding: '6px' }}
                        title="Delete study material"
                      >
                        <Trash2 size={16} color="var(--accent-rose)" />
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Selected Document RAG Vector Chunk Inspection */}
        <div className="glass-panel" style={{
          padding: '24px',
          borderRadius: 'var(--radius-lg)',
          display: 'flex',
          flexDirection: 'column',
          gap: '18px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--border-color)', paddingBottom: '14px' }}>
            <div>
              <h3 style={{ fontSize: '1rem', fontWeight: 600 }}>
                Ask Your Study Material
              </h3>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                {selectedDoc ? selectedDoc.name : 'All Indexed Study Materials'}
              </span>
            </div>
            <span style={{
              fontSize: '0.72rem',
              fontWeight: 600,
              padding: '3px 8px',
              borderRadius: 'var(--radius-md)',
              background: 'var(--accent-primary-subtle)',
              color: '#60a5fa',
              border: '1px solid rgba(37, 99, 235, 0.25)'
            }}>
              RAG • Verified Sources
            </span>
          </div>

          {/* RAG Query Test Box */}
          <div style={{ display: 'flex', gap: '8px' }}>
            <div style={{ position: 'relative', flex: 1, display: 'flex', alignItems: 'center' }}>
              <Search size={16} color="var(--text-muted)" style={{ position: 'absolute', left: '12px' }} />
              <input
                type="text"
                value={ragSearchQuery}
                onChange={(e) => setRagSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleRagSearch()}
                placeholder="Ask a question about your study material..."
                style={{
                  width: '100%',
                  background: 'var(--bg-tertiary)',
                  border: '1px solid var(--border-color)',
                  color: 'var(--text-primary)',
                  padding: '10px 14px 10px 36px',
                  borderRadius: 'var(--radius-md)',
                  fontSize: '0.85rem',
                  outline: 'none'
                }}
              />
            </div>
            <button
              onClick={handleRagSearch}
              className="btn btn-primary"
              style={{ padding: '0 16px', fontSize: '0.85rem', borderRadius: 'var(--radius-md)' }}
              disabled={isSearching}
            >
              {isSearching ? 'Searching...' : 'Search'}
            </button>
          </div>

          {/* Single RAG-generated document answer */}
          <div aria-live="polite" style={{ display: 'flex', flexDirection: 'column', gap: '12px', maxHeight: '350px', overflowY: 'auto' }}>
            {isSearching ? (
              <div style={{ padding: '32px 16px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                <Loader2 size={18} className="animate-spin" style={{ verticalAlign: 'middle', marginRight: '8px' }} />
                Searching your material and generating one grounded answer...
              </div>
            ) : searchError ? (
              <div role="alert" style={{ color: 'var(--accent-rose)', padding: '16px', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)' }}>
                {searchError}
              </div>
            ) : searchAnswer ? (
              <article
                style={{
                  background: 'var(--bg-tertiary)',
                  border: '1px solid rgba(37, 99, 235, 0.35)',
                  borderRadius: 'var(--radius-md)',
                  padding: '18px',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#60a5fa', fontSize: '0.78rem', fontWeight: 700, marginBottom: '12px' }}>
                  <Sparkles size={15} />
                  <span>RAG ANSWER</span>
                </div>
                <p style={{ whiteSpace: 'pre-wrap', fontSize: '0.92rem', color: 'var(--text-primary)', lineHeight: 1.75, margin: 0 }}>
                  {searchAnswer.answer}
                </p>
                {!!searchAnswer.citations.length && (
                  <div style={{ marginTop: '16px', paddingTop: '12px', borderTop: '1px solid var(--border-color)', display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                    {searchAnswer.citations.map((citation, index) => (
                      <span
                        key={`${citation.document_name}-${citation.page_number}-${index}`}
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '6px',
                          borderRadius: 'var(--radius-full)',
                          padding: '5px 10px',
                          color: 'var(--accent-emerald)',
                          background: 'rgba(16, 185, 129, 0.1)',
                          fontSize: '0.76rem',
                        }}
                      >
                        <FileText size={13} />
                        {citation.document_name} • Page {citation.page_number}
                      </span>
                    ))}
                  </div>
                )}
              </article>
            ) : (
              <div style={{
                padding: '32px 16px',
                textAlign: 'center',
                color: 'var(--text-muted)',
                fontSize: '0.85rem',
                border: '1px dashed var(--border-color)',
                borderRadius: 'var(--radius-md)',
                background: 'rgba(255, 255, 255, 0.01)'
              }}>
                {ragSearchQuery.trim()
                  ? `Ask about "${ragSearchQuery}" to get one answer grounded in your study material.`
                  : 'Enter a question above to get one answer grounded in your study material.'}
              </div>
            )}
          </div>

          {/* Fallback Warning Box */}
          <div style={{
            marginTop: 'auto',
            padding: '12px 14px',
            borderRadius: 'var(--radius-md)',
            background: 'rgba(245, 158, 11, 0.08)',
            border: '1px solid rgba(245, 158, 11, 0.25)',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            fontSize: '0.8rem',
            color: 'var(--accent-amber)'
          }}>
            <AlertCircle size={18} style={{ flexShrink: 0 }} />
            <span>
              <strong>Grounding Transparency:</strong> Answers are generated from retrieved passages and include verified document citations. If no relevant passage is found, EduMate will say so instead of guessing.
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
