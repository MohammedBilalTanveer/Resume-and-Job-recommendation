"""
Skills taxonomy: canonical skill names, their aliases, categories,
related-skill groups (for partial credit) and a matcher that handles
symbols (C++, C#, .NET, CI/CD) and ambiguous words (Go, R, Spring, Excel).
"""

import re
from functools import lru_cache
from typing import Dict, List, Set, Tuple

# category -> {canonical name: [aliases (case-insensitive)]}
# The canonical name itself is always matched as an alias.
SKILLS: Dict[str, Dict[str, List[str]]] = {
    "programming_languages": {
        "Python": ["python3", "python 3"],
        "Java": ["java 8", "java 11", "java 17", "core java", "j2ee", "java ee"],
        "JavaScript": ["javascript", "js", "es6", "ecmascript", "vanilla js"],
        "TypeScript": ["ts"],
        "C++": ["cpp", "c plus plus"],
        "C#": ["c sharp", "csharp"],
        "Ruby": [], "Go": ["golang"], "R": ["r programming", "r language", "rstudio", "tidyverse", "ggplot2"],
        "C": ["c programming", "c language", "ansi c", "embedded c"], "Rust": [], "Kotlin": [], "PHP": [], "Scala": [],
        "Swift": [], "Objective-C": ["objective c", "objc"], "MATLAB": [], "Perl": [],
        "Dart": [], "Lua": [], "Haskell": [], "Elixir": [], "Clojure": [], "Julia": [],
        "Groovy": [], "VBA": ["visual basic"], "COBOL": [], "Fortran": [], "Solidity": [],
        "SQL": ["t-sql", "tsql", "pl/sql", "plsql", "ansi sql"],
        "HTML": ["html5"], "CSS": ["css3"], "Sass": ["scss"],
        "Bash": ["shell scripting", "shell script", "bash scripting", "zsh"],
        "PowerShell": [], "SAS": [], "Apex": [], "ABAP": [], "Assembly": ["assembly language"],
    },
    "frameworks_libraries": {
        "React": ["react.js", "reactjs", "react js"], "Angular": ["angularjs", "angular.js"],
        "Vue.js": ["vue", "vuejs", "vue js", "vue 3"], "Svelte": ["sveltekit"],
        "Next.js": ["nextjs", "next js"], "Nuxt.js": ["nuxt", "nuxtjs"], "Gatsby": [],
        "Node.js": ["nodejs", "node js", "node"], "Express.js": ["expressjs", "express js"],
        "NestJS": ["nest.js", "nestjs"], "Django": ["django rest framework", "drf"],
        "Flask": [], "FastAPI": ["fast api"], "Spring Boot": ["springboot", "spring framework", "spring mvc"],
        "Hibernate": [], ".NET": ["dotnet", ".net core", "dot net", ".net framework"],
        "ASP.NET": ["asp.net core", "asp .net"], "Ruby on Rails": ["rails", "ror"],
        "Laravel": [], "Symfony": [], "Redux": ["redux toolkit"], "MobX": [],
        "GraphQL": ["apollo graphql"], "jQuery": [], "Bootstrap": [], "Tailwind CSS": ["tailwind", "tailwindcss"],
        "Material UI": ["material-ui", "mui"], "React Native": [], "Flutter": [], "Ionic": [],
        "Xamarin": [], "SwiftUI": [], "Jetpack Compose": [], "Android": ["android sdk", "android development"],
        "iOS": ["ios development"], "Electron": [], "Three.js": ["threejs"], "D3.js": ["d3"],
        "TensorFlow": ["tensorflow 2", "tf2"], "PyTorch": ["torch"], "Keras": [],
        "scikit-learn": ["sklearn", "scikit learn"], "Pandas": [], "NumPy": [], "SciPy": [],
        "Matplotlib": [], "Seaborn": [], "Plotly": [], "OpenCV": [], "XGBoost": [], "LightGBM": [],
        "Hugging Face": ["huggingface", "hugging face transformers"], "LangChain": [], "LlamaIndex": [],
        "spaCy": [], "NLTK": [], "Apache Spark": ["spark", "pyspark", "spark sql"], "Hadoop": ["hdfs", "mapreduce"],
        "Kafka": ["apache kafka"], "Airflow": ["apache airflow"], "dbt": ["data build tool"],
        "RabbitMQ": [], "Celery": [], "JUnit": [], "pytest": [], "Jest": [], "Mocha": [],
        "Cypress": [], "Selenium": ["selenium webdriver"], "Playwright": [], "Puppeteer": [],
        "Unity": ["unity3d"], "Unreal Engine": ["unreal"], "Qt": [], "Streamlit": [], "Gradio": [],
    },
    "cloud_devops": {
        "AWS": ["amazon web services", "aws cloud"], "Azure": ["microsoft azure"],
        "GCP": ["google cloud", "google cloud platform"], "Docker": ["containerization", "docker compose"],
        "Kubernetes": ["k8s", "eks", "aks", "gke", "openshift"], "Helm": [], "Terraform": [],
        "Ansible": [], "Puppet": [], "Jenkins": [], "GitHub Actions": [], "GitLab CI": ["gitlab ci/cd"],
        "CircleCI": [], "Travis CI": [], "ArgoCD": ["argo cd"], "CI/CD": ["ci cd", "cicd", "continuous integration",
        "continuous delivery", "continuous deployment"], "CloudFormation": [], "AWS Lambda": ["lambda functions"],
        "EC2": ["amazon ec2"], "S3": ["amazon s3"], "ECS": ["fargate"], "Serverless": ["serverless framework"],
        "Heroku": [], "Vercel": [], "Netlify": [], "Firebase": [], "DigitalOcean": [], "Nginx": [],
        "Apache HTTP Server": ["apache httpd"], "Linux": ["ubuntu", "centos", "red hat", "rhel", "debian"],
        "Unix": [], "Prometheus": [], "Grafana": [], "Datadog": [], "Splunk": [], "New Relic": [],
        "ELK Stack": ["elk", "logstash", "kibana"], "Sentry": [], "Vagrant": [], "Istio": [],
        "Microservices": ["microservice", "micro-services", "microservices architecture"],
        "DevOps": ["devsecops"], "SRE": ["site reliability engineering", "site reliability"],
        "Networking": ["tcp/ip", "dns", "load balancing", "vpn"],
    },
    "databases": {
        "MySQL": [], "PostgreSQL": ["postgres", "psql"], "MongoDB": ["mongo"], "Redis": [],
        "Elasticsearch": ["elastic search", "opensearch"], "Cassandra": [], "DynamoDB": [],
        "SQLite": [], "Oracle Database": ["oracle db", "oracle sql", "oracle 19c"], "SQL Server": ["mssql", "ms sql",
        "microsoft sql server"], "MariaDB": [], "Neo4j": [], "CouchDB": [], "InfluxDB": [], "Memcached": [],
        "Snowflake": [], "BigQuery": [], "Redshift": [], "Databricks": [], "Firestore": [], "Supabase": [],
        "Pinecone": [], "Vector Databases": ["vector database", "vector db", "pgvector", "weaviate", "chromadb", "faiss"],
        "NoSQL": [], "Data Warehousing": ["data warehouse", "data warehousing"], "ETL": ["elt", "etl pipelines"],
        "Data Modeling": ["data modelling", "dimensional modeling"],
    },
    "data_science_ai": {
        "Machine Learning": ["ml", "machine-learning"], "Deep Learning": ["dl"],
        "NLP": ["natural language processing"], "Computer Vision": [], "Generative AI": ["genai", "gen ai", "generative ai"],
        "LLMs": ["llm", "large language models", "large language model"], "Prompt Engineering": [],
        "RAG": ["retrieval augmented generation", "retrieval-augmented generation"],
        "Data Analysis": ["data analytics", "data analyst", "analytics"], "Data Visualization": ["data viz", "dashboards", "dashboarding"],
        "Statistics": ["statistical analysis", "statistical modeling", "statistical modelling"],
        "A/B Testing": ["ab testing", "a/b tests", "experimentation", "split testing"],
        "Neural Networks": ["cnn", "rnn", "lstm", "neural network"], "Transformers": ["bert", "gpt"],
        "Reinforcement Learning": [], "Time Series": ["time series analysis", "forecasting"],
        "Feature Engineering": [], "MLOps": ["mlflow", "kubeflow", "model deployment"],
        "Predictive Modeling": ["predictive modelling", "predictive analytics"], "Data Mining": [],
        "Big Data": [], "Data Engineering": ["data pipelines", "data pipeline"], "Data Science": [],
        "Regression": ["linear regression", "logistic regression"], "Classification": [], "Clustering": [],
        "Recommendation Systems": ["recommender systems", "recommendation engine"],
    },
    "concepts_practices": {
        "REST APIs": ["rest", "restful", "rest api", "restful apis", "restful api", "api development", "web services"],
        "gRPC": [], "WebSockets": ["websocket", "socket.io"], "System Design": ["distributed systems", "scalable systems"],
        "OOP": ["object oriented programming", "object-oriented programming", "object oriented design"],
        "Data Structures": ["data structures and algorithms", "dsa"], "Algorithms": [],
        "Design Patterns": [], "Unit Testing": ["unit tests", "tdd", "test driven development", "test-driven development"],
        "Automation Testing": ["test automation", "automated testing", "qa automation"],
        "Manual Testing": ["qa testing", "quality assurance"], "Agile": ["agile methodology", "agile methodologies"],
        "Scrum": [], "Kanban": [], "Git": ["version control"], "Security": ["cybersecurity", "cyber security",
        "information security", "application security", "appsec"], "OAuth": ["oauth2", "oauth 2.0", "jwt", "sso"],
        "Penetration Testing": ["pentesting", "pen testing", "ethical hacking"], "SIEM": [],
        "Cloud Architecture": ["solutions architecture", "cloud computing"], "Performance Optimization": ["performance tuning"],
        "Responsive Design": ["responsive web design"], "Accessibility": ["wcag", "a11y"], "SEO": ["search engine optimization"],
        "UI/UX": ["ui", "ux", "user experience", "user interface", "ux design", "ui design"],
        "Backend Development": ["backend", "back-end", "back end", "server-side", "server side"],
        "Frontend Development": ["frontend", "front-end", "front end", "client-side"],
        "Full Stack Development": ["full stack", "full-stack", "fullstack", "mern", "mean stack"],
        "Web Development": ["web applications", "web apps", "web app", "web developer"],
        "Mobile Development": ["mobile app development", "mobile apps"], "Embedded Systems": ["embedded", "firmware", "rtos"],
        "Blockchain": ["web3", "smart contracts"], "IoT": ["internet of things"], "SDLC": [],
    },
    "tools_platforms": {
        "GitHub": [], "GitLab": [], "Bitbucket": [], "Jira": [], "Confluence": [], "Trello": [],
        "Asana": [], "Notion": [], "Slack": [], "Figma": [], "Sketch": [], "Adobe XD": [],
        "Photoshop": ["adobe photoshop"], "Illustrator": ["adobe illustrator"], "InDesign": ["adobe indesign"],
        "Premiere Pro": ["adobe premiere"], "After Effects": [], "Canva": [], "Postman": [], "Swagger": ["openapi"],
        "Tableau": [], "Power BI": ["powerbi"], "Looker": [], "Excel": ["excel spreadsheets", "ms excel", "microsoft excel",
        "advanced excel", "excel vba"], "Google Sheets": [], "PowerPoint": ["ms powerpoint"],
        "Microsoft Office": ["ms office", "microsoft 365", "office 365"], "Salesforce": ["sfdc"],
        "HubSpot": [], "SAP": ["sap erp", "sap s/4hana"], "QuickBooks": [], "Tally": ["tally erp"],
        "Zendesk": [], "ServiceNow": [], "Workday": [], "Google Analytics": ["ga4"], "Jupyter": ["jupyter notebook"],
        "VS Code": ["visual studio code"], "IntelliJ": ["intellij idea"], "AutoCAD": [], "SolidWorks": [],
        "Revit": [], "Blender": [], "Mailchimp": [], "SEMrush": [], "Shopify": [], "WordPress": [],
    },
    "business_finance": {
        "Financial Analysis": ["financial modeling", "financial modelling", "financial reporting"],
        "Accounting": ["bookkeeping", "accounts payable", "accounts receivable", "general ledger", "gaap", "ifrs"],
        "Budgeting": ["forecasting and budgeting", "budget management"], "Auditing": ["internal audit", "audit"],
        "Taxation": ["tax", "gst", "tax preparation"], "Risk Management": [], "Compliance": ["regulatory compliance"],
        "Business Analysis": ["business analyst", "requirements gathering", "brd"], "Product Management": ["product manager", "product roadmap"],
        "Project Management": ["project manager", "program management"], "Operations Management": ["operations"],
        "Supply Chain": ["supply chain management", "logistics", "procurement", "inventory management"],
        "Sales": ["b2b sales", "inside sales", "business development", "lead generation"],
        "CRM": ["customer relationship management"], "Customer Service": ["customer support", "client servicing"],
        "Recruitment": ["talent acquisition", "recruiting", "hiring"], "HR Management": ["human resources", "hrms", "payroll", "onboarding"],
        "Digital Marketing": ["online marketing", "performance marketing"], "Content Marketing": ["content writing", "copywriting", "content strategy"],
        "Social Media Marketing": ["social media", "smm"], "Email Marketing": [], "Market Research": [],
        "Brand Management": ["branding"], "PPC": ["google ads", "sem", "paid search"], "Negotiation": [],
        "Strategic Planning": ["strategy", "business strategy"], "Six Sigma": ["lean six sigma", "lean"],
        "KPI Tracking": ["kpis", "kpi", "okrs"],
    },
    "healthcare": {
        "Patient Care": ["patient management"], "Critical Care": ["icu"], "Nursing": ["registered nurse", "rn"],
        "EMR": ["ehr", "electronic medical records", "electronic health records", "epic"], "HIPAA": [],
        "Clinical Research": ["clinical trials"], "Medical Coding": ["icd-10", "cpt coding"],
        "Pharmacology": [], "Phlebotomy": [], "BLS": ["basic life support", "cpr"], "ACLS": [],
    },
    "soft_skills": {
        "Leadership": ["team leadership", "people management", "led a team", "team lead"],
        "Communication": ["communication skills", "verbal communication", "written communication"],
        "Teamwork": ["team player", "team work", "cross-functional collaboration"],
        "Problem Solving": ["problem-solving", "troubleshooting"], "Analytical Skills": ["analytical thinking", "analytical"],
        "Collaboration": ["cross-functional"], "Mentoring": ["mentorship", "coaching"],
        "Presentation": ["presentation skills", "public speaking"], "Stakeholder Management": ["stakeholder communication"],
        "Time Management": ["prioritization"], "Critical Thinking": [], "Adaptability": ["flexibility"],
        "Creativity": [], "Attention to Detail": ["detail-oriented", "detail oriented"], "Decision Making": [],
        "Customer Focus": ["client-facing", "customer-facing"], "Ownership": [],
    },
    "certifications": {
        "AWS Certified": ["aws certified solutions architect", "aws certified developer", "aws solutions architect"],
        "Azure Certified": ["az-900", "az-104", "az-204", "azure fundamentals"], "GCP Certified": ["google cloud certified"],
        "PMP": ["project management professional"], "Scrum Master": ["csm", "psm", "certified scrum master"],
        "CISSP": [], "CompTIA": ["comptia security+", "security+", "comptia a+", "network+"], "CKA": [], "CKAD": [],
        "CPA": [], "CFA": [], "ACCA": [], "Chartered Accountant": [], "ITIL": [], "CCNA": [], "Six Sigma Certified": ["green belt", "black belt"],
    },
}

# Ambiguous words: matched case-sensitively, and rejected when followed by a
# lowercase word (prose like "Go to market", "R&D", "Spring semester").
AMBIGUOUS: Dict[str, Tuple[str, List[str], bool]] = {
    # name: (category, case-sensitive words, strict) - strict words need list context
    "Go": ("programming_languages", ["Go"], False),
    "R": ("programming_languages", ["R"], True),
    "C": ("programming_languages", ["C"], True),
    "Spring Boot": ("frameworks_libraries", ["Spring"], False),
    "Express.js": ("frameworks_libraries", ["Express"], False),
    "Excel": ("tools_platforms", ["Excel", "EXCEL"], False),
    "AWS Lambda": ("cloud_devops", ["Lambda"], False),
    "Chef": ("cloud_devops", ["Chef"], False),
    "Less": ("programming_languages", ["LESS"], False),
}
# Canonical names that must only be matched through AMBIGUOUS rules / aliases
NO_CANONICAL_MATCH = {"Go", "R", "C", "Excel"}

# Words that may follow an ambiguous skill without making it prose ("Go is a plus")
_TECH_FOLLOWERS = (
    "is|are|was|programming|development|developer|developers|experience|preferred|required|"
    "language|languages|services|service|microservices|code|modules|backend|applications|apps|"
    "framework|boot|cloud|functions|function|spreadsheets|spreadsheet|skills|knowledge|scripts|"
    "scripting|and|or|plus|a"
)

# Aliases that are too risky as plain lowercase matches; only matched in their
# original casing. Example: "ml" in "5 ml" vs "ML"; "rest" vs "REST".
CASE_SENSITIVE_ALIASES = {
    "ml": "ML", "dl": "DL", "rest": "REST", "ts": "TS", "js": "JS", "ui": "UI", "ux": "UX",
    "elk": "ELK", "rn": "RN", "csm": "CSM", "psm": "PSM", "sem": "SEM", "smm": "SMM",
    "drf": "DRF", "ror": "ROR", "mui": "MUI", "brd": "BRD", "gst": "GST", "tax": "Tax",
    "lean": "Lean", "node": "Node", "epic": "Epic", "audit": "Audit", "spark": "Spark",
    "torch": "Torch", "d3": "D3", "unreal": "Unreal", "embedded": "Embedded", "analytics": "Analytics",
    "operations": "Operations", "strategy": "Strategy", "hiring": "Hiring", "flexibility": "Flexibility",
    "gpt": "GPT", "bert": "BERT", "cnn": "CNN", "rnn": "RNN", "lstm": "LSTM", "dsa": "DSA", "sso": "SSO",
    "jwt": "JWT", "dns": "DNS", "vpn": "VPN", "swift": "Swift", "rust": "Rust", "dart": "Dart",
    "julia": "Julia", "unity": "Unity", "notion": "Notion", "slack": "Slack", "sketch": "Sketch",
    "helm": "Helm", "electron": "Electron", "ionic": "Ionic", "assembly": "Assembly", "sas": "SAS",
    "apex": "Apex", "groovy": "Groovy", "sales": "Sales", "puppet": "Puppet", "qt": "Qt",
    "canva": "Canva", "looker": "Looker", "asana": "Asana", "elt": "ELT", "ai": "AI", "seo": "SEO",
    "kpi": "KPI", "kpis": "KPIs", "icu": "ICU", "epic": "Epic", "lambda functions": "Lambda functions",
    "ownership": "Ownership", "creativity": "Creativity", "networking": "Networking",
}
# Note: case-sensitive aliases still match their ALL-CAPS / Title-case forms.

SOFT_CATEGORIES = {"soft_skills"}
CATEGORY_WEIGHT = {
    "soft_skills": 0.35, "certifications": 0.8, "tools_platforms": 0.8, "concepts_practices": 0.85,
}

# Groups of interchangeable / closely related skills. Having one when the JD
# asks for another earns partial credit (value in the tuple).
RELATED_GROUPS: List[Tuple[Set[str], float]] = [
    ({"PostgreSQL", "MySQL", "SQL Server", "MariaDB", "Oracle Database", "SQLite"}, 0.6),
    ({"MongoDB", "DynamoDB", "Cassandra", "CouchDB", "Firestore"}, 0.5),
    ({"AWS", "Azure", "GCP"}, 0.5),
    ({"React", "Vue.js", "Angular", "Svelte"}, 0.45),
    ({"Next.js", "Nuxt.js", "Gatsby"}, 0.5),
    ({"Django", "Flask", "FastAPI"}, 0.6),
    ({"Spring Boot", "ASP.NET", ".NET", "NestJS", "Express.js"}, 0.3),
    ({"Node.js", "Express.js", "NestJS"}, 0.6),
    ({"TensorFlow", "PyTorch", "Keras"}, 0.65),
    ({"Jenkins", "GitHub Actions", "GitLab CI", "CircleCI", "Travis CI", "CI/CD", "ArgoCD"}, 0.6),
    ({"Terraform", "CloudFormation", "Ansible", "Puppet", "Chef"}, 0.45),
    ({"Docker", "Kubernetes"}, 0.35),
    ({"Kafka", "RabbitMQ"}, 0.5),
    ({"Tableau", "Power BI", "Looker"}, 0.6),
    ({"Snowflake", "BigQuery", "Redshift", "Databricks"}, 0.55),
    ({"JavaScript", "TypeScript"}, 0.7),
    ({"Java", "Kotlin", "Scala"}, 0.4),
    ({"C++", "C", "Rust"}, 0.35),
    ({"Jest", "Mocha", "pytest", "JUnit", "Unit Testing"}, 0.5),
    ({"Selenium", "Cypress", "Playwright", "Puppeteer", "Automation Testing"}, 0.55),
    ({"Jira", "Trello", "Asana"}, 0.6),
    ({"Figma", "Sketch", "Adobe XD"}, 0.65),
    ({"Prometheus", "Grafana", "Datadog", "New Relic", "ELK Stack", "Splunk"}, 0.5),
    ({"React Native", "Flutter", "Ionic", "Xamarin"}, 0.5),
    ({"Machine Learning", "Deep Learning", "Data Science", "Predictive Modeling"}, 0.5),
    ({"LLMs", "Generative AI", "RAG", "LangChain", "LlamaIndex", "Prompt Engineering", "Transformers"}, 0.5),
    ({"GitHub", "GitLab", "Bitbucket", "Git"}, 0.7),
    ({"Leadership", "Mentoring"}, 0.5),
    ({"Teamwork", "Collaboration"}, 0.7),
    ({"Linux", "Unix", "Bash"}, 0.5),
    ({"Backend Development", "Full Stack Development", "Web Development"}, 0.6),
    ({"Frontend Development", "Full Stack Development", "Web Development"}, 0.6),
]

# Having the key skill implies working knowledge of the listed ones
# (someone who uses MySQL knows SQL; Django implies Python).
IMPLIES: Dict[str, List[str]] = {
    "MySQL": ["SQL"], "PostgreSQL": ["SQL"], "SQL Server": ["SQL"], "SQLite": ["SQL"], "MariaDB": ["SQL"],
    "Oracle Database": ["SQL"], "Snowflake": ["SQL"], "BigQuery": ["SQL"], "Redshift": ["SQL"],
    "Django": ["Python"], "Flask": ["Python"], "FastAPI": ["Python"], "Pandas": ["Python"], "NumPy": ["Python"],
    "scikit-learn": ["Python", "Machine Learning"], "PyTorch": ["Python", "Deep Learning"],
    "TensorFlow": ["Deep Learning"], "Keras": ["Deep Learning"], "Apache Spark": ["Big Data"],
    "React": ["JavaScript"], "Angular": ["TypeScript"], "Vue.js": ["JavaScript"], "Next.js": ["React", "JavaScript"],
    "Node.js": ["JavaScript"], "Express.js": ["Node.js", "JavaScript"], "NestJS": ["Node.js", "TypeScript"],
    "Redux": ["React"], "Spring Boot": ["Java"], "Hibernate": ["Java"], "ASP.NET": [".NET", "C#"],
    "Ruby on Rails": ["Ruby"], "Laravel": ["PHP"], "Flutter": ["Dart", "Mobile Development"],
    "React Native": ["JavaScript", "Mobile Development"], "SwiftUI": ["Swift", "iOS"], "Jetpack Compose": ["Kotlin", "Android"],
    "Kubernetes": ["Docker"], "EC2": ["AWS"], "S3": ["AWS"], "AWS Lambda": ["AWS", "Serverless"], "ECS": ["AWS"],
    "DynamoDB": ["AWS", "NoSQL"], "MongoDB": ["NoSQL"], "Cassandra": ["NoSQL"], "GitHub": ["Git"], "GitLab": ["Git"],
    "GitHub Actions": ["CI/CD"], "Jenkins": ["CI/CD"], "GitLab CI": ["CI/CD"], "CircleCI": ["CI/CD"],
    "LangChain": ["LLMs"], "LlamaIndex": ["LLMs"], "RAG": ["LLMs"], "Hugging Face": ["Transformers"],
    "Tableau": ["Data Visualization"], "Power BI": ["Data Visualization"], "Looker": ["Data Visualization"],
    "Matplotlib": ["Data Visualization"], "Seaborn": ["Data Visualization"], "Plotly": ["Data Visualization"],
    "Airflow": ["Data Engineering"], "dbt": ["Data Engineering", "SQL"], "Kafka": ["Data Engineering"],
    "Scrum": ["Agile"], "Kanban": ["Agile"], "Scrum Master": ["Scrum", "Agile"], "Jest": ["Unit Testing"],
    "pytest": ["Unit Testing"], "JUnit": ["Unit Testing"], "Selenium": ["Automation Testing"],
    "Cypress": ["Automation Testing"], "Playwright": ["Automation Testing"], "Mentoring": ["Leadership"],
    "Sass": ["CSS"], "Tailwind CSS": ["CSS"], "Bootstrap": ["CSS"], "TypeScript": ["JavaScript"],
}

CANONICAL_CATEGORY: Dict[str, str] = {}
for _cat, _skills in SKILLS.items():
    for _name in _skills:
        CANONICAL_CATEGORY.setdefault(_name, _cat)
for _name, (_cat, _w, _strict) in AMBIGUOUS.items():
    CANONICAL_CATEGORY.setdefault(_name, _cat)


def skill_weight(name: str) -> float:
    return CATEGORY_WEIGHT.get(CANONICAL_CATEGORY.get(name, ""), 1.0)


def is_soft_skill(name: str) -> bool:
    return CANONICAL_CATEGORY.get(name) in SOFT_CATEGORIES


def related_credit(target: str, have: Set[str]) -> Tuple[float, str]:
    """Best partial credit for `target` given the skills the candidate has."""
    best, via = 0.0, ""
    for group, credit in RELATED_GROUPS:
        if target in group:
            for other in group:
                if other != target and other in have and credit > best:
                    best, via = credit, other
    return best, via


# ---------------------------------------------------------------------------
# Matcher
# ---------------------------------------------------------------------------

_LEFT = r"(?<![A-Za-z0-9_])"
_RIGHT = r"(?![A-Za-z0-9_+#]|\.[A-Za-z0-9])"


def _alias_regex(alias: str) -> str:
    # Allow flexible whitespace / hyphen between words ("problem solving" ~ "problem-solving")
    parts = [re.escape(p) for p in re.split(r"[\s\-]+", alias.strip()) if p]
    body = r"[\s\-]*".join(parts) if len(parts) > 1 else parts[0]
    left = "" if alias[0] in ".#" else _LEFT
    return left + body + _RIGHT


@lru_cache(maxsize=1)
def _compiled() -> List[Tuple[str, str, "re.Pattern", "re.Pattern|None"]]:
    out = []
    for cat, skills in SKILLS.items():
        for name, aliases in skills.items():
            ci, cs = [], []
            for a in ([] if name in NO_CANONICAL_MATCH else [name]) + aliases:
                low = a.lower()
                if low in CASE_SENSITIVE_ALIASES:
                    cs.append(CASE_SENSITIVE_ALIASES[low])
                    cs.append(CASE_SENSITIVE_ALIASES[low].upper())
                else:
                    ci.append(low)
            ci = sorted(set(ci), key=len, reverse=True)
            cs = sorted(set(cs), key=len, reverse=True)
            ci_re = re.compile("|".join(_alias_regex(a) for a in ci), re.IGNORECASE) if ci else None
            cs_re = re.compile("|".join(_alias_regex(a) for a in cs)) if cs else None
            # Literal substrings every match must contain - lets find_skills skip
            # the regex entirely for skills that can't be present (big speed-up)
            ci_needles = tuple({_first_part(a) for a in ci})
            cs_needles = tuple({_first_part(a) for a in cs})
            out.append((name, cat, ci_re, cs_re, ci_needles, cs_needles))
    return out


def _first_part(alias: str) -> str:
    """Longest literal word of the alias (every word must appear in a match)."""
    return max(re.split(r"[\s\-]+", alias.strip()), key=len)


@lru_cache(maxsize=1)
def _ambiguous_compiled() -> List[Tuple[str, str, "re.Pattern"]]:
    out = []
    for name, (cat, words, strict) in AMBIGUOUS.items():
        alts = "|".join(re.escape(w) for w in words)
        core = rf"(?<![A-Za-z0-9_&./+#'-])(?:{alts})(?![A-Za-z0-9_&+#'\-]|\.[A-Za-z0-9])"
        if strict:
            # Single letters: must sit in a list ("Python, R, SQL" / "C and C++" / "(R)")
            left_ctx = (r"(?:^|(?<=[,;|/(:•])|(?<=[,;|/(:•][ \t])|(?<=\band )|(?<=\bor )"
                        r"|(?<=\bin )|(?<=\bwith ))")
            right_ctx = r"(?=[ \t]*(?:[,;|/)]|$|and\b|or\b|\())"
            pat = left_ctx + core + right_ctx
        else:
            # Reject when followed by an ordinary lowercase word ("Go to market", "Spring semester")
            pat = core + rf"(?![ \t]+(?!(?:{_TECH_FOLLOWERS})\b)[a-z])"
        out.append((name, cat, re.compile(pat, re.MULTILINE)))
    return out


def find_skills(text: str) -> Dict[str, Dict]:
    """
    Find skills in text.
    Returns {canonical_name: {"category": str, "count": int, "positions": [int]}}
    """
    found: Dict[str, Dict] = {}
    if not text:
        return found

    def add(name, cat, matches):
        if not matches:
            return
        entry = found.setdefault(name, {"category": cat, "count": 0, "positions": []})
        entry["count"] += len(matches)
        entry["positions"].extend(m.start() for m in matches)

    lower = text.lower()
    for name, cat, ci_re, cs_re, ci_needles, cs_needles in _compiled():
        matches = []
        if ci_re and any(n in lower for n in ci_needles):
            matches.extend(ci_re.finditer(text))
        if cs_re and any(n in text for n in cs_needles):
            matches.extend(cs_re.finditer(text))
        add(name, cat, matches)

    for name, cat, pat in _ambiguous_compiled():
        add(name, cat, list(pat.finditer(text)))

    # Resolve overlaps where a more specific skill contains a generic one
    _suppress_contained(found, "React Native", "React")
    _suppress_contained(found, "Google Analytics", "Data Analysis")
    _suppress_contained(found, "SQL Server", "SQL")
    _suppress_contained(found, "Six Sigma Certified", "Six Sigma")
    return found


def _suppress_contained(found: Dict[str, Dict], specific: str, generic: str, window: int = 20):
    if specific == generic or specific not in found or generic not in found:
        return
    spec_pos = found[specific]["positions"]
    keep = [p for p in found[generic]["positions"] if not any(0 <= p - s <= window for s in spec_pos)]
    if keep:
        found[generic]["positions"] = keep
        found[generic]["count"] = len(keep)
    else:
        del found[generic]
