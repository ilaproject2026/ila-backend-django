# 🚀 ILA_APP — React (TypeScript) Frontend Connection & Integration Blueprint

> **Complete Enterprise DRF Integration Guide for React 18+ / Vite / Tailwind / TypeScript**  
> *Connecting the complete ILA_APP Suite: Study Abroad ATS, Work & Study Hub, Jobs & Career Matcher, Communication Engine, Intake Tracking, and Rewards Loyalty Plan.*

---

## 📑 Table of Contents

1. [Architecture & Base URL Routing](#1-architecture--base-url-routing)
2. [Global HTTP Client & Auth Protocol](#2-global-http-client--auth-protocol)
3. [Comprehensive Endpoint Reference Matrix](#3-comprehensive-endpoint-reference-matrix)
4. [Section 1: Study Abroad, ATS & AI Resume Parser](#4-section-1-study-abroad-ats--ai-resume-parser)
5. [Section 2: Work & Study Hub](#5-section-2-work--study-hub)
6. [Section 3: Job Search, Candidates & Match Engine](#6-section-3-job-search-candidates--match-engine)
7. [Section 4: Automated Communication Engine](#7-section-4-automated-communication-engine)
8. [Section 5: Front Office Intake & Campaign Tracking](#8-section-5-front-office-intake--campaign-tracking)
9. [Section 6: Rewards & Loyalty Engine](#9-section-6-rewards--loyalty-engine)
10. [TypeScript Domain Type Definitions (`src/types/ilaApp.ts`)](#10-typescript-domain-type-definitions)
11. [Complete React Custom Hooks Library](#11-complete-react-custom-hooks-library)
12. [React Component Wiring & UI Integration Examples](#12-react-component-wiring--ui-integration-examples)

---

## 1. Architecture & Base URL Routing

The backend exposes all **ILA_APP** features under consistent, modular endpoints:

```text
Backend Server: http://localhost:8000
API Version Prefix: /api/v1/ (Also aliased to /api/ and /api/v1/ila-app/)
```

### URL Prefix Mapping

| Module Name | Core Route | Direct Aliases |
|---|---|---|
| **Study Abroad & ATS** | `/api/v1/study-abroad/` | `/api/v1/ila-app/study-abroad/` |
| **Work & Study** | `/api/v1/work-study/` | `/api/v1/work-study-hub/`, `/api/v1/ila-app/work-study/` |
| **Jobs & Career** | `/api/v1/jobs/` | `/api/v1/job-search/`, `/api/v1/ila-app/jobs/` |
| **Communication Engine** | `/api/v1/communication/` | `/api/v1/communication-engine/`, `/api/v1/ila-app/communication/` |
| **Intake Tracking** | `/api/v1/intake/` | `/api/v1/intake-tracking/`, `/api/v1/ila-app/intake/` |
| **Rewards & Loyalty** | `/api/v1/rewards/` | `/api/v1/rewards-plan/`, `/api/v1/ila-app/rewards/` |

---

## 2. Global HTTP Client & Auth Protocol

Create `src/services/api/ilaAppClient.ts` in your frontend project:

```typescript
// src/services/api/ilaAppClient.ts
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

class ILAAppClient {
  private getAuthHeader(): Record<string, string> {
    const token = localStorage.getItem('ila_access_token') || localStorage.getItem('access_token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  public async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_BASE_URL}${endpoint.startsWith('/') ? '' : '/'}${endpoint}`;
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...this.getAuthHeader(),
      ...(options.headers as Record<string, string> || {}),
    };

    const response = await fetch(url, { ...options, headers });
    if (!response.ok) {
      const errorBody = await response.json().catch(() => ({}));
      throw new Error(errorBody.error || errorBody.message || `HTTP ${response.status}: ${response.statusText}`);
    }
    return response.json() as Promise<T>;
  }

  public get<T>(endpoint: string, params?: Record<string, any>): Promise<T> {
    let url = endpoint;
    if (params) {
      const query = new URLSearchParams();
      Object.entries(params).forEach(([key, val]) => {
        if (val !== undefined && val !== null && val !== '') query.append(key, String(val));
      });
      const qs = query.toString();
      if (qs) url += `?${qs}`;
    }
    return this.request<T>(url, { method: 'GET' });
  }

  public post<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, { method: 'POST', body: data ? JSON.stringify(data) : undefined });
  }

  public put<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, { method: 'PUT', body: data ? JSON.stringify(data) : undefined });
  }

  public patch<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, { method: 'PATCH', body: data ? JSON.stringify(data) : undefined });
  }

  public delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }

  public async uploadFile<T>(endpoint: string, formData: FormData): Promise<T> {
    const url = `${API_BASE_URL}${endpoint.startsWith('/') ? '' : '/'}${endpoint}`;
    const response = await fetch(url, {
      method: 'POST',
      headers: { ...this.getAuthHeader() }, // Let browser set Content-Type with boundary for FormData
      body: formData,
    });
    if (!response.ok) {
      const errorBody = await response.json().catch(() => ({}));
      throw new Error(errorBody.error || `HTTP ${response.status}: ${response.statusText}`);
    }
    return response.json() as Promise<T>;
  }
}

export const ilaAppClient = new ILAAppClient();
```

---

## 3. Comprehensive Endpoint Reference Matrix

| # | Module | Action / Feature | HTTP Method | Endpoint Path | Payload / Query |
|---|---|---|---|---|---|
| **1** | Study Abroad | List All Countries | `GET` | `/study-abroad/countries/` | — |
| **2** | Study Abroad | Get/Create Country | `GET/POST` | `/study-abroad/countries/` | `{ name, code, flag, visa_type, avg_tuition, living_cost }` |
| **3** | Study Abroad | List Colleges | `GET` | `/study-abroad/colleges/` | `?country_id={id}` |
| **4** | Study Abroad | List Courses | `GET` | `/study-abroad/courses/` | `?country_id={id}&degree={degree}` |
| **5** | Study Abroad | Public Student Browse | `GET` | `/study-abroad/courses/public-browse/` | Obfuscates institutional proprietary details |
| **6** | Study Abroad | Student Applications | `GET/POST` | `/study-abroad/applications/` | `{ applicant_name, applicant_email, target_country, target_degree }` |
| **7** | Study Abroad | Toggle College Reveal | `POST` | `/study-abroad/applications/{id}/toggle-college-reveal/` | `{ reveal: boolean }` |
| **8** | Study Abroad | Document Checklists | `GET` | `/study-abroad/checklists/` | `?country={country}&course_track={track}` |
| **9** | Study Abroad | Consultant ATS Tasks | `GET` | `/study-abroad/ats-tasks/` | `?stage={stage}&search={query}` |
| **10**| Study Abroad | Advance ATS Stage | `POST` | `/study-abroad/ats-tasks/{id}/advance-stage/` | `{ stage: string, author: string }` |
| **11**| Study Abroad | Log Follow-up Note | `POST` | `/study-abroad/ats-tasks/{id}/log-note/` | `{ note: string, author: string, next_follow_up_date: string }` |
| **12**| Study Abroad | AI Profile Matcher | `POST` | `/study-abroad/profile-match/` | `{ country_id, cgpa, ielts, german_level }` |
| **13**| Study Abroad | AI Resume Parser | `POST` | `/study-abroad/parse-resume/` | `FormData (file: .pdf/.docx)` |
| **14**| Study Abroad | Country Categories | `GET` | `/study-abroad/country-categories/` | — |
| **15**| Work & Study | List Packages | `GET` | `/work-study/packages/` | — |
| **16**| Work & Study | Create Package | `POST` | `/work-study/packages/` | `{ title, category, stipend, training_duration, roles: [], streams: [] }` |
| **17**| Work & Study | Promote to Marketing | `POST` | `/work-study/packages/{id}/promote-jd/` | `{ channels: ["LinkedIn", "Meta"], target_region: "India" }` |
| **18**| Work & Study | Candidates ATS | `GET` | `/work-study/candidates/` | — |
| **19**| Work & Study | Candidate Stage Advance| `POST` | `/work-study/candidates/{id}/advance-stage/` | `{ stage: string, progress_pct: number }` |
| **20**| Jobs | Partner Companies | `GET/POST` | `/jobs/companies/` | `{ name, domain, city, country, logo_url }` |
| **21**| Jobs | Job Listings | `GET/POST` | `/jobs/listings/` | `?domain={domain}&country={country}&blue_card=true` |
| **22**| Jobs | Upload Candidate Resume| `POST` | `/jobs/resumes/` | `{ candidate_name, candidate_email, field, primary_skills: [], german_level }` |
| **23**| Jobs | Run AI Match on Resume | `POST/GET`| `/jobs/resumes/{id}/run-job-match/` | Compares skills against all active listings |
| **24**| Communication | Workflow Rules | `GET/POST` | `/communication/workflows/` | `{ trigger_event, channel, message_template, is_active }` |
| **25**| Communication | Toggle Workflow Active | `POST` | `/communication/workflows/{id}/toggle-active/` | — |
| **26**| Communication | Simulate Dispatch | `POST` | `/communication/workflows/simulate-trigger/` | `{ workflow_id, student_name, student_email, student_phone, course_track }` |
| **27**| Communication | Dispatch Audit Logs | `GET` | `/communication/logs/` | — |
| **28**| Intake Tracking| Department Inquiries | `GET/POST` | `/intake/inquiries/` | `?department={dept}&status={status}` |
| **29**| Intake Tracking| Follow-up Triggers | `GET/POST` | `/intake/triggers/` | `?department={dept}` |
| **30**| Intake Tracking| Trigger Simulation | `POST` | `/intake/triggers/{id}/simulate-execution/` | — |
| **31**| Intake Tracking| Social Media Campaigns | `GET/POST` | `/intake/campaigns/` | `?department={dept}` |
| **32**| Intake Tracking| Broadcast Live Campaign| `POST` | `/intake/campaigns/{id}/broadcast-live/` | — |
| **33**| Rewards Plan | List Loyalty Plans | `GET` | `/rewards/plans/` | — |
| **34**| Rewards Plan | Points Earning Rules | `GET/POST` | `/rewards/rules/` | `{ trigger_event, points_awarded, description }` |
| **35**| Rewards Plan | Rewards Catalog Items | `GET/POST` | `/rewards/catalog/` | `{ title, points_required, reward_type, voucher_code }` |
| **36**| Rewards Plan | Student Redemptions | `GET/POST` | `/rewards/redemptions/` | `{ student_account_id, item_id }` |
| **37**| Rewards Plan | Broadcast Promotion | `POST` | `/rewards/broadcast-promo/` | `{ campaign_title, message_copy, channels: [] }` |

---

## 4. Section 1: Study Abroad, ATS & AI Resume Parser

### 1.1 AI Resume Parser Endpoint
Takes an uploaded PDF or Word resume and automatically extracts structured candidate parameters.

```typescript
// Call Resume Parser
const formData = new FormData();
formData.append('file', file);
const parsed = await ilaAppClient.uploadFile<ParsedResumeResponse>('/study-abroad/parse-resume/', formData);
```

**Response Body:**
```json
{
  "name": "Arjun Sharma",
  "email": "arjun.sharma@gmail.com",
  "phone": "+91 9876543210",
  "course_duration": "2 Years (Masters)",
  "work_experience": "2.5 Years Full-Stack Development",
  "transcript_score": "8.4 CGPA",
  "field_of_interest": "Computer Science & Artificial Intelligence",
  "language_score": "IELTS 7.5 Academic (German A2)",
  "raw_text_snippet": "Arjun Sharma | B.Tech CSE | CGPA: 8.4..."
}
```

### 1.2 Profile Matcher Endpoint
Evaluates eligibility across all university course tracks with real-time match scoring (0-99%).

```typescript
const matchResults = await ilaAppClient.post('/study-abroad/profile-match/', {
  country_id: 1,
  cgpa: 8.2,
  ielts: 7.0,
  german_level: "B1"
});
```

---

## 5. Section 2: Work & Study Hub

### 2.1 Promote Job Description to Marketing
```typescript
const res = await ilaAppClient.post('/work-study/packages/WSP-PKG-01/promote-jd/', {
  channels: ["LinkedIn Ads", "Meta Ads", "WhatsApp Blast"],
  target_region: "India / Kerala"
});
```

### 2.2 Candidate ATS Stage Progression
```typescript
const res = await ilaAppClient.post('/work-study/candidates/1/advance-stage/', {
  stage: "Corporate Pilot",
  progress_pct: 75
});
```

---

## 6. Section 3: Job Search, Candidates & Match Engine

### 3.1 Run Dynamic Job Match for Candidate
```typescript
const matches = await ilaAppClient.post('/jobs/resumes/1/run-job-match/');
```

**Response:**
```json
{
  "candidate_name": "Priya Nair",
  "matches": [
    {
      "job_id": 1,
      "job_title": "Junior Python / Django Developer",
      "company_name": "Siemens AG",
      "location": "Munich, Germany",
      "salary_range": "€55,000 - €65,000",
      "match_score": 92,
      "matched_skills": ["Python", "Django", "REST APIs"],
      "is_high_fit": true
    }
  ]
}
```

---

## 7. Section 4: Automated Communication Engine

### 7.1 Simulate Real-Time Multi-Channel Dispatch
```typescript
const result = await ilaAppClient.post('/communication/workflows/simulate-trigger/', {
  workflow_id: 1,
  student_name: "Rahul Menon",
  student_email: "rahul@gmail.com",
  student_phone: "+91 9447001122",
  course_track: "German Language A1 Intensive"
});
```

---

## 8. Section 5: Front Office Intake & Campaign Tracking

### 8.1 Broadcast Social Media Campaign Live
```typescript
const result = await ilaAppClient.post('/intake/campaigns/1/broadcast-live/');
```

---

## 9. Section 6: Rewards & Loyalty Engine

### 9.1 Broadcast Live Promotion Campaign
```typescript
const result = await ilaAppClient.post('/rewards/broadcast-promo/', {
  campaign_title: "10,000 Bonus Coins for Germany Winter 2026 Batch",
  message_copy: "Enroll before Oct 30 and unlock verified flight ticket discounts!",
  channels: ["Meta Ads", "LinkedIn", "WhatsApp Broadcast"]
});
```

---

## 10. TypeScript Domain Type Definitions

Create `src/types/ilaApp.ts`:

```typescript
// src/types/ilaApp.ts

// --- Study Abroad Types ---
export interface Country {
  id: number;
  name: string;
  code: string;
  flag: string;
  visa_type: string;
  currency: string;
  avg_tuition: string;
  living_cost: string;
  description: string;
  status: 'Active' | 'Coming Soon';
  created_at: string;
}

export interface College {
  id: number;
  country: number;
  country_name?: string;
  name: string;
  city: string;
  ranking: string;
  institution_type: 'Public' | 'University of Applied Sciences' | 'Technical University' | 'Private';
  admission_criteria: string;
  terms: string[];
  contact_email: string;
  status: 'Active' | 'Partnered' | 'Under Review';
}

export interface StudyAbroadCourse {
  id: number;
  country: number;
  country_name?: string;
  college: number;
  college_name?: string;
  course_name: string;
  degree: 'Bachelors' | 'Masters' | 'Ausbildung / Dual' | 'Doctorate (PhD)' | 'Language Pathway';
  duration: string;
  intake_semesters: string;
  tuition_per_year: string;
  min_cgpa: number;
  min_ielts: number;
  min_german_level: string;
  status: string;
}

export interface ConsultantATSTask {
  id: number;
  student_account_id: string;
  student_name: string;
  student_email: string;
  student_phone: string;
  target_country: string;
  target_course: string;
  match_score: number;
  stage: 'Lead / Intake' | 'Document Verification' | 'University Review' | 'Interview Scheduled' | 'Visa Preparation' | 'Enrolled' | 'Closed / Dropped';
  assigned_consultant: string;
  uploaded_documents: {
    checklistId: string;
    docName: string;
    fileName: string;
    fileSize: string;
    uploadedAt: string;
    verified: boolean;
  }[];
  consultant_notes: {
    id: string;
    author: string;
    note: string;
    timestamp: string;
    nextFollowUpDate?: string;
  }[];
  created_at: string;
  updated_at: string;
}

export interface ParsedResumeResponse {
  name: string;
  email: string;
  phone: string;
  course_duration: string;
  work_experience: string;
  transcript_score: string;
  field_of_interest: string;
  language_score: string;
  raw_text_snippet?: string;
}

// --- Work & Study Types ---
export interface WorkStudyPackage {
  id: string;
  category: string;
  category_label: string;
  title: string;
  badge: string;
  stipend: string;
  training_duration: string;
  internship_duration: string;
  certification: string;
  action_text: string;
  description: string;
  status: string;
  promoted_to_marketing: boolean;
  marketing_campaign_id?: string;
  roles: { id: number; title: string; order: number; is_milestone: boolean }[];
  streams: { id: number; name: string }[];
}

export interface WorkStudyCandidate {
  id: number;
  candidate_name: string;
  candidate_email: string;
  candidate_phone: string;
  package: number;
  package_title?: string;
  current_stage: string;
  progress_pct: number;
  stipend_earned: number;
}

// --- Job Search Types ---
export interface JobListing {
  id: number;
  title: string;
  company: number;
  company_name?: string;
  domain: string;
  city: string;
  country: string;
  salary_range: string;
  job_type: string;
  required_skills: string[];
  min_german_level: string;
  blue_card_eligible: boolean;
  status: string;
}

export interface CandidateResume {
  id: number;
  candidate_name: string;
  candidate_email: string;
  field: string;
  primary_skills: string[];
  german_level: string;
  experience_years: number;
}

// --- Communication Types ---
export interface CommunicationWorkflow {
  id: number;
  trigger_event: string;
  channel: 'WhatsApp' | 'Email' | 'SMS' | 'In-App Notification';
  message_template: string;
  is_active: boolean;
  total_dispatched: number;
  delivered_count: number;
}

// --- Intake Tracking Types ---
export interface DepartmentInquiry {
  id: number;
  full_name: string;
  phone: string;
  email: string;
  department: string;
  inquiry_text: string;
  source_campaign: string;
  status: 'New' | 'Contacted' | 'Converted' | 'Cold';
  created_at: string;
}
```

---

## 11. Complete React Custom Hooks Library

### Hook: `useStudyAbroadATS.ts`
```typescript
// src/hooks/useStudyAbroadATS.ts
import { useState, useEffect, useCallback } from 'react';
import { ilaAppClient } from '../services/api/ilaAppClient';
import { ConsultantATSTask, Country, StudyAbroadCourse, ParsedResumeResponse } from '../types/ilaApp';

export function useStudyAbroadATS() {
  const [tasks, setTasks] = useState<ConsultantATSTask[]>([]);
  const [countries, setCountries] = useState<Country[]>([]);
  const [courses, setCourses] = useState<StudyAbroadCourse[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchTasks = useCallback(async (stage?: string, search?: string) => {
    try {
      setLoading(true);
      const res = await ilaAppClient.get<ConsultantATSTask[]>('/study-abroad/ats-tasks/', { stage, search });
      setTasks(res);
    } finally {
      setLoading(false);
    }
  }, []);

  const advanceStage = async (taskId: number, newStage: string, author = 'Senior Consultant') => {
    const updated = await ilaAppClient.post<ConsultantATSTask>(`/study-abroad/ats-tasks/${taskId}/advance-stage/`, {
      stage: newStage,
      author,
    });
    setTasks(prev => prev.map(t => (t.id === taskId ? updated : t)));
    return updated;
  };

  const addNote = async (taskId: number, note: string, author = 'Consultant', nextFollowUp?: string) => {
    const updated = await ilaAppClient.post<ConsultantATSTask>(`/study-abroad/ats-tasks/${taskId}/log-note/`, {
      note,
      author,
      next_follow_up_date: nextFollowUp,
    });
    setTasks(prev => prev.map(t => (t.id === taskId ? updated : t)));
    return updated;
  };

  const parseResumeFile = async (file: File): Promise<ParsedResumeResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    return ilaAppClient.uploadFile<ParsedResumeResponse>('/study-abroad/parse-resume/', formData);
  };

  useEffect(() => {
    fetchTasks();
    ilaAppClient.get<Country[]>('/study-abroad/countries/').then(setCountries).catch(console.error);
    ilaAppClient.get<StudyAbroadCourse[]>('/study-abroad/courses/').then(setCourses).catch(console.error);
  }, [fetchTasks]);

  return { tasks, countries, courses, loading, fetchTasks, advanceStage, addNote, parseResumeFile };
}
```

---

## 12. React Component Wiring & UI Integration Examples

### Component: `StudyAbroadATSBoard.tsx`

```tsx
// src/components/StudyAbroadATSBoard.tsx
import React, { useState } from 'react';
import { useStudyAbroadATS } from '../hooks/useStudyAbroadATS';
import { ConsultantATSTask } from '../types/ilaApp';

const STAGES = [
  'Lead / Intake',
  'Document Verification',
  'University Review',
  'Interview Scheduled',
  'Visa Preparation',
  'Enrolled',
];

export const StudyAbroadATSBoard: React.FC = () => {
  const { tasks, loading, advanceStage, addNote } = useStudyAbroadATS();
  const [activeTask, setActiveTask] = useState<ConsultantATSTask | null>(null);
  const [noteText, setNoteText] = useState('');

  if (loading) {
    return <div className="p-8 text-center text-slate-400">Loading ILA ATS Pipeline...</div>;
  }

  return (
    <div className="flex flex-col h-full bg-slate-950 text-slate-100 p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-emerald-400">Study Abroad ATS & Admissions Tracker</h1>
          <p className="text-sm text-slate-400">Live Stage Workflow & Verification Logs</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4 flex-1 overflow-x-auto">
        {STAGES.map(stage => {
          const stageTasks = tasks.filter(t => t.stage === stage);
          return (
            <div key={stage} className="bg-slate-900 border border-slate-800 rounded-xl p-3 flex flex-col">
              <div className="flex justify-between items-center mb-3">
                <span className="font-semibold text-xs tracking-wider text-slate-300 uppercase">{stage}</span>
                <span className="bg-slate-800 text-emerald-400 text-xs px-2 py-0.5 rounded-full font-bold">
                  {stageTasks.length}
                </span>
              </div>

              <div className="flex-1 space-y-3 overflow-y-auto">
                {stageTasks.map(task => (
                  <div
                    key={task.id}
                    onClick={() => setActiveTask(task)}
                    className="p-3 bg-slate-800/80 hover:bg-slate-800 border border-slate-700/60 rounded-lg cursor-pointer transition shadow-sm"
                  >
                    <div className="flex justify-between items-start">
                      <h4 className="font-semibold text-sm text-slate-100">{task.student_name}</h4>
                      <span className="text-xs bg-emerald-500/20 text-emerald-300 font-bold px-1.5 py-0.5 rounded">
                        {task.match_score}%
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 mt-1">{task.target_course}</p>
                    <div className="mt-2 flex justify-between items-center text-[11px] text-slate-500">
                      <span>{task.target_country}</span>
                      <span>{task.uploaded_documents.length} Docs</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      {/* Task Drawer / Modal */}
      {activeTask && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-xl w-full p-6 space-y-4">
            <div className="flex justify-between items-start">
              <div>
                <h2 className="text-xl font-bold text-emerald-400">{activeTask.student_name}</h2>
                <p className="text-xs text-slate-400">{activeTask.student_email} • {activeTask.student_phone}</p>
              </div>
              <button onClick={() => setActiveTask(null)} className="text-slate-400 hover:text-white">✕</button>
            </div>

            <div>
              <label className="text-xs font-bold text-slate-400 uppercase">Current Stage</label>
              <select
                value={activeTask.stage}
                onChange={e => advanceStage(activeTask.id, e.target.value)}
                className="mt-1 w-full bg-slate-800 border border-slate-700 rounded-lg p-2 text-sm text-slate-100"
              >
                {STAGES.map(s => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>

            <div>
              <label className="text-xs font-bold text-slate-400 uppercase">Log Consultant Note</label>
              <div className="flex gap-2 mt-1">
                <input
                  type="text"
                  placeholder="Enter follow-up update..."
                  value={noteText}
                  onChange={e => setNoteText(e.target.value)}
                  className="flex-1 bg-slate-800 border border-slate-700 rounded-lg p-2 text-sm text-slate-100"
                />
                <button
                  onClick={async () => {
                    if (noteText) {
                      await addNote(activeTask.id, noteText);
                      setNoteText('');
                    }
                  }}
                  className="bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded-lg text-sm font-semibold"
                >
                  Save
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
```

---

### Component: `AIResumeParserModal.tsx`

```tsx
// src/components/AIResumeParserModal.tsx
import React, { useState } from 'react';
import { useStudyAbroadATS } from '../hooks/useStudyAbroadATS';
import { ParsedResumeResponse } from '../types/ilaApp';

export const AIResumeParserModal: React.FC<{ isOpen: boolean; onClose: () => void }> = ({ isOpen, onClose }) => {
  const { parseResumeFile } = useStudyAbroadATS();
  const [file, setFile] = useState<File | null>(null);
  const [parsing, setParsing] = useState(false);
  const [parsedData, setParsedData] = useState<ParsedResumeResponse | null>(null);

  if (!isOpen) return null;

  const handleUpload = async () => {
    if (!file) return;
    setParsing(true);
    try {
      const data = await parseResumeFile(file);
      setParsedData(data);
    } catch (err) {
      alert('Resume parsing failed: ' + err);
    } finally {
      setParsing(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 space-y-4">
        <h2 className="text-lg font-bold text-emerald-400">AI Resume Parser (Gemini Preview)</h2>
        <p className="text-xs text-slate-400">Upload candidate .pdf or .docx to automatically extract academic parameters.</p>

        <input
          type="file"
          accept=".pdf,.docx"
          onChange={e => setFile(e.target.files?.[0] || null)}
          className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2 text-sm text-slate-300"
        />

        <button
          onClick={handleUpload}
          disabled={!file || parsing}
          className="w-full bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-bold py-2 rounded-lg text-sm"
        >
          {parsing ? 'Parsing with AI...' : 'Extract Parameters'}
        </button>

        {parsedData && (
          <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2 text-xs">
            <div><span className="text-slate-400">Name:</span> <strong className="text-slate-200">{parsedData.name}</strong></div>
            <div><span className="text-slate-400">Email:</span> <span className="text-slate-200">{parsedData.email}</span></div>
            <div><span className="text-slate-400">Phone:</span> <span className="text-slate-200">{parsedData.phone}</span></div>
            <div><span className="text-slate-400">CGPA / Score:</span> <span className="text-emerald-400 font-bold">{parsedData.transcript_score}</span></div>
            <div><span className="text-slate-400">Language:</span> <span className="text-slate-200">{parsedData.language_score}</span></div>
            <div><span className="text-slate-400">Field:</span> <span className="text-slate-200">{parsedData.field_of_interest}</span></div>
          </div>
        )}

        <button onClick={onClose} className="w-full bg-slate-800 text-slate-300 py-2 rounded-lg text-sm font-semibold">
          Close
        </button>
      </div>
    </div>
  );
};
```
