# AuraSync SaaS

🚀 Professional AI Voice Studio with Next.js 16, Python, Neon, Polar, Modal & Better Auth

## 📋 Overview

Welcome to AuraSync! This is a production-grade platform that combines a modern Next.js 16 frontend with a powerful Python backend for AI-powered text-to-speech generation.

### 🏗️ Technical Architecture
AuraSync utilizes a decoupled, event-driven architecture to manage high-compute AI tasks:

1. **Orchestration Layer (Next.js):** Handles user sessions, credit validation, and metadata management via Prisma & Neon.
2. **Deterministic Cache (Redis/DB):** Before triggering a GPU job, a SHA-256 hash of parameters is checked to serve existing assets instantly.
3. **Inference Layer (Python/Modal):** A serverless GPU worker that executes the TTS model and handles high-fidelity voice cloning.
4. **Persistence Layer (AWS S3):** Direct-to-bucket uploads from the worker to ensure data durability and low-latency playback.

## ✅ Key Features

### 🎵 AI Text-to-Speech Generation
- Serverless AI TTS using Python & Modal
- Support for multiple languages and voices
- Real-time audio generation and caching for performance
- Custom voice cloning capabilities

## 🏗️ Architecture

```
aurasync/                       # AuraSync Root
├── frontend/                 # Next.js 16 application
│   ├── src/
│   │   ├── app/             # App Router pages and layouts
│   │   ├── components/      # Reusable React components
│   │   ├── lib/             # Utility functions and configurations
│   │   ├── actions/         # Server actions (including tts with caching)
│   │   └── types/           # TypeScript type definitions
│   ├── prisma/              # Database schema and migrations
│   └── public/              # Static assets
├── backend/                 # Python backend services
│   └── text-to-speech/      # AuraSyncEngine (Modal-based)
└── README.md
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- Python 3.11+
- Modal account
- Neon database
- AWS account (for S3)
- Polar account (for payments)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/aurasync.git
   cd aurasync
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

3. **Environment Variables**
   Create `.env` file in `/frontend` (refer to `.env.example`).

4. **Database Setup**
   ```bash
   npx prisma generate
   npx prisma db push
   ```

5. **Backend Setup**
   ```bash
   cd ../backend/text-to-speech
   pip install -r requirements.txt
   modal deploy tts.py
   ```

6. **Run the Application**
   ```bash
   cd ../../frontend
   npm run dev
   ```

---
Built with ❤️ for AuraSync
