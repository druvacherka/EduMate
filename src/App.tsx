import React, { useState, useEffect } from 'react';
import { ActiveTab, StudentProfile } from './types';
import { Sidebar } from './components/Sidebar';
import { Navbar } from './components/Navbar';
import { DashboardView } from './components/DashboardView';
import { CurriculumView } from './components/CurriculumView';
import { ChatView } from './components/ChatView';
import { StudyMaterialView } from './components/StudyMaterialView';
import { QuizView } from './components/QuizView';
import { PlannerView } from './components/PlannerView';
import { RevisionView } from './components/RevisionView';
import { GoalsView } from './components/GoalsView';
import { CareerExplorerView } from './components/CareerExplorerView';
import { AnalyticsView } from './components/AnalyticsView';
import { SettingsView } from './components/SettingsView';
import { OnboardingModal } from './components/OnboardingModal';

import { fetchStudentProfile } from './services/api';

export function App() {
  const [activeTab, setActiveTab] = useState<ActiveTab>('dashboard');
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  const [isVoiceActive, setIsVoiceActive] = useState<boolean>(true);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState<boolean>(false);
  const [isOnboardingOpen, setIsOnboardingOpen] = useState<boolean>(false);

  const [profile, setProfile] = useState<StudentProfile>({
    name: 'Student',
    email: '',
    level: 'Beginner',
    language: 'English',
    currentSubject: '',
    currentTopic: '',
    masteryScore: 0.0,
    weakAreas: [],
    strongAreas: [],
    studyStreakDays: 0,
    educationLevel: '',
    institution: '',
    streamBranch: '',
    academicYearSemester: '',
    dailyStudyHours: 0,
    onboardingCompleted: false,
  });

  const loadProfile = () => {
    fetchStudentProfile().then((data) => {
      if (data) {
        setProfile((prev) => ({ ...prev, ...data }));
        if (data.onboardingCompleted === false) {
          setIsOnboardingOpen(true);
        }
      }
    });
  };

  useEffect(() => {
    loadProfile();
  }, []);

  const toggleSidebar = () => {
    setIsSidebarCollapsed((prev) => !prev);
  };

  const handleNavigateToTab = (tab: ActiveTab, topicContext?: string) => {
    if (topicContext) {
      setProfile((prev) => ({
        ...prev,
        currentTopic: topicContext,
      }));
    }
    setActiveTab(tab);
  };

  const handleSelectTopicForChat = (topic: string, subject: string) => {
    setProfile((prev) => ({
      ...prev,
      currentSubject: subject,
      currentTopic: topic,
    }));
    setActiveTab('tutor');
  };

  const handleSelectTopicForQuiz = (topic: string) => {
    setProfile((prev) => ({
      ...prev,
      currentTopic: topic,
    }));
    setActiveTab('quizzes');
  };

  return (
    <div className="app-container" data-theme={theme}>
      {/* Sidebar Navigation */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        profile={profile}
        isCollapsed={isSidebarCollapsed}
        onToggleCollapse={toggleSidebar}
      />

      {/* Main Content Workspace */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>
        <Navbar
          profile={profile}
          setProfile={setProfile}
          theme={theme}
          setTheme={setTheme}
          isVoiceActive={isVoiceActive}
          setIsVoiceActive={setIsVoiceActive}
          isSidebarCollapsed={isSidebarCollapsed}
          onToggleSidebar={toggleSidebar}
          onOpenOnboarding={() => setIsOnboardingOpen(true)}
        />

        <main style={{ flex: 1, overflowY: 'auto', position: 'relative', padding: activeTab === 'tutor' ? 0 : '24px 32px' }}>
          {activeTab === 'dashboard' && (
            <DashboardView
              onNavigateToTab={handleNavigateToTab}
              onOpenOnboarding={() => setIsOnboardingOpen(true)}
            />
          )}

          {activeTab === 'curriculum' && (
            <CurriculumView
              onSelectTopicForChat={handleSelectTopicForChat}
              onSelectTopicForQuiz={handleSelectTopicForQuiz}
            />
          )}

          {activeTab === 'tutor' && (
            <ChatView profile={profile} isVoiceActive={isVoiceActive} />
          )}

          {activeTab === 'materials' && (
            <StudyMaterialView profile={profile} />
          )}

          {activeTab === 'quizzes' && (
            <QuizView profile={profile} />
          )}

          {activeTab === 'planner' && (
            <PlannerView onNavigateToTab={handleNavigateToTab} />
          )}

          {activeTab === 'revision' && (
            <RevisionView
              onSelectTopicForChat={handleSelectTopicForChat}
              onSelectTopicForQuiz={handleSelectTopicForQuiz}
            />
          )}

          {activeTab === 'goals' && (
            <GoalsView onNavigateToTab={handleNavigateToTab} />
          )}

          {activeTab === 'career' && (
            <CareerExplorerView onNavigateToTab={handleNavigateToTab} />
          )}

          {activeTab === 'analytics' && (
            <AnalyticsView profile={profile} />
          )}

          {activeTab === 'settings' && (
            <SettingsView
              profile={profile}
              setProfile={setProfile}
              onOpenOnboarding={() => setIsOnboardingOpen(true)}
            />
          )}
        </main>
      </div>

      {/* Student Onboarding Flow Modal */}
      <OnboardingModal
        isOpen={isOnboardingOpen}
        onClose={() => setIsOnboardingOpen(false)}
        onCompleted={loadProfile}
      />
    </div>
  );
}

export default App;
