# AI Learning Platform

An intelligent, adaptive learning platform that generates personalized educational content using Large Language Models (LLMs). The platform assesses user proficiency and creates customized learning paths tailored to individual skill levels.
Visit here: https://ailmspro.roberto-costantino.com/

## Features

### 🎯 Adaptive Learning

- **Difficulty Assessment**: Initial quiz to determine user's proficiency level
- **Personalized Learning Paths**: Three difficulty levels (Beginner, Intermediate, Advanced)
- **Structured Curriculum**: 10 topics per difficulty level, 4 lessons per topic (40 lessons total per level)
- **Progress Tracking**: Mark lessons as complete and track advancement through the curriculum

### 🤖 AI-Powered Content Generation

- Dynamic content creation using LLM technology (powered by Groq)
- Asynchronous content generation for optimal performance
- Subject-specific learning materials tailored to difficulty level

### 📈 Progression System

- Advance to next difficulty level upon completing all topics
- Retake assessment quiz option (unlocked at 80% completion)
- Validate learning and ensure readiness for next level

## Tech Stack

### Backend

- **Framework**: Django
- **Language**: Python
- **Data Validation**: Pydantic
- **Database**: PostgreSQL
- **Task Queue**: Celery
- **Message Broker**: Redis
- **LLM Integration**: Groq library

### Infrastructure

- **Hosting**: Google Cloud Platform (VM)
- **CI/CD**: GitHub Actions
- **Deployment**: Automated deployment pipeline

## Installation

### Prerequisites

- Python 3.8+
- PostgreSQL
- Redis
- Google Cloud Platform account (for deployment)

## Usage

### User Flow

1. **Subject Selection**: Choose a subject to learn
2. **Assessment Quiz**: Complete initial difficulty assessment
3. **Learning Path Generation**: System generates personalized 10-topic curriculum
4. **Learn**: Progress through 4 lessons per topic
5. **Complete**: Mark lessons as complete to track progress
6. **Advance**: Complete all topics to unlock next difficulty level
7. **Reassess**: Retake quiz at 80% completion to validate advancement

### Local Setup

1. **Clone the repository**

```bash
git clone <repository-url>
cd learning-platform
```

2. **Create virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
   Create a `.env` file in the project root:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
REDIS_URL=redis://localhost:6379/0
GROQ_API_KEY=your-groq-api-key
```

5. **Run migrations**

```bash
python manage.py migrate
```

6. **Start Redis server**

```bash
redis-server
```

7. **Start Celery worker**

```bash
celery -A project_name worker --loglevel=info
```

8. **Run development server**

```bash
python manage.py runserver
```

## Deployment

### Google Cloud Platform

The application is deployed on GCP using a Virtual Machine instance with automated deployment via GitHub Actions.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
