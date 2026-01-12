# Shopping Buddy AI 🛍️🤖

**Shopping Buddy AI** is an intelligent mobile assistant designed to revolutionize your shopping and fashion experience. It combines the power of computer vision, generative AI, and a seamless mobile interface to help you find products, understand fashion trends, and get personalized styling advice.

## ✨ Key Features

*   **🔍 Visual Search & Analysis**: Snap a photo or upload an image to identify products instantly using advanced object detection (YOLOv8) and analysis.
*   **👗 AI Fashion Stylist**: Get personalized styling advice on how to wear specific items, suggested combinations, and outfit ideas powered by Generative AI (Google Gemini).
*   **🏎️ Real-time Recommendations**: Fast and accurate product matching and search results using Vector Search (ChromaDB).
*   **📱 Modern Mobile Experience**: A beautiful, fluid Flutter application with smooth animations and intuitive UX.

## 🛠️ Tech Stack

### Mobile App (Frontend)
*   **Framework**: Flutter (Dart)
*   **State Management**: (Implicit/StatefulWidgets - *Extend as needed*)
*   **Networking**: Dio
*   **Animations**: Flutter Animate
*   **UI Components**: Material Design 3, Cached Network Image

### Backend (API & Workers)
*   **Framework**: FastAPI (Python)
*   **Database**: PostgreSQL (Structured Data), ChromaDB (Vector Data)
*   **ORM**: SQLAlchemy + Alembic
*   **Task Queue**: Celery + Redis
*   **AI/ML**:
    *   **Object Detection**: YOLOv8 (Ultralytics)
    *   **LLM Integration**: Google Generative AI (Gemini)
    *   **Embeddings**: HuggingFace Transformers / Torch
*   **Infrastructure**: Docker, Docker Compose

## 🚀 Getting Started

Follow these instructions to get the project running on your local machine.

### Prerequisites
*   [Flutter SDK](https://flutter.dev/docs/get-started/install) installed.
*   [Docker Desktop](https://www.docker.com/products/docker-desktop) installed and running.
*   [Python 3.10+](https://www.python.org/) (optional, if running backend without Docker).

### 1. Backend Verification & Setup

The backend is containerized for easy setup.

1.  Navigate to the backend directory:
    ```bash
    cd backend
    ```
2.  **Environment Variables**: Ensure you have a `.env` file in the `backend` directory. (Refer to `.env.example` if available, otherwise configure standard database/API keys).
    *   *Note: You will need a Google Generative AI API Key.*

3.  Start the services using Docker Compose:
    ```bash
    docker-compose up --build
    ```
    This will start:
    *   FastAPI Server (exposed on port `8000` likely)
    *   Celery Worker
    *   PostgreSQL Database
    *   Redis

### 2. Mobile App Setup

1.  Navigate to the mobile app directory:
    ```bash
    cd mobile_app
    ```
2.  Install dependencies:
    ```bash
    flutter pub get
    ```
3.  Run the app:
    *   Ensure a simulator/emulator is running or a device is connected.
    *   Update `lib/constants.dart` or `lib/services/api_service.dart` (or equivalent) to point to your local machine IP instead of `localhost` if testing on a real device.
    ```bash
    flutter run
    ```

## 📂 Project Structure

```
Shopping Buddy AI/
├── backend/                # Python FastAPI Backend
│   ├── app/                # Application logic (Routes, Models, Schemas)
│   ├── ml_models/          # Machine learning models (YOLO weights, etc.)
│   ├── docker-compose.yml  # Container orchestration
│   └── requirements.txt    # Python dependencies
├── mobile_app/             # Flutter Frontend
│   ├── lib/
│   │   ├── screens/        # UI Screens (ResultScreen, etc.)
│   │   ├── services/       # API Services
│   │   └── core/           # Theme and constants
│   └── pubspec.yaml        # Dart dependencies
└── README.md               # Project Documentation
```

## 🤝 Contributing
Contributions are welcome! Please fork the repository and create a pull request with your features or fixes.

---
*Built with ❤️ by your AI Pair Programmer.*
