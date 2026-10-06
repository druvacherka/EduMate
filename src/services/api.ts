import {
  StudyDocument,
  StudentProfile,
  StudentGoal,
  DailyDashboardData,
  DailyStudyTask,
  StudyPlan,
  CurriculumLevel,
  RevisionItem,
  CareerPath,
} from '../types';

const API_BASE_URL = 'http://localhost:8000/api';
const AUTH_TOKEN_KEY = 'edumate.accessToken';

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: { id: number; email: string };
}

export function getAuthToken(): string | null {
  return window.localStorage.getItem(AUTH_TOKEN_KEY);
}

export function clearAuthToken(): void {
  window.localStorage.removeItem(AUTH_TOKEN_KEY);
}

async function fetch(input: RequestInfo | URL, init?: RequestInit): Promise<Response> {
  const headers = new Headers(init?.headers);
  const token = getAuthToken();
  if (token) headers.set('Authorization', `Bearer ${token}`);
  const response = await window.fetch(input, { ...init, headers });
  if (response.status === 401) {
    clearAuthToken();
    window.dispatchEvent(new Event('edumate:unauthorized'));
  }
  return response;
}

export async function authenticateAccount(
  mode: 'login' | 'register',
  email: string,
  password: string
): Promise<AuthResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/${mode}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || 'Authentication failed.');
  window.localStorage.setItem(AUTH_TOKEN_KEY, data.access_token);
  return data;
}

export async function validateAuthToken(): Promise<boolean> {
  if (!getAuthToken()) return false;
  try {
    const response = await fetch(`${API_BASE_URL}/auth/me`);
    return response.ok;
  } catch {
    return false;
  }
}

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

export async function uploadStudyDocument(
  file: File,
  subject: string = 'General',
  educationLevel: string = 'All',
  curriculum: string = 'General'
) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('subject', subject);
  formData.append('education_level', educationLevel);
  formData.append('curriculum', curriculum);

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

export async function submitQuizAnswers(
  sessionId: string,
  userAnswers: Record<string, any>
): Promise<QuizSubmissionResponse> {
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
      name: '',
      email: '',
      level: '',
      language: '',
      currentSubject: '',
      currentTopic: '',
      masteryScore: 0.0,
      studyStreakDays: 0,
      weakAreas: [],
      strongAreas: [],
      subjectProgress: [],
      educationLevel: '',
      streamBranch: '',
      dailyStudyHours: 0,
      onboardingCompleted: false,
    };
  }
}

export async function updateStudentProfile(settings: Record<string, any>) {
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

// ==============================================================================
// Universal Platform API Extensions
// ==============================================================================

export async function fetchDailyDashboard(): Promise<DailyDashboardData | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/dashboard/daily`);
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Failed to fetch daily dashboard:', err);
    return null;
  }
}

export async function toggleDailyTask(taskId: string): Promise<DailyStudyTask | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/dashboard/tasks/${taskId}/toggle`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Failed to toggle task:', err);
    return null;
  }
}

export async function fetchStudentGoals(): Promise<StudentGoal[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/goals`);
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Failed to fetch goals:', err);
    return [];
  }
}

export async function createStudentGoal(goalData: Partial<StudentGoal>): Promise<StudentGoal | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/goals`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(goalData),
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Failed to create goal:', err);
    return null;
  }
}

export async function deleteStudentGoal(goalId: string): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE_URL}/goals/${goalId}`, {
      method: 'DELETE',
    });
    return res.ok;
  } catch (err) {
    console.warn('Failed to delete goal:', err);
    return false;
  }
}

export async function toggleStudentGoal(goalId: string): Promise<StudentGoal | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/goals/${goalId}/toggle`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Failed to toggle goal:', err);
    return null;
  }
}

export async function selectStudentGoal(goalId: string): Promise<StudentGoal | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/goals/${goalId}/select`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Failed to select active goal:', err);
    return null;
  }
}

export async function generateAdaptiveStudyPlan(payload: {
  goal_name: string;
  target_date?: string;
  available_hours_per_day?: number;
  current_level?: string;
}): Promise<StudyPlan | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/planner/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Failed to generate adaptive plan:', err);
    return null;
  }
}

export async function fetchCurriculumLevels(): Promise<CurriculumLevel[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/curriculum/levels`);
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Failed to fetch curriculum levels:', err);
    return [];
  }
}

export async function fetchCurriculumHierarchy(levelId: string = 'btech', stream: string = 'Computer Science & Engineering') {
  try {
    const res = await fetch(
      `${API_BASE_URL}/curriculum/hierarchy?level_id=${encodeURIComponent(levelId)}&stream=${encodeURIComponent(stream)}`
    );
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Failed to fetch curriculum hierarchy:', err);
    return { education_level: levelId, stream: stream, subjects: [] };
  }
}

export async function fetchNextRecommendation() {
  try {
    const res = await fetch(`${API_BASE_URL}/recommendations/next`);
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Failed to fetch recommendation:', err);
    return null;
  }
}

export async function fetchRevisionItems(dueOnly: boolean = false): Promise<RevisionItem[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/revision/items?due_only=${dueOnly}`);
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Failed to fetch revision items:', err);
    return [];
  }
}

export async function completeRevisionItem(itemId: number, score: number = 100.0): Promise<RevisionItem | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/revision/complete`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ item_id: itemId, score: score }),
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Failed to complete revision item:', err);
    return null;
  }
}

export async function fetchCareerPaths(): Promise<CareerPath[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/career/paths`);
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Failed to fetch career paths:', err);
    return [];
  }
}

export async function logVoiceSession(payload: {
  language: string;
  topic?: string;
  goal_id?: string;
  duration_seconds: number;
  transcript_summary?: string;
}) {
  try {
    const res = await fetch(`${API_BASE_URL}/voice/session`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return await res.json();
  } catch (err) {
    console.warn('Failed to log voice session:', err);
    return null;
  }
}

export async function submitStudentOnboarding(payload: Record<string, any>) {
  const res = await fetch(`${API_BASE_URL}/onboarding`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Onboarding submission failed');
  }
  return await res.json();
}
