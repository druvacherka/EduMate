import React, { useState } from 'react';
import { ActiveTab, StudentProfile } from './types';
import { Sidebar } from './components/Sidebar';
import { Navbar } from './components/Navbar';
import { ChatView } from './components/ChatView';
import { StudyMaterialView } from './components/StudyMaterialView';
import { QuizView } from './components/QuizView';
import { AnalyticsView } from './components/AnalyticsView';
import { SettingsView } from './components/SettingsView';

export function App() {
  const [activeTab, setActiveTab] = useState<ActiveTab>('tutor');
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  const [isVoiceActive, setIsVoiceActive] = useState<boolean>(true);

  const [profile, setProfile] = useState<StudentProfile>({
    name: 'Druva Kumar',
    email: 'druva@edumate.edu',
    level: 'Beginner',
    language: 'English',
    currentSubject: 'Data Structures',
    currentTopic: 'Binary Search Trees',
    masteryScore: 82,
    weakAreas: ['BST Deletion', '3NF Normalization'],
    strongAreas: ['Arrays', 'Linked Lists', 'In-Order Traversal'],
    studyStreakDays: 5
  });

  return (
    <div className="app-container" data-theme={theme}>
      {/* Sidebar Navigation */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        profile={profile}
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
        />

        <main style={{ flex: 1, overflow: 'hidden', position: 'relative' }}>
          {activeTab === 'tutor' && (
            <ChatView profile={profile} isVoiceActive={isVoiceActive} />
          )}
          {activeTab === 'materials' && (
            <StudyMaterialView profile={profile} />
          )}
          {activeTab === 'quizzes' && (
            <QuizView profile={profile} />
          )}
          {activeTab === 'analytics' && (
            <AnalyticsView profile={profile} />
          )}
          {activeTab === 'settings' && (
            <SettingsView profile={profile} setProfile={setProfile} />
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
