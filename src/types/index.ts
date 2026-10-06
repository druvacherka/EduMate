export type LearningLevel = 'Beginner' | 'Intermediate' | 'Advanced';

export type Language = 'English' | 'Hindi' | 'Telugu';

export type ActiveTab =
  | 'dashboard'
  | 'curriculum'
  | 'tutor'
  | 'materials'
  | 'quizzes'
  | 'planner'
  | 'revision'
  | 'goals'
  | 'career'
  | 'analytics'
  | 'settings';

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
  level?: LearningLevel | '';
  language?: Language | '';
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
  citations?: Array<{
    document_name: string;
    page_number: number;
  }>;
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
  education_level?: string;
  curriculum?: string;
  goal_id?: string;
}

export interface QuizQuestion {
  id: string;
  type: 'mcq' | 'tf' | 'short';
  question: string;
  options?: string[];
  correctAnswer: any;
  explanation: string;
  difficulty: 'Easy' | 'Medium' | 'Hard';
  topic: string;
}

export interface StudentProfile {
  name: string;
  email: string;
  level: LearningLevel | '';
  language: Language | '';
  currentSubject: string;
  currentTopic: string;
  masteryScore: number;
  weakAreas: string[];
  strongAreas: string[];
  studyStreakDays: number;
  subjectProgress?: Array<{
    name: string;
    progress: number;
    topicsCompleted: number;
    totalTopics: number;
    status: string;
  }>;
  educationLevel?: string;
  institution?: string;
  streamBranch?: string;
  academicYearSemester?: string;
  dailyStudyHours?: number;
  onboardingCompleted?: boolean;
  activeGoalsCount?: number;
}

export interface StudentGoal {
  id: string;
  name: string;
  goal_type: 'academic' | 'exam' | 'career' | 'skill';
  target_exam?: string;
  target_date?: string;
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
  available_hours_per_day: number;
  current_level: LearningLevel | '';
  target_level: LearningLevel | '';
  is_active: boolean;
  created_at?: string;
}

export interface DailyStudyTask {
  id: string;
  title: string;
  subject: string;
  topic: string;
  task_type: 'LEARN' | 'PRACTICE' | 'QUIZ' | 'REVISE' | 'REVIEW_MISTAKES';
  estimated_minutes: number;
  is_completed: boolean;
  priority: 'HIGH' | 'MEDIUM' | 'NORMAL';
  reason?: string;
  date_scheduled: string;
  plan_id?: string;
}

export interface DailyDashboardData {
  greeting: string;
  student_name: string;
  education_level: string;
  stream_branch: string;
  available_hours_today: number;
  study_streak_days: number;
  overall_mastery: number;
  active_goals: StudentGoal[];
  today_tasks: DailyStudyTask[];
  total_tasks_count: number;
  completed_tasks_count: number;
  estimated_time_remaining_minutes: number;
  priority_weak_areas: string[];
  recent_recommendation?: {
    recommended_action: string;
    subject: string;
    topic: string;
    reason: string;
    estimated_minutes: number;
    priority: string;
    learning_level?: string;
  };
}

export interface StudyPlanItem {
  week_number: number;
  theme: string;
  focus_topics: string[];
  target_milestone: string;
  estimated_hours: number;
}

export interface StudyPlan {
  id: string;
  goal_id?: string;
  title: string;
  target_date?: string;
  total_hours_planned: number;
  status: string;
  weekly_breakdown: StudyPlanItem[];
}

export interface CurriculumTopic {
  name: string;
  difficulty: 'Easy' | 'Medium' | 'Hard';
  concepts: string[];
}

export interface CurriculumChapter {
  name: string;
  topics: CurriculumTopic[];
}

export interface CurriculumSubject {
  subject: string;
  chapters: CurriculumChapter[];
}

export interface CurriculumLevel {
  id: string;
  title: string;
  description: string;
  icon: string;
  streams: string[];
}

export interface RevisionItem {
  id: number;
  subject: string;
  topic: string;
  learned_date: string;
  interval_days: number;
  next_revision_date: string;
  last_reviewed_date?: string;
  mastery_score: number;
  mistake_count: number;
  status: 'DUE' | 'PENDING' | 'COMPLETED';
}

export interface CareerPath {
  id: string;
  title: string;
  category: string;
  description: string;
  target_degrees: string[];
  primary_exams: string[];
  core_subjects: string[];
  key_skills: string[];
  typical_roadmap: string[];
}
