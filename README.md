# Quentora — AI-Powered MCQ Generation & Assessment Platform

Quentora is an AI-powered educational platform designed to simplify question creation, online assessments, automated evaluation, and student performance tracking. It helps teachers prepare assessments from learning materials while giving students an interactive environment to attempt quizzes and review their results.

## ✨ Features

### 🤖 AI-Powered Question Generation
- Generate multiple-choice questions (MCQs) from learning content.
- Support different question difficulty levels.
- Support True/False questions.
- Use AI-generated questions and explanations to support learning and assessment.

### 📝 Online Assessments
- Create and manage assessments.
- Allow students to attempt assigned assessments online.
- Automatically evaluate submitted answers.
- Calculate scores using option correctness and explanation quality.

### ⚖️ Automated Evaluation
Each question is worth **1 mark**, using the following marking scheme:

| Component | Marks |
|---|---:|
| Correct option | 0.8 |
| Explanation quality | 0.2 |
| **Total per question** | **1.0** |

Explanation scoring uses an AI-based evaluation method when available, with a similarity-based fallback.

### 👥 Role-Based Access
Quentora supports three user roles:

- **Administrator:** Manage platform data and oversee users, courses, and assessments.
- **Teacher:** Manage learning content and assessments, and review student performance.
- **Student:** Attempt assessments and view results.

### 📊 Student Performance Tracking
- Store assessment attempts and results in PostgreSQL.
- Review marks, percentages, and question-level feedback.
- View student performance through reports and dashboards.

### 🛡️ Assessment Monitoring
- Fullscreen assessment mode.
- Tab-switch warnings and violation tracking.
- Automatic submission after repeated tab-switch violations.
- Restrictions on selected browser shortcuts during assessments.

*Note: Browser-based monitoring provides best-effort deterrence and cannot prevent every form of cheating.*

## 🛠️ Technology Stack

| Category | Technologies |
|---|---|
| Backend | Python, Flask |
| Frontend | HTML, CSS, JavaScript, Jinja2 |
| Database | PostgreSQL |
| AI integration | Google Gemini API |
| Data access | `psycopg` |
| Version control | Git, GitHub |

## 🏗️ Application Architecture

```text
                    ┌─────────────────────┐
                    │       Users         │
                    │ Admin / Teacher /   │
                    │       Student       │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Frontend Interface │
                    │ HTML / CSS / JS     │
                    │ Jinja2 Templates    │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │    Flask Backend    │
                    │ Authentication      │
                    │ Assessments & Scoring│
                    └───────┬───────┬─────┘
                            │       │
                 ┌──────────▼─┐  ┌──▼────────────┐
                 │ PostgreSQL │  │ Gemini API    │
                 │ Users,     │  │ AI Question   │
                 │ Questions, │  │ Generation    │
                 │ Results    │  │               │
                 └────────────┘  └───────────────┘
```

## 📋 Prerequisites

Before running Quentora locally, install:

- Python 3.10 or a compatible version for the project's dependencies
- PostgreSQL
- Git
- A Google Gemini API key for AI-powered functionality

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd <YOUR_PROJECT_DIRECTORY>
```

Replace the placeholders with your actual repository URL and project directory.

### 2. Create a virtual environment

**Windows**

```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure PostgreSQL

Create a PostgreSQL database for Quentora and configure the database connection using the settings expected by your application.

Ensure the required tables are created before starting the application. Use the project's existing database schema or SQL setup files where available.

### 5. Configure environment variables

Add your Gemini API key and database configuration using the variable names expected by your `app.py` or configuration module.

For example, a `.env` file could contain:

```env
GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=your_postgresql_connection_string
SECRET_KEY=replace_with_a_secure_random_secret
```

These are example variable names; verify that they match the names your application actually reads. Do not commit API keys, passwords, or production secrets to GitHub.

### 6. Run the application

If your Flask entry point is `app.py`:

```bash
python app.py
```

Open the local URL printed by Flask in your terminal, commonly:

```text
http://127.0.0.1:5000
```

## 📁 Project Structure

The project is organized around a Flask application, templates, static assets, and supporting configuration files.

```text
Quentora/
├── app.py
├── requirements.txt
├── config.py
├── templates/
│   ├── admin/
│   └── student/
├── static/
│   └── style.css
├── .env                 # Local secrets; do not commit
└── README.md
```

*This is an illustrative structure. Keep the filenames and directories consistent with the actual files in your repository.*

## 🔄 Assessment Workflow

1. A teacher prepares learning content and creates an assessment.
2. Quentora generates or manages questions for the assessment.
3. A student opens the assessment and submits answers with explanations.
4. The backend checks the selected options and evaluates explanations.
5. Marks are calculated using the configured scoring scheme.
6. Results are saved in PostgreSQL and made available for review.

## 🔐 Security Considerations

- Keep API keys and database credentials out of source control.
- Use secure session settings and a strong Flask secret key.
- Enforce role-based authorization on protected routes.
- Validate user input and handle database errors safely.
- Treat browser-based assessment restrictions as deterrents, not complete security controls.

## 🧪 Testing

Before deploying, verify:

- User login and role-based access.
- MCQ and True/False generation.
- Assessment creation and submission.
- Correct-option and explanation scoring.
- Result persistence and report calculations.
- Tab-switch warnings and automatic submission.
- Database connectivity and error handling.

## 🔮 Future Enhancements

Potential improvements include:

- Question bank search and filtering.
- Assessment scheduling and time limits.
- Detailed performance analytics.
- Exportable student reports.
- Improved question quality validation.
- More robust monitoring and audit logs.

## 🎯 Project Objective

Quentora aims to make assessment creation and evaluation more efficient by combining AI-assisted question generation, structured online testing, automated scoring, and student performance reporting in one platform.

## 👨‍💻 Author

**Arunava Biswas**

BCA — Artificial Intelligence & Data Science

- GitHub: [Add your GitHub profile URL](https://github.com/arun888-bis)
- LinkedIn: [Add your LinkedIn profile URL](https://www.linkedin.com/in/arunavabis//)

---

*Quentora — Smarter Question Generation. Simpler Assessments. Better Learning.*
