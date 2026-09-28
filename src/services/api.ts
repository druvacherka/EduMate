import { StudyDocument, StudentProfile } from '../types';

const API_BASE_URL = 'http://localhost:8000/api';

export interface ChatRequestPayload {
  query: string;
  level: string;
  language: string;
  conversation_history?: Array<{ sender: string; text: string }>;
}

export interface ChatResponseData {
  response: string;
  level: string;
  language: string;
  quick_actions: string[];
  citations?: Array<{ document_name: string; page_number: number; raw_tag?: string }>;
}

export interface QuizRequestPayload {
  topic: string;
  num_questions?: number;
  difficulty?: string;
}

export interface QuizQuestionData {
  id: string;
  type: 'mcq' | 'tf' | 'short';
  question: string;
  options?: string[];
  correctAnswer: any;
  explanation: string;
  difficulty: string;
  topic: string;
}

export interface QuizSessionData {
  session_id: string;
  topic: string;
  difficulty: string;
  status: string;
  questions: QuizQuestionData[];
}

export interface QuizSubmissionResponse {
  session_id: string;
  status: string;
  score: number;
  total_questions: number;
  percentage: number;
  mistakes_count: number;
  mistaken_topics: string[];
  results: Array<{
    id: string;
    question: string;
    type?: string;
    options?: string[];
    user_answer: any;
    correct_answer: any;
    is_correct: boolean;
    explanation: string;
  }>;
}

export interface RagSearchResultItem {
  chunk_id: string;
  document_name: string;
  page_number: number;
  text_snippet: string;
  section_title?: string;
  score: number;
  dense_score: number;
  bm25_score: number;
  rrf_score: number;
}

export async function sendSocraticChatMessage(payload: ChatRequestPayload): Promise<ChatResponseData> {
  const res = await fetch(`${API_BASE_URL}/chat/socratic`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(errorData.detail || `API error: ${res.statusText}`);
  }

  return await res.json();
}

export async function fetchStudyMaterials(): Promise<StudyDocument[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/materials`);
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Failed to fetch study materials from backend:', err);
    return [];
  }
}

export async function uploadStudyDocument(file: File, subject: string = 'Computer Science') {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('subject', subject);

  const res = await fetch(`${API_BASE_URL}/materials/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const errData = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(errData.detail || `Upload error: ${res.statusText}`);
  }

  const data = await res.json();
  return data.document;
}

export async function deleteStudyDocument(docId: string): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE_URL}/materials/${docId}`, {
      method: 'DELETE',
    });
    return res.ok;
  } catch (err) {
    console.warn('Delete material error:', err);
    return false;
  }
}

export async function generateQuizQuestions(payload: QuizRequestPayload): Promise<QuizSessionData> {
  const res = await fetch(`${API_BASE_URL}/quizzes/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const errData = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(errData.detail || `Quiz API error: ${res.statusText}`);
  }

  return await res.json();
}

export async function submitQuizAnswers(sessionId: string, userAnswers: Record<string, any>): Promise<QuizSubmissionResponse> {
  const res = await fetch(`${API_BASE_URL}/quizzes/submit`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, user_answers: userAnswers }),
  });

  if (!res.ok) {
    const errData = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(errData.detail || `Quiz submission error: ${res.statusText}`);
  }

  return await res.json();
}

export async function fetchStudentProfile(): Promise<StudentProfile & { subjectProgress?: any[] }> {
  try {
    const res = await fetch(`${API_BASE_URL}/analytics/profile`);
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Could not fetch student profile from backend, using empty state:', err);
    return {
      name: 'Student',
      email: '',
      level: 'Beginner',
      language: 'English',
      currentSubject: '',
      currentTopic: '',
      masteryScore: 0.0,
      studyStreakDays: 0,
      weakAreas: [],
      strongAreas: [],
      subjectProgress: [],
    };
  }
}

export async function updateStudentProfile(settings: { level?: string; language?: string; current_subject?: string; current_topic?: string }) {
  try {
    const res = await fetch(`${API_BASE_URL}/settings/profile`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(settings),
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Profile settings update failed:', err);
    return { status: 'error' };
  }
}

export async function performRagSearch(queryText: string, topK: number = 4): Promise<RagSearchResultItem[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/rag/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query_text: queryText, top_k: topK }),
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    const data = await res.json();
    return data.results || [];
  } catch (err) {
    console.warn('Fallback RAG search:', err);
    return [];
  }
}
