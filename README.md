# Personalized Learning Platform

An AI-powered adaptive learning platform built with Django that personalizes educational content based on individual learning styles and knowledge levels.

## 🎯 Overview

This platform creates customized learning experiences by:

- Assessing users' learning preferences (visual, hands-on, reading)
- Evaluating knowledge levels through AI-generated assessments
- Generating personalized learning paths with multi-modal content
- Adapting content presentation based on individual learning styles

## ✨ Key Features

### Intelligent Assessment System

- **Learning Style Assessment**: 5-question evaluation to determine visual, hands-on, and reading preferences
- **Subject Selection**: Choose from Programming, Music, or Art
- **AI-Generated Difficulty Testing**: Dynamic questions created by Groq AI to assess knowledge level (beginner/intermediate/advanced)

### Personalized Learning Paths

- **Topic Generation**: AI creates comprehensive learning roadmaps for all difficulty levels
- **Multi-Modal Lessons**: Each lesson includes visual, hands-on, and reading content
- **Adaptive Content Display**: Emphasizes content types matching user's learning preferences
- **On-Demand Generation**: Lessons created when needed to optimize resource usage

### Progress Tracking

- Complete registration flow with step validation
- Learning progress monitoring
- User profiles displaying assessment results and preferences

## 🛠️ Technology Stack

- **Backend**: Django 5.0+
- **Database**: SQLite (development) / PostgreSQL (production-ready)
- **AI Integration**: Groq API (LLaMA models)
- **Data Validation**: Pydantic
- **Authentication**: Django built-in auth system

## 📋 Prerequisites

- Python 3.11+
- Groq API key (free tier available)
- pip or uv for package management

## 🚀 Installation
