"""Career Exploration and Pathway Blueprint Engine for EduMate.

Provides factual, structured career path data, prerequisite education degrees,
primary entrance examinations, essential syllabus subjects, and preparation roadmaps.
"""

from typing import Any, Dict, List, Optional
from backend.schemas import CareerPathSchema


CAREER_PATHS_DATABASE: List[Dict[str, Any]] = [
    {
        "id": "career-swe",
        "title": "Software Development Engineer (SDE)",
        "category": "Engineering & Technology",
        "description": "Designs, develops, and maintains scalable software applications, cloud systems, and core platforms.",
        "target_degrees": ["B.Tech / B.E (CSE/IT/ECE)", "MCA", "B.Sc Computer Science / BCA"],
        "primary_exams": ["Campus Placement Tests", "GATE CSE (for PSUs/R&D)", "Company Technical Coding Contests"],
        "core_subjects": ["Data Structures & Algorithms", "Operating Systems", "DBMS", "Computer Networks", "System Design"],
        "key_skills": ["Python / C++ / Java", "Git Version Control", "REST APIs", "SQL & NoSQL Databases", "Distributed Systems Basics"],
        "typical_roadmap": [
            "Year 1-2: Master Programming Fundamentals, Data Structures, and Discrete Math.",
            "Year 2-3: Core CS Theory (OS, DBMS, Networks) + Build full-stack projects.",
            "Year 3-4: Advanced Problem Solving (LeetCode / Codeforces) + System Design & Mock Interviews.",
            "Final Year: On-campus placement drives and off-campus tech applications."
        ]
    },
    {
        "id": "career-aiml",
        "title": "AI & Machine Learning Engineer",
        "category": "Engineering & Technology",
        "description": "Architects generative AI solutions, deep learning models, retrieval-augmented systems, and automated pipelines.",
        "target_degrees": ["B.Tech / M.Tech (CSE, AI, Data Science)", "M.Sc Statistics / Mathematics"],
        "primary_exams": ["GATE CSE / DA (Data Science & AI)", "GRE / GATE for M.Tech/MS Admissions"],
        "core_subjects": ["Linear Algebra & Calculus", "Probability & Statistics", "Machine Learning & Neural Networks", "Python & DSA"],
        "key_skills": ["PyTorch / TensorFlow", "Vector Databases & RAG", "LLM Fine-tuning", "Data Preprocessing (Pandas/NumPy)", "MLOps"],
        "typical_roadmap": [
            "Phase 1: Solid foundation in Multivariable Calculus, Probability, and Python programming.",
            "Phase 2: Classical ML algorithms (Linear/Logistic, SVM, Decision Trees, Ensembles).",
            "Phase 3: Deep Learning (CNNs, Transformers, Attention mechanisms) & Vector Search RAG.",
            "Phase 4: Open-source project portfolio & Research paper implementations."
        ]
    },
    {
        "id": "career-upsc",
        "title": "Civil Services (IAS / IPS / IFS)",
        "category": "Government & Public Administration",
        "description": "Key public leadership and policy execution roles in central and state governments.",
        "target_degrees": ["Graduation / Degree in any discipline (B.Tech, B.A, B.Sc, B.Com, etc.)"],
        "primary_exams": ["UPSC Civil Services Examination (Prelims, Mains, Interview)", "State PSCs"],
        "core_subjects": ["Indian Polity & Constitution", "Indian Economy", "Modern Indian History & Geography", "Ethics, Integrity, & Aptitude"],
        "key_skills": ["Critical Analytical Writing", "Public Policy Understanding", "Current Affairs Synthesis", "Decision Making"],
        "typical_roadmap": [
            "Month 1-6: Thorough NCERT foundational reading across Polity, History, Economy, and Geography.",
            "Month 7-12: Standard textbooks (Laxmikanth, Spectrum, Ramesh Singh) + Daily Newspaper Editorial Analysis.",
            "Month 13-18: Mains answer writing practice, optional subject preparation, and prelims test series.",
            "Final: Prelims simulation tests and Personality Test interview preparation."
        ]
    },
    {
        "id": "career-gate-psu",
        "title": "PSU Officer / M.Tech Research Scholar",
        "category": "Higher Education & Research",
        "description": "Technical executive in Navratna/Maharatna PSUs (ONGC, IOCL, NTPC, BHEL) or research scholar at premier IITs/IISc.",
        "target_degrees": ["B.Tech / B.E (Engineering in respective discipline)"],
        "primary_exams": ["GATE (Graduate Aptitude Test in Engineering)", "BARC / ISRO Centralised Recruitment"],
        "core_subjects": ["Engineering Mathematics", "General Aptitude", "Discipline Core Technical Subjects"],
        "key_skills": ["Rigorous Theoretical Depth", "Speed & Numerical Accuracy", "Conceptual Problem Solving"],
        "typical_roadmap": [
            "Semester 5-6: Complete 100% syllabus coverage of high-weightage core engineering subjects.",
            "Semester 7: Solve last 25 years of GATE previous year question papers (PYQs).",
            "Winter Break: Subject-wise and full-length simulated mock tests.",
            "February: GATE examination followed by CCMT / COAP admission counseling & PSU interviews."
        ]
    },
    {
        "id": "career-banking",
        "title": "Probationary Officer (IBPS / SBI PO)",
        "category": "Banking & Financial Services",
        "description": "Officer grade roles in premier nationalized and scheduled commercial banks managing credit and retail operations.",
        "target_degrees": ["Graduation in any discipline"],
        "primary_exams": ["SBI PO", "IBPS PO", "RBI Grade B Officer Examination"],
        "core_subjects": ["Quantitative Aptitude", "Reasoning Ability", "English Language", "General & Banking Awareness"],
        "key_skills": ["High-Speed Calculation", "Complex Seating Puzzles", "Data Interpretation", "Financial Literacy"],
        "typical_roadmap": [
            "Month 1-3: Master basic mental math, Vedic techniques, and arithmetic formulas.",
            "Month 4-6: Daily practice of high-level reasoning puzzles and sectional speed quizzes.",
            "Month 7-9: Comprehensive Banking Awareness and financial budget revisions.",
            "Month 10+: Prelims and Mains mock test series with time-bound accuracy tracking."
        ]
    }
]


class CareerEngine:
    """Provides career discovery, requirement matching, and exam guidance."""

    def list_paths(self) -> List[CareerPathSchema]:
        """Fetch all curated career paths."""
        return [CareerPathSchema(**cp) for cp in CAREER_PATHS_DATABASE]

    def get_path_detail(self, path_id: str) -> Optional[CareerPathSchema]:
        """Fetch details for a specific career pathway."""
        for cp in CAREER_PATHS_DATABASE:
            if cp["id"] == path_id:
                return CareerPathSchema(**cp)
        return None

    def get_recommended_paths(self, education_level: str) -> List[CareerPathSchema]:
        """Filter paths most relevant to student's current tier."""
        edu_lower = education_level.lower()
        if "10" in edu_lower or "intermediate" in edu_lower or "11" in edu_lower or "12" in edu_lower:
            # Emphasize foundational & entrance paths
            return [CareerPathSchema(**cp) for cp in CAREER_PATHS_DATABASE if "Engineering" in cp["category"] or "Government" in cp["category"]]
        return self.list_paths()


career_engine = CareerEngine()
