"""Unified Curriculum and Subject-Topic Hierarchy Engine for EduMate.

Provides cross-level curriculum structures spanning Class 10, Intermediate, Diploma,
B.Tech, Degree, GATE, Government exams, and Placement preparation.
"""

from typing import Any, Dict, List, Optional
from backend.schemas import CurriculumLevelSchema


CURRICULUM_CATALOG: Dict[str, Dict[str, Any]] = {
    "class_10": {
        "id": "class_10",
        "title": "Telangana State Board SSC (TG SSC Class 10)",
        "description": "Official Telangana State SCERT Class 10 curriculum covering all 6 SSC papers: Mathematics, Physical Sciences, Biological Science, Social Studies (incl. Telangana Movement), English, and Telugu.",
        "icon": "GraduationCap",
        "streams": ["TG SSC Regular (All Subjects)", "POLYCET & TSRJC Entrance (MPC / BiPC)"],
        "curricula": {
            "TG SSC Regular (All Subjects)": [
                {
                    "subject": "Mathematics",
                    "chapters": [
                        {
                            "name": "Number Systems & Progressions",
                            "topics": [
                                {"name": "Real Numbers", "difficulty": "Medium", "concepts": ["Euclid's Division Lemma", "Fundamental Theorem of Arithmetic", "Proofs of Irrationality of √2, √3, √5", "Logarithms: log(xy), log(x/y), log(x^n), Change of Base"]},
                                {"name": "Sets", "difficulty": "Easy", "concepts": ["Roster and Set-builder forms", "Universal Set & Subsets", "Venn Diagrams", "Union A∪B, Intersection A∩B, Difference A-B", "Disjoint Sets"]},
                                {"name": "Progressions", "difficulty": "Medium", "concepts": ["Arithmetic Progression (AP): nth term an=a+(n-1)d, Sum Sn", "Geometric Progression (GP): common ratio r, nth term an=a·r^(n-1)"]}
                            ]
                        },
                        {
                            "name": "Algebra & Coordinate Geometry",
                            "topics": [
                                {"name": "Polynomials", "difficulty": "Medium", "concepts": ["Geometrical Meaning of Zeros", "Quadratic & Cubic Polynomials", "Zeros and Coefficients: α+β = -b/a, αβ = c/a", "Division Algorithm"]},
                                {"name": "Pair of Linear Equations", "difficulty": "Medium", "concepts": ["Graphical Method & Intersection Points", "Consistency Conditions (a1/a2, b1/b2, c1/c2)", "Substitution & Elimination Methods"]},
                                {"name": "Quadratic Equations", "difficulty": "Hard", "concepts": ["Standard Form ax²+bx+c=0", "Factorization & Method of Completing Square", "Quadratic Formula x = (-b±√(b²-4ac))/2a", "Discriminant b²-4ac & Nature of Roots"]},
                                {"name": "Coordinate Geometry", "difficulty": "Medium", "concepts": ["Distance Formula √((x₂-x₁)²+(y₂-y₁)²)", "Section Formula & Trisection Points", "Area of Triangle & Heron's Formula", "Slope of Line m = (y₂-y₁)/(x₂-x₁) = tanθ"]}
                            ]
                        },
                        {
                            "name": "Geometry, Mensuration & Trigonometry",
                            "topics": [
                                {"name": "Similar Triangles", "difficulty": "Hard", "concepts": ["Basic Proportionality Theorem (BPT/Thales Theorem) & Converse", "AAA, SSS, SAS Similarity Criteria", "Pythagoras Theorem & Converse"]},
                                {"name": "Tangents and Secants", "difficulty": "Medium", "concepts": ["Tangent Perpendicular to Radius", "Equal Tangent Lengths from External Point", "Area of Sector (θ/360 × πr²) & Segment"]},
                                {"name": "Mensuration", "difficulty": "Hard", "concepts": ["Cylinder, Cone, Sphere, Hemisphere", "Surface Areas & Volumes of Combined Solids", "Conversion of Shapes (Melting & Recasting)"]},
                                {"name": "Trigonometry", "difficulty": "Medium", "concepts": ["Trig Ratios (sin, cos, tan, cot, sec, cosec)", "Values at 0°, 30°, 45°, 60°, 90°", "Complementary Angles: sin(90°-A)=cosA", "Identities: sin²A+cos²A=1, 1+tan²A=sec²A, 1+cot²A=cosec²A"]},
                                {"name": "Applications of Trigonometry", "difficulty": "Hard", "concepts": ["Line of Sight", "Angle of Elevation & Depression", "Heights and Distances Multi-story & Tower Problems"]}
                            ]
                        },
                        {
                            "name": "Statistics & Probability",
                            "topics": [
                                {"name": "Statistics", "difficulty": "Medium", "concepts": ["Mean of Grouped Data (Direct, Assumed Mean, Step-deviation)", "Median and Mode of Grouped Data", "Cumulative Frequency: Less than & More than Ogive Curves"]},
                                {"name": "Probability", "difficulty": "Easy", "concepts": ["Probability Definition P(E) = n(E)/n(S)", "Complementary Events P(E)+P(not E)=1", "Deck of 52 Playing Cards, Coins, Dice Problems"]}
                            ]
                        }
                    ]
                },
                {
                    "subject": "Physical Sciences",
                    "chapters": [
                        {
                            "name": "Physics: Optics & Electromagnetism",
                            "topics": [
                                {"name": "Reflection of Light at Curved Surfaces", "difficulty": "Medium", "concepts": ["Concave & Convex Spherical Mirrors", "Ray Diagrams for Object at 6 Positions", "Mirror Formula 1/f = 1/v + 1/u & Magnification m = -v/u"]},
                                {"name": "Refraction of Light at Curved Surfaces", "difficulty": "Hard", "concepts": ["Convex & Concave Lenses", "Lens Formula 1/f = 1/v - 1/u", "Lens Maker's Formula 1/f = (n-1)(1/R1 - 1/R2)", "Power of Lens P = 1/f"]},
                                {"name": "Human Eye and Colourful World", "difficulty": "Medium", "concepts": ["Myopia (Nearsightedness) & Concave Lens Correction", "Hypermetropia & Convex Lens Correction", "Prism Dispersion & Rainbow", "Atmospheric Refraction & Light Scattering"]},
                                {"name": "Electric Current", "difficulty": "Hard", "concepts": ["Ohm's Law V = IR & Lab Verification", "Factors Affecting Resistance (R = ρl/A)", "Resistors in Series & Parallel", "Kirchhoff's Laws (Junction Law & Loop Law)"]},
                                {"name": "Electromagnetism", "difficulty": "Hard", "concepts": ["Magnetic Field Lines around Solenoid", "Faraday's Law of Induction & Lenz's Law", "Fleming's Left-Hand (Motor) & Right-Hand (Generator) Rules"]}
                            ]
                        },
                        {
                            "name": "Chemistry: Atomic Structure, Bonding & Reactions",
                            "topics": [
                                {"name": "Chemical Equations", "difficulty": "Easy", "concepts": ["Writing & Balancing Chemical Equations", "Physical States (s, l, g, aq)", "Exothermic & Endothermic Reactions"]},
                                {"name": "Acids, Bases, and Salts", "difficulty": "Medium", "concepts": ["Indicators & Metal/Carbonate Reactions", "pH Scale & Daily Life Importance", "Chlor-Alkali Process, Bleaching Powder, Baking Soda, Plaster of Paris"]},
                                {"name": "Structure of Atom", "difficulty": "Hard", "concepts": ["Bohr-Sommerfeld Model & Elliptical Orbits", "Quantum Numbers: n, l, m_l, m_s", "Aufbau Principle, Pauli's Exclusion Principle, Hund's Rule", "Electronic Configuration of Elements 1 to 30"]},
                                {"name": "Classification of Elements", "difficulty": "Medium", "concepts": ["Mendeleev vs Modern Periodic Table", "Groups, Periods, s/p/d/f Blocks", "Periodic Trends: Atomic Radius, Ionization Energy, Electronegativity"]},
                                {"name": "Chemical Bonding", "difficulty": "Hard", "concepts": ["Ionic vs Covalent Bonds (NaCl, MgCl2, H2, O2)", "VSEPR Theory & Molecular Shapes", "Hybridization: sp, sp², sp³ (BeCl2, BF3, CH4, NH3, H2O)"]},
                                {"name": "Principles of Metallurgy", "difficulty": "Medium", "concepts": ["Froth Floatation, Calcination, Roasting, Smelting", "Reactivity Series in Extraction", "Refining Methods & Corrosion Prevention"]},
                                {"name": "Carbon and its Compounds", "difficulty": "Hard", "concepts": ["Allotropes: Diamond, Graphite, Fullerenes C60, Nanotubes", "Hydrocarbons & IUPAC Nomenclature", "Functional Groups (Alcohols, Aldehydes, Ketones, Acids)", "Soaps, Detergents & Micelle Action"]}
                            ]
                        }
                    ]
                },
                {
                    "subject": "Biological Science",
                    "chapters": [
                        {
                            "name": "Life Processes & Energy Systems",
                            "topics": [
                                {"name": "Nutrition", "difficulty": "Medium", "concepts": ["Chloroplast Structure & Light/Dark Reactions", "Human Digestive System & Enzyme Action", "Malnutrition Diseases (Kwashiorkor, Marasmus, Pellagra)"]},
                                {"name": "Respiration", "difficulty": "Medium", "concepts": ["Aerobic vs Anaerobic Respiration", "Pathway of Air & Alveolar Exchange", "Cellular Respiration: Glycolysis & Fermentation"]},
                                {"name": "Transportation", "difficulty": "Hard", "concepts": ["Internal Structure of Human Heart", "Systemic & Pulmonary Double Circulation", "Cardiac Cycle & Blood Clotting", "Xylem Transpiration Pull & Root Pressure"]}
                            ]
                        },
                        {
                            "name": "Excretion, Coordination & Reproduction",
                            "topics": [
                                {"name": "Excretion", "difficulty": "Hard", "concepts": ["Structure of Kidney & Nephron (Malpighian Body, Renal Tubule)", "Mechanism of Urine Formation (Filtration, Reabsorption, Secretion)", "Hemodialysis & Kidney Transplantation", "Plant Secondary Metabolites (Alkaloids, Tannins, Gums, Latex)"]},
                                {"name": "Control and Coordination", "difficulty": "Hard", "concepts": ["Neuron Structure & Reflex Arc", "Central Nervous System: Brain Anatomy & Spinal Cord", "Plant Hormones (Auxins, Gibberellins, Cytokinins, ABA, Ethylene)", "Endocrine Glands (Pituitary, Thyroid, Adrenal, Pancreas)"]},
                                {"name": "Reproduction", "difficulty": "Medium", "concepts": ["Asexual: Fission, Budding, Spore Formation", "Sexual Reproduction in Flowering Plants", "Human Male & Female Reproductive Systems", "Menstrual Cycle & Contraception", "Mitosis vs Meiosis Cell Division"]},
                                {"name": "Coordination in Life Processes", "difficulty": "Easy", "concepts": ["Hunger Pangs & Ghrelin/Leptin Hormones", "Taste Buds & Smell Coordination", "Peristalsis in Esophagus & Digestive Regulation"]}
                            ]
                        },
                        {
                            "name": "Heredity & Environment",
                            "topics": [
                                {"name": "Heredity", "difficulty": "Hard", "concepts": ["Mendel's Pea Plant Experiments (Pisum sativum)", "Monohybrid Cross (3:1) & Dihybrid Cross (9:3:3:1)", "Sex Determination in Humans (XX / XY)", "Lamarckism vs Darwinism (Natural Selection)", "Homologous and Analogous Organs, Fossils"]},
                                {"name": "Our Environment & Natural Resources", "difficulty": "Easy", "concepts": ["Trophic Levels & 10% Energy Transfer Law", "Ecological Pyramids (Number, Biomass, Energy)", "Bioaccumulation & Biomagnification of Pesticides", "Water Conservation, ICRISAT Watershed Model, Check Dams, 4 R's Principle"]}
                            ]
                        }
                    ]
                },
                {
                    "subject": "Social Studies",
                    "chapters": [
                        {
                            "name": "Part I: Geography & Economics",
                            "topics": [
                                {"name": "India: Relief Features & Climate", "difficulty": "Medium", "concepts": ["Himalayas, Indo-Gangetic Plains, Peninsular Plateau, Coastal Plains, Thar Desert", "Indian Monsoon Mechanism & Climatic Controls", "Himalayan vs Peninsular River Systems"]},
                                {"name": "Production, Employment & Population", "difficulty": "Medium", "concepts": ["Primary, Secondary, Tertiary Economic Sectors", "Organized vs Unorganized Sector Employment", "Census Data, Density, Sex Ratio, Literacy Trends"]},
                                {"name": "Food Security & Sustainable Development", "difficulty": "Easy", "concepts": ["Public Distribution System (PDS) & Ration Shops", "Nutrition & Buffer Stock", "Sustainable Development with Equity"]}
                            ]
                        },
                        {
                            "name": "Part II: History & Political Processes",
                            "topics": [
                                {"name": "World Between Wars 1900-1950", "difficulty": "Medium", "concepts": ["Causes of World War I & Treaty of Versailles", "Russian Revolution & Great Economic Depression 1929", "Rise of Nazism in Germany & World War II", "Formation of United Nations (UNO)"]},
                                {"name": "National Movement & Independence", "difficulty": "Medium", "concepts": ["Quit India Movement 1942 & INA Subhash Chandra Bose", "Mountbatten Plan & Partition 1947", "Integration of Princely States (Hyderabad Police Action)"]},
                                {"name": "Making of Constitution & Democratic Process", "difficulty": "Medium", "concepts": ["Constituent Assembly Drafting Committee (Dr. B.R. Ambedkar)", "Preamble, Fundamental Rights & Federal Structure", "Election Commission of India & Model Code of Conduct"]},
                                {"name": "Telangana Movement & State Formation", "difficulty": "Hard", "concepts": ["Gentlemen's Agreement 1956 & Violations", "1969 Telangana Agitation & Jai Telangana Slogan", "Mulki Rules & G.O. 610", "Telangana Joint Action Committee (TJAC), Million March, Sakala Janula Samme", "Srikrishna Committee Report", "AP Reorganisation Act 2014 & Telangana Statehood on June 2, 2014"]}
                            ]
                        }
                    ]
                },
                {
                    "subject": "Third Language: English",
                    "chapters": [
                        {
                            "name": "Units 1 to 4: Personality, Humour, Relations & Films",
                            "topics": [
                                {"name": "Unit 1: Personality Development", "difficulty": "Easy", "concepts": ["Attitude is Altitude (Nick Vujicic Biography)", "Every Success Story is also a Story of Great Failures", "I will do it (Narayan Murthy Story)"]},
                                {"name": "Unit 2: Wit and Humour", "difficulty": "Easy", "concepts": ["The Dear Departed Play (Part 1 & 2)", "The Brave Potter (Folk Tale)"]},
                                {"name": "Unit 3: Human Relations & Films", "difficulty": "Medium", "concepts": ["The Journey (Father and Son Narrative)", "Rendezvous with Ray (Satyajit Ray)", "Maya Bazaar (Classic Cinema Tribute)"]}
                            ]
                        },
                        {
                            "name": "Units 5 to 8 & Discourse Writing",
                            "topics": [
                                {"name": "Social Issues, Bio-diversity & Human Rights", "difficulty": "Medium", "concepts": ["The Storeyed House (Caste Issues)", "Environment & Wangari Maathai", "Unity in Diversity in India", "Jamaican Fragment & Once Upon a Time"]},
                                {"name": "Major & Minor Discourses", "difficulty": "Medium", "concepts": ["Formal & Informal Letter Writing", "Diary Entry & Biographical Sketch", "Speech Writing & Notice Preparation", "Editing, Relative Clauses, Reported Speech, Passive Voice"]}
                            ]
                        }
                    ]
                },
                {
                    "subject": "First Language: Telugu",
                    "chapters": [
                        {
                            "name": "Poetry & Prose Literature (Sahityam)",
                            "topics": [
                                {"name": "Classical & Modern Poetry", "difficulty": "Medium", "concepts": ["Mathrubhavana (Motherland Adoration)", "Sathakamadhurima (Moral Verses)", "Samudrollanghanam (Hanuman Saga)", "Bhiksha (Srinatha Classical Style)"]},
                                {"name": "Prose & Telangana Identity", "difficulty": "Medium", "concepts": ["Nagarageetham (Urban Life)", "Bhagyodayam (Bhagya Reddy Varma Dalit Upliftment)", "Lakshyasiddhi (Telangana Statehood)", "Golconda Fort (Historical Glory)"]}
                            ]
                        },
                        {
                            "name": "Non-Detail & Grammar (Ramayana & Vyakaranam)",
                            "topics": [
                                {"name": "Ramayana Non-Detail (6 Kandas)", "difficulty": "Easy", "concepts": ["Bala Kanda, Ayodhya Kanda, Aranya Kanda", "Kishkindha Kanda, Sundara Kanda, Yuddha Kanda Character Analysis"]},
                                {"name": "Sandhulu, Samasalu, Chandassu & Alankaralu", "difficulty": "Hard", "concepts": ["Sandhulu: Savarnadeergha, Guna, Vriddhi, Yanadesha, Trika, Utva, Itva", "Samasalu: Dvandva, Dvigu, Tatpurusha, Bahuvrihi, Rupaka", "Chandassu: Utpalamala, Champakamala, Shardoolam, Mattebham", "Alankaralu: Vrutyanuprasa, Chekanuprasa, Upama, Rupaka, Utpreksha"]}
                            ]
                        }
                    ]
                }
            ],
            "POLYCET & TSRJC Entrance (MPC / BiPC)": [
                {
                    "subject": "Mathematics (POLYCET Spec)",
                    "chapters": [
                        {
                            "name": "POLYCET 60-Marks Mathematics Fast-Track",
                            "topics": [
                                {"name": "Real Numbers & Sets MCQ Mastery", "difficulty": "Medium", "concepts": ["Logarithm Laws Application Shortcuts", "Venn Diagram Set Count Formulae", "Terminating & Non-Terminating Decimals"]},
                                {"name": "Polynomials & Quadratic Equations Speed Drill", "difficulty": "Hard", "concepts": ["Location of Roots", "Condition for Common Roots", "Maximum/Minimum value of quadratic polynomial"]},
                                {"name": "Trigonometry & Coordinate Geometry Shortcuts", "difficulty": "Hard", "concepts": ["Collinear Points Slope Technique", "Area of Triangle Shortcut", "Identities Elimination in 30 seconds"]}
                            ]
                        }
                    ]
                },
                {
                    "subject": "Physics (POLYCET Spec)",
                    "chapters": [
                        {
                            "name": "Physics 30-Marks Fast-Track",
                            "topics": [
                                {"name": "Optics & Lens Maker Formula Problems", "difficulty": "Hard", "concepts": ["Focal Length of Cut Lenses", "Equivalent Power of Lenses in Contact", "Sign Convention Pitfalls"]},
                                {"name": "Current Electricity & Circuits Numerical", "difficulty": "Hard", "concepts": ["Kirchhoff's Junction & Loop Law Simplifications", "Wheatstone Bridge Principle", "Resistor Cube & Symmetry Networks"]}
                            ]
                        }
                    ]
                },
                {
                    "subject": "Chemistry (POLYCET Spec)",
                    "chapters": [
                        {
                            "name": "Chemistry 30-Marks Fast-Track",
                            "topics": [
                                {"name": "Atomic Structure & Periodic Trends", "difficulty": "Medium", "concepts": ["Quantum Number Combinations (n+l rule)", "Exceptional Configurations Cr & Cu", "Ionization Potential Anomalies (N > O, Be > B)"]},
                                {"name": "Chemical Bonding & Metallurgy", "difficulty": "Medium", "concepts": ["Bond Angle Comparisons (CH4, NH3, H2O)", "Froth Floatation Collectors & Frothers", "Blast Furnace Chemical Reactions"]}
                            ]
                        }
                    ]
                }
            ]
        }
    },
    "intermediate": {
        "id": "intermediate",
        "title": "Class 11–12 / Intermediate",
        "description": "Pre-university higher secondary education for Science, Commerce, and Arts.",
        "icon": "BookOpen",
        "streams": ["Science (MPC - Math, Physics, Chem)", "Science (BiPC - Biology, Physics, Chem)", "Commerce & Economics"],
        "curricula": {
            "Science (MPC - Math, Physics, Chem)": [
                {
                    "subject": "Mathematics",
                    "chapters": [
                        {
                            "name": "Calculus",
                            "topics": [
                                {"name": "Limits and Continuity", "difficulty": "Medium", "concepts": ["L'Hopital's Rule", "Squeeze Theorem", "Standard Limits"]},
                                {"name": "Differentiation & Applications", "difficulty": "Hard", "concepts": ["Chain Rule", "Maxima and Minima", "Rate of Change"]},
                                {"name": "Indefinite & Definite Integrals", "difficulty": "Hard", "concepts": ["Substitution", "Integration by Parts", "Area Under Curves"]}
                            ]
                        },
                        {
                            "name": "Algebra & Vectors",
                            "topics": [
                                {"name": "Matrices and Determinants", "difficulty": "Medium", "concepts": ["Matrix Inversion", "Cramer's Rule", "Eigenvalues intro"]},
                                {"name": "Vectors and 3D Geometry", "difficulty": "Hard", "concepts": ["Dot & Cross Product", "Direction Cosines", "Planes in 3D"]}
                            ]
                        }
                    ]
                },
                {
                    "subject": "Physics",
                    "chapters": [
                        {
                            "name": "Mechanics",
                            "topics": [
                                {"name": "Laws of Motion & Friction", "difficulty": "Medium", "concepts": ["Newton's Laws", "Free Body Diagrams", "Frictional Forces"]},
                                {"name": "Work, Energy, and Power", "difficulty": "Medium", "concepts": ["Work-Energy Theorem", "Conservation of Energy", "Collisions"]},
                                {"name": "Rotational Motion", "difficulty": "Hard", "concepts": ["Moment of Inertia", "Torque", "Angular Momentum Conservation"]}
                            ]
                        },
                        {
                            "name": "Electromagnetism",
                            "topics": [
                                {"name": "Electrostatics & Capacitance", "difficulty": "Hard", "concepts": ["Coulomb's Law", "Gauss Law", "Capacitor Networks"]},
                                {"name": "Current Electricity & Magnetism", "difficulty": "Medium", "concepts": ["Kirchhoff's Laws", "Wheatstone Bridge", "Biot-Savart Law"]}
                            ]
                        }
                    ]
                },
                {
                    "subject": "Chemistry",
                    "chapters": [
                        {
                            "name": "Physical Chemistry",
                            "topics": [
                                {"name": "Thermodynamics & Equilibrium", "difficulty": "Hard", "concepts": ["First & Second Laws", "Enthalpy & Entropy", "Le Chatelier Principle"]},
                                {"name": "Chemical Kinetics & Electrochemistry", "difficulty": "Medium", "concepts": ["Rate Laws", "Nernst Equation", "Faraday's Laws"]}
                            ]
                        },
                        {
                            "name": "Organic Chemistry",
                            "topics": [
                                {"name": "Hydrocarbons & Reaction Mechanisms", "difficulty": "Hard", "concepts": ["Electrophilic Addition", "SN1 & SN2 Mechanisms", "Markovnikov Rule"]}
                            ]
                        }
                    ]
                }
            ]
        }
    },
    "btech": {
        "id": "btech",
        "title": "B.Tech / Engineering",
        "description": "Comprehensive undergraduate engineering degree covering technical core, coding, and architecture.",
        "icon": "Cpu",
        "streams": ["Computer Science & Engineering", "Electronics & Communication", "Mechanical Engineering", "Electrical Engineering"],
        "curricula": {
            "Computer Science & Engineering": [
                {
                    "subject": "Data Structures & Algorithms",
                    "chapters": [
                        {
                            "name": "Trees & Graphs",
                            "topics": [
                                {"name": "Binary Search Trees", "difficulty": "Medium", "concepts": ["Insertion & Deletion", "BST Invariants", "Tree Traversals"]},
                                {"name": "Balanced Trees & AVL Rotations", "difficulty": "Hard", "concepts": ["Balance Factor", "LL/RR/LR/RL Rotations", "Height Bounds"]},
                                {"name": "Graph Traversal & Shortest Path", "difficulty": "Hard", "concepts": ["BFS / DFS", "Dijkstra Algorithm", "Bellman-Ford", "Floyd-Warshall"]}
                            ]
                        },
                        {
                            "name": "Dynamic Programming",
                            "topics": [
                                {"name": "0/1 Knapsack Problem", "difficulty": "Hard", "concepts": ["Tabulation", "Memoization", "Space Optimization"]},
                                {"name": "Longest Common Subsequence", "difficulty": "Hard", "concepts": ["Optimal Substructure", "Overlapping Subproblems", "Reconstruction"]}
                            ]
                        }
                    ]
                },
                {
                    "subject": "Operating Systems",
                    "chapters": [
                        {
                            "name": "Process Management",
                            "topics": [
                                {"name": "CPU Scheduling Algorithms", "difficulty": "Medium", "concepts": ["Round Robin", "SJF / Preemptive", "Gantt Charts", "Turnaround Time"]},
                                {"name": "Process Synchronization", "difficulty": "Hard", "concepts": ["Race Conditions", "Peterson Algorithm", "Semaphores & Mutexes"]},
                                {"name": "Deadlock Avoidance & Banker Algorithm", "difficulty": "Hard", "concepts": ["Coffman Conditions", "Resource Allocation Graph", "Safety State Analysis"]}
                            ]
                        },
                        {
                            "name": "Memory Management",
                            "topics": [
                                {"name": "Virtual Memory & Paging", "difficulty": "Medium", "concepts": ["Page Tables", "TLB Translation", "Page Replacement (LRU, FIFO)"]}
                            ]
                        }
                    ]
                },
                {
                    "subject": "Database Management Systems",
                    "chapters": [
                        {
                            "name": "Storage & Normalization",
                            "topics": [
                                {"name": "Relational Normalization", "difficulty": "Medium", "concepts": ["1NF, 2NF, 3NF, BCNF", "Functional Dependencies", "Lossless Join Decomposition"]},
                                {"name": "B+ Tree Indexing & Query Optimization", "difficulty": "Hard", "concepts": ["B+ Tree Fan-out", "Clustered vs Non-Clustered", "Cost-Based Query Optimization"]}
                            ]
                        },
                        {
                            "name": "Transactions",
                            "topics": [
                                {"name": "ACID Properties & Concurrency", "difficulty": "Hard", "concepts": ["Two-Phase Locking (2PL)", "Timestamp Ordering", "Serializability"]}
                            ]
                        }
                    ]
                },
                {
                    "subject": "Computer Networks",
                    "chapters": [
                        {
                            "name": "Transport & Network Layers",
                            "topics": [
                                {"name": "TCP Congestion Control & 3-Way Handshake", "difficulty": "Medium", "concepts": ["Slow Start", "Congestion Avoidance", "Fast Retransmit"]},
                                {"name": "IP Routing & Subnetting", "difficulty": "Medium", "concepts": ["CIDR", "Distance Vector vs Link State", "BGP Protocol"]}
                            ]
                        }
                    ]
                }
            ]
        }
    },
    "gate": {
        "id": "gate",
        "title": "GATE & Higher Entrance Exams",
        "description": "Rigorous national level entrance examination for PSU recruitment and M.Tech / PhD admissions.",
        "icon": "Award",
        "streams": ["GATE CSE & IT", "GATE ECE", "GATE Mechanical"],
        "curricula": {
            "GATE CSE & IT": [
                {
                    "subject": "Theory of Computation & Compiler Design",
                    "chapters": [
                        {
                            "name": "Automata & Grammars",
                            "topics": [
                                {"name": "DFA / NFA Equivalence & Minimization", "difficulty": "Medium", "concepts": ["Myhill-Nerode Theorem", "Regular Expressions", "Pumping Lemma"]},
                                {"name": "Context-Free Grammars & Pushdown Automata", "difficulty": "Hard", "concepts": ["Ambiguity", "Chomsky Hierarchy", "Decidability Table"]},
                                {"name": "LL(1) & LR Parsing", "difficulty": "Hard", "concepts": ["First and Follow Sets", "Shift-Reduce Conflicts", "SLR, CLR, LALR"]}
                            ]
                        }
                    ]
                },
                {
                    "subject": "Computer Organization & Architecture",
                    "chapters": [
                        {
                            "name": "Pipelines & Cache",
                            "topics": [
                                {"name": "Instruction Pipelining & Hazards", "difficulty": "Hard", "concepts": ["Data, Structural, Control Hazards", "Branch Prediction", "Speedup Ratio"]},
                                {"name": "Cache Memory Mapping & Miss Rates", "difficulty": "Hard", "concepts": ["Direct Mapped", "Set Associative", "Cache Miss Penalty & Hit Time"]}
                            ]
                        }
                    ]
                },
                {
                    "subject": "Discrete Mathematics & Engineering Math",
                    "chapters": [
                        {
                            "name": "Logic & Combinatorics",
                            "topics": [
                                {"name": "Propositional & First-Order Logic", "difficulty": "Medium", "concepts": ["Tautology", "Inference Rules", "Quantifiers"]},
                                {"name": "Combinatorics & Graph Theory", "difficulty": "Hard", "concepts": ["Generating Functions", "Eulerian & Hamiltonian Graphs", "Planar Graphs"]}
                            ]
                        }
                    ]
                }
            ]
        }
    },
    "govt_exams": {
        "id": "govt_exams",
        "title": "Competitive & Government Exams",
        "description": "General studies, quantitative aptitude, reasoning, and domain knowledge for UPSC, SSC, Banking, and State PSCs.",
        "icon": "Briefcase",
        "streams": ["Quantitative Aptitude & Reasoning", "UPSC / Civil Services", "Banking (IBPS / SBI PO)"],
        "curricula": {
            "Quantitative Aptitude & Reasoning": [
                {
                    "subject": "Quantitative Aptitude",
                    "chapters": [
                        {
                            "name": "Arithmetic & Algebra",
                            "topics": [
                                {"name": "Time, Speed, and Distance", "difficulty": "Medium", "concepts": ["Relative Speed", "Trains & Platforms", "Boats and Streams"]},
                                {"name": "Profit, Loss, and Percentage", "difficulty": "Easy", "concepts": ["Successive Discounts", "Marked Price", "Cost Price Ratios"]},
                                {"name": "Time and Work & Pipes", "difficulty": "Medium", "concepts": ["Efficiency Ratios", "Alternate Day Work", "Inlet & Outlet Pipes"]}
                            ]
                        }
                    ]
                },
                {
                    "subject": "Logical & Analytical Reasoning",
                    "chapters": [
                        {
                            "name": "Verbal & Non-Verbal Logic",
                            "topics": [
                                {"name": "Syllogisms & Deductive Logic", "difficulty": "Medium", "concepts": ["Venn Diagram Method", "Possibility Cases", "Neither-Nor Conditions"]},
                                {"name": "Seating Arrangements & Puzzles", "difficulty": "Hard", "concepts": ["Linear & Circular Seating", "Floor & Priority Puzzles"]}
                            ]
                        }
                    ]
                },
                {
                    "subject": "General Studies & Current Affairs",
                    "chapters": [
                        {
                            "name": "Indian Polity & Economy",
                            "topics": [
                                {"name": "Indian Constitution & Fundamental Rights", "difficulty": "Medium", "concepts": ["Preamble", "Articles 12-35", "Constitutional Amendments"]},
                                {"name": "Monetary Policy & Fiscal Budget", "difficulty": "Medium", "concepts": ["Repo & Reverse Repo Rate", "Inflation Types", "Fiscal Deficit"]}
                            ]
                        }
                    ]
                }
            ]
        }
    },
    "placement_prep": {
        "id": "placement_prep",
        "title": "Placement Preparation & Career Skills",
        "description": "Tech interview prep, problem solving, system design, and communication for top companies.",
        "icon": "Target",
        "streams": ["Software Engineering & Coding", "Data Engineering & Analytics", "Core Technical Placement"],
        "curricula": {
            "Software Engineering & Coding": [
                {
                    "subject": "Data Structures Coding Practice",
                    "chapters": [
                        {
                            "name": "High-Frequency Interview Patterns",
                            "topics": [
                                {"name": "Two Pointer & Sliding Window Patterns", "difficulty": "Medium", "concepts": ["Fast & Slow Pointers", "Variable Size Window", "Subarray Sums"]},
                                {"name": "Binary Search on Answer Space", "difficulty": "Hard", "concepts": ["Capacity to Ship Packages", "Aggressive Cows Pattern", "Monotonic Predicates"]}
                            ]
                        }
                    ]
                },
                {
                    "subject": "System Design & Architecture",
                    "chapters": [
                        {
                            "name": "Scalability & Distributed Systems",
                            "topics": [
                                {"name": "System Design Fundamentals", "difficulty": "Hard", "concepts": ["Load Balancers", "Horizontal Scaling", "CAP Theorem", "Sharding"]},
                                {"name": "Caching Strategies & Message Queues", "difficulty": "Hard", "concepts": ["Redis Caching Patterns", "Write-Through vs Write-Back", "Kafka & RabbitMQ"]}
                            ]
                        }
                    ]
                }
            ]
        }
    }
}


class CurriculumEngine:
    """Manages education levels, subjects, chapters, and topics across all curricula."""

    def get_education_levels(self) -> List[CurriculumLevelSchema]:
        """List all supported high-level education tiers."""
        return [
            CurriculumLevelSchema(
                id=cat["id"],
                title=cat["title"],
                description=cat["description"],
                icon=cat["icon"],
                streams=cat["streams"],
            )
            for cat in CURRICULUM_CATALOG.values()
        ]

    def get_streams_for_level(self, level_id: str) -> List[str]:
        """Fetch available streams or specializations for a given education level."""
        cat = CURRICULUM_CATALOG.get(level_id) or CURRICULUM_CATALOG.get("btech")
        return cat["streams"] if cat else []

    def get_subjects_hierarchy(self, level_id: str, stream: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve full subject -> chapter -> topic hierarchy for given level and stream."""
        cat = CURRICULUM_CATALOG.get(level_id)
        if not cat:
            # Fallback to B.Tech if not found
            cat = CURRICULUM_CATALOG["btech"]
        
        curricula = cat.get("curricula", {})
        active_stream = stream if stream and stream in curricula else list(curricula.keys())[0]
        return curricula.get(active_stream, [])

    def find_topic_meta(self, topic_name: str) -> Optional[Dict[str, Any]]:
        """Find topic metadata across any curriculum catalog."""
        search_lower = topic_name.strip().lower()
        for cat in CURRICULUM_CATALOG.values():
            for stream_subjects in cat.get("curricula", {}).values():
                for subj in stream_subjects:
                    for ch in subj.get("chapters", []):
                        for top in ch.get("topics", []):
                            if search_lower in top["name"].lower() or top["name"].lower() in search_lower:
                                return {
                                    "level": cat["title"],
                                    "subject": subj["subject"],
                                    "chapter": ch["name"],
                                    "topic": top["name"],
                                    "difficulty": top.get("difficulty", "Medium"),
                                    "concepts": top.get("concepts", []),
                                }
        return None


curriculum_engine = CurriculumEngine()
