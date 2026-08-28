export type LearningLevel = 'Beginner' | 'Intermediate' | 'Advanced';

export type Language = 'English' | 'Hindi' | 'Telugu';

export type ActiveTab = 'tutor' | 'materials' | 'quizzes' | 'analytics' | 'settings';

export interface SubjectTopic {
  id: string;
  subject: string;
  topic: string;
}

export interface ChatMessage {
  id: string;
  sender: 'student' | 'tutor';
  text: string;
  timestamp: string;
  level?: LearningLevel;
  language?: Language;
  quickActions?: string[];
  isAudio?: boolean;
  documentRef?: {
    name: string;
    page: number;
    snippet: string;
  };
  codeSnippet?: {
    language: string;
    code: string;
  };
  formula?: string;
}

export interface StudyDocument {
  id: string;
  name: string;
  uploadDate: string;
  size: string;
  pages: number;
  chunks: number;
  status: 'Ready' | 'Processing' | 'Failed';
  subject: string;
}

export interface QuizQuestion {
  id: string;
  type: 'mcq' | 'tf' | 'short';
  question: string;
  options?: string[];
  correctAnswer: string | number;
  explanation: string;
  difficulty: 'Easy' | 'Medium' | 'Hard';
  topic: string;
}

export interface StudentProfile {
  name: string;
  email: string;
  level: LearningLevel;
  language: Language;
  currentSubject: string;
  currentTopic: string;
  masteryScore: number;
  weakAreas: string[];
  strongAreas: string[];
  studyStreakDays: number;
}
