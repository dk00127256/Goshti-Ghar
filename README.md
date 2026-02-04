# गोष्टी घर (Goshti Ghar) - Marathi Storytelling App for Kids

A professional Marathi language storytelling application that generates age-appropriate stories with educational value, converts them to engaging videos, and provides a seamless user experience for children aged 2-12 years.

## 🌟 Features

- **AI-Generated Stories**: Create personalized Marathi stories using OpenAI GPT-4
- **Text-to-Speech**: Convert stories to natural Marathi audio using Google TTS
- **Video Generation**: Automated video creation with subtitles and animations
- **Age-Appropriate Content**: Stories tailored for different age groups (2-4, 5-7, 8-12 years)
- **Moral Lessons**: Each story includes educational themes and moral values
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Offline Support**: Download stories for offline viewing

## 🏗️ Architecture

### Backend (Python/FastAPI)
- **FastAPI**: Modern, fast web framework for building APIs
- **OpenAI Integration**: GPT-4 for story generation
- **Google TTS**: Marathi text-to-speech conversion
- **MoviePy**: Video generation and editing
- **PostgreSQL**: Story database and metadata
- **Redis**: Caching and background task queue

### Frontend (React/TypeScript)
- **React 18**: Modern React with hooks and TypeScript
- **Tailwind CSS**: Utility-first CSS framework
- **React Router**: Client-side routing
- **React Player**: Video playback component
- **Responsive Design**: Mobile-first approach

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)
- OpenAI API key

### 1. Clone the Repository

```bash
git clone <repository-url>
cd goshti-ghar
```

### 2. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env file and add your OpenAI API key
# OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Run with Docker (Recommended)

```bash
# Build and start all services
docker-compose up --build

# The application will be available at:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Documentation: http://localhost:8000/docs
```

### 4. Local Development Setup

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p media/videos media/audio assets/fonts assets/music

# Download Noto Sans Devanagari font
wget -O assets/fonts/NotoSansDevanagari-Bold.ttf \
  "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Bold.ttf"

# Start the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

## 📱 Usage

### Creating a New Story

1. Click "नवीन गोष्ट" (New Story) in the header
2. Select age group (2-4, 5-7, or 8-12 years)
3. Choose or enter a theme (friendship, honesty, courage, etc.)
4. Select moral lesson type
5. Click "गोष्ट तयार करा" (Create Story)
6. Wait 2-3 minutes for AI generation, TTS, and video creation

### Viewing Stories

1. Browse stories on the home page
2. Filter by age group or theme
3. Click on a story card to watch the video
4. View story transcript, characters, and moral lessons
5. Add stories to favorites for easy access

## 🎨 Design System

### Colors
- **Primary**: Orange gradient (#fb923c to #ea580c)
- **Secondary**: Pink gradient (#ec4899 to #db2777)
- **Success**: Green (#10b981)
- **Warning**: Yellow (#f59e0b)
- **Error**: Red (#ef4444)

### Typography
- **Primary Font**: Noto Sans Devanagari (for Marathi text)
- **Secondary Font**: System fonts for UI elements
- **Font Sizes**: Responsive scaling based on device size

### Components
- **Cards**: Rounded corners with subtle shadows
- **Buttons**: Gradient backgrounds with hover effects
- **Forms**: Clean inputs with focus states
- **Video Player**: Custom controls with Marathi labels

## 🔧 Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional
DATABASE_URL=postgresql://user:pass@localhost/db
REDIS_URL=redis://localhost:6379
TTS_SERVICE=gtts
VIDEO_QUALITY=1080p
LOG_LEVEL=INFO
```

### Story Generation Parameters

- **Age Groups**: 2-4, 5-7, 8-12 years
- **Themes**: Friendship, honesty, courage, kindness, helping, respect
- **Story Length**: 2-5 minutes based on age group
- **Language**: Marathi (Devanagari script)
- **Moral Lessons**: Embedded in each story

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v
```

### Frontend Tests

```bash
cd frontend
npm test
```

### End-to-End Tests

```bash
# Install Playwright
npm install -g @playwright/test

# Run E2E tests
npx playwright test
```

## 📦 Deployment

### Docker Production Build

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy to production
docker-compose -f docker-compose.prod.yml up -d
```

### Serverless Deployment (AWS)

1. **Backend**: Deploy to AWS Lambda using Serverless Framework
2. **Frontend**: Deploy to AWS S3 + CloudFront
3. **Database**: Use AWS RDS PostgreSQL
4. **Storage**: Use AWS S3 for media files
5. **CDN**: CloudFront for video delivery

### iOS App Deployment

1. Use React Native or Capacitor to wrap the web app
2. Add native features like offline storage
3. Submit to App Store following guidelines
4. Implement in-app purchases for premium content

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow TypeScript best practices
- Use Tailwind CSS for styling
- Write tests for new features
- Ensure Marathi text rendering works correctly
- Test on multiple devices and browsers

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Noto Fonts**: For excellent Marathi (Devanagari) font support
- **OpenAI**: For GPT-4 story generation capabilities
- **Google**: For Text-to-Speech services
- **MoviePy**: For video generation and editing
- **React Community**: For amazing frontend tools and libraries

## 📞 Support

For support, email support@goshtighaar.com or create an issue in this repository.

## 🗺️ Roadmap

### Phase 1 - MVP ✅
- [x] Story generation with AI
- [x] Text-to-speech conversion
- [x] Basic video assembly
- [x] Web interface
- [x] Docker setup

### Phase 2 - Enhanced Features
- [ ] Advanced animations and transitions
- [ ] Multiple voice options
- [ ] User authentication and profiles
- [ ] Favorite stories and playlists
- [ ] Download for offline viewing
- [ ] Parental controls

### Phase 3 - Production Ready
- [ ] iOS mobile application
- [ ] Serverless deployment
- [ ] Analytics and usage tracking
- [ ] Content moderation
- [ ] Multi-user support
- [ ] Premium content and subscriptions

---

Made with ❤️ for Marathi-speaking children and families.