import React, { useState } from 'react';
import { StudyDocument, StudentProfile } from '../types';
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
  AlertCircle
} from 'lucide-react';

interface StudyMaterialViewProps {
  profile: StudentProfile;
}

export const StudyMaterialView: React.FC<StudyMaterialViewProps> = ({ profile }) => {
  const [documents, setDocuments] = useState<StudyDocument[]>([
    {
      id: 'doc-1',
      name: 'Data_Structures_Unit3_Trees.pdf',
      uploadDate: '2026-08-25',
      size: '2.4 MB',
      pages: 28,
      chunks: 84,
      status: 'Ready',
      subject: 'Data Structures'
    },
    {
      id: 'doc-2',
      name: 'DBMS_Unit_2_Normalization.pdf',
      uploadDate: '2026-08-26',
      size: '1.8 MB',
      pages: 18,
      chunks: 52,
      status: 'Ready',
      subject: 'Database Management'
    },
    {
      id: 'doc-3',
      name: 'Algorithms_Sorting_Searching_Notes.pdf',
      uploadDate: '2026-08-28',
      size: '3.1 MB',
      pages: 35,
      chunks: 110,
      status: 'Processing',
      subject: 'Algorithms'
    }
  ]);

  const [selectedDoc, setSelectedDoc] = useState<StudyDocument | null>(documents[0]);
  const [ragSearchQuery, setRagSearchQuery] = useState('');

  const handleSimulatedUpload = () => {
    const newDoc: StudyDocument = {
      id: `doc-${Date.now()}`,
      name: 'Operating_Systems_Semaphores.pdf',
      uploadDate: new Date().toISOString().split('T')[0],
      size: '1.5 MB',
      pages: 14,
      chunks: 42,
      status: 'Ready',
      subject: 'Operating Systems'
    };
    setDocuments(prev => [newDoc, ...prev]);
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
      {/* Page Header */}
      <div>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Database color="var(--accent-cyan)" /> Study Material & Grounded RAG Knowledge
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginTop: '4px' }}>
          Upload your lecture notes, textbooks, and syllabus PDFs. EduMate chunks, embeds, and grounds all tutoring explanations in your specific study materials.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
        {/* PDF Upload Drop Zone & Uploaded Files */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Upload Dropzone */}
          <div
            onClick={handleSimulatedUpload}
            className="glass-panel"
            style={{
              border: '2px dashed var(--border-color-glow)',
              borderRadius: 'var(--radius-lg)',
              padding: '36px 24px',
              textAlign: 'center',
              cursor: 'pointer',
              transition: 'var(--transition-smooth)',
              background: 'rgba(99, 102, 241, 0.03)'
            }}
          >
            <UploadCloud size={48} color="var(--accent-primary)" style={{ marginBottom: '12px' }} />
            <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--text-primary)' }}>
              Click to Upload Lecture Notes (PDF)
            </h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '4px' }}>
              Supports PDF files up to 50MB. Text is semantically chunked and indexed into Qdrant Vector Store.
            </p>
            <span className="badge badge-lang" style={{ marginTop: '14px' }}>
              + Upload Demo PDF
            </span>
          </div>

          {/* Uploaded Documents List */}
          <div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '14px' }}>
              Indexed Materials ({documents.length})
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {documents.map((doc) => (
                <div
                  key={doc.id}
                  onClick={() => setSelectedDoc(doc)}
                  className="glass-panel"
                  style={{
                    padding: '16px',
                    borderRadius: 'var(--radius-md)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    cursor: 'pointer',
                    border: selectedDoc?.id === doc.id ? '1px solid var(--accent-primary)' : '1px solid var(--border-color)',
                    background: selectedDoc?.id === doc.id ? 'rgba(99, 102, 241, 0.08)' : 'var(--bg-secondary)'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <FileText size={28} color="var(--accent-cyan)" />
                    <div>
                      <div style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-primary)' }}>
                        {doc.name}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', gap: '12px', marginTop: '2px' }}>
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
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Selected Document RAG Vector Chunk Inspection */}
        {selectedDoc && (
          <div className="glass-panel" style={{
            padding: '24px',
            borderRadius: 'var(--radius-lg)',
            display: 'flex',
            flexDirection: 'column',
            gap: '18px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--border-color)', paddingBottom: '14px' }}>
              <div>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 600 }}>
                  Vector Chunk Preview
                </h3>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  {selectedDoc.name}
                </span>
              </div>
              <span className="badge badge-lang">
                {selectedDoc.chunks} Embedded Vectors
              </span>
            </div>

            {/* RAG Query Test Box */}
            <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
              <Search size={16} color="var(--text-muted)" style={{ position: 'absolute', left: '12px' }} />
              <input
                type="text"
                value={ragSearchQuery}
                onChange={(e) => setRagSearchQuery(e.target.value)}
                placeholder="Test semantic retrieval (e.g., 'normalization', 'rotations')..."
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

            {/* Sample Retrieved Vector Chunks */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div style={{
                background: 'rgba(255, 255, 255, 0.03)',
                border: '1px solid var(--border-color)',
                borderRadius: 'var(--radius-md)',
                padding: '14px'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--accent-emerald)', marginBottom: '6px' }}>
                  <span>Chunk #14 (Page 4)</span>
                  <span>Cosine Similarity: 0.92</span>
                </div>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                  "A Binary Search Tree (BST) is an organized binary tree where each node key is greater than all keys in its left subtree and smaller than all keys in its right subtree."
                </p>
              </div>

              <div style={{
                background: 'rgba(255, 255, 255, 0.03)',
                border: '1px solid var(--border-color)',
                borderRadius: 'var(--radius-md)',
                padding: '14px'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--accent-emerald)', marginBottom: '6px' }}>
                  <span>Chunk #18 (Page 8)</span>
                  <span>Cosine Similarity: 0.86</span>
                </div>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                  "Deletion in a BST involves three cases: 1) Node is a leaf, 2) Node has one child, 3) Node has two children (replace with in-order successor)."
                </p>
              </div>
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
                <strong>Grounding Transparency:</strong> If a student query falls below 0.65 similarity, EduMate explicitly flags that the information is absent from notes.
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
