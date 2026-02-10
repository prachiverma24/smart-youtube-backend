# YouTube Learning Assistant - Backend

A powerful Node.js/Express backend API that processes YouTube videos and generates AI-powered educational content including summaries, key points, and quiz questions.

## 🚀 Features

- **YouTube Transcript Extraction**: Multiple fallback methods for reliable transcript fetching
  - `youtube-transcript` npm package
  - Python `youtube-transcript-api` fallback
  - Manual scraping fallback
  - Audio transcription with OpenAI Whisper (for videos without captions)
- **AI Content Generation**: 
  - Uses Groq AI (Llama 3.1) for intelligent content generation
  - Fallback mode for demo without API key
- **Direct Transcript Processing**: Accept and process manual transcript input
- **MongoDB Integration**: Cache processed videos to reduce API calls
- **RESTful API**: Clean, well-documented endpoints
- **CORS Enabled**: Ready for frontend integration

## 🛠️ Tech Stack

- **Node.js** with **Express.js** - REST API framework
- **MongoDB** with **Mongoose** - Database and ODM
- **Python 3.12** - Transcript extraction scripts
- **OpenAI Whisper** - Audio transcription for videos without captions
- **Groq SDK** - AI-powered content generation
- **yt-dlp** - YouTube audio downloading
- **ffmpeg** - Audio processing

## 📋 Prerequisites

- Node.js (v14 or higher)
- MongoDB (local or Atlas)
- Python 3.12+
- ffmpeg (for audio transcription)
- Groq API Key (optional, has fallback mode)

## 🔧 Installation

### 1. Clone the repository
```bash
git clone https://github.com/prachiverma24/smart-youtube-backend.git
cd smart-youtube-backend
```

### 2. Install Node.js dependencies
```bash
npm install
```

### 3. Set up Python virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install Python dependencies
```bash
pip install youtube-transcript-api openai-whisper yt-dlp
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install numpy tiktoken tqdm more-itertools numba
```

### 5. Install ffmpeg
```bash
# Ubuntu/Debian
sudo apt-get install -y ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

### 6. Configure Environment Variables

Create a `.env` file in the root directory:

```env
# Server Configuration
PORT=5000
NODE_ENV=development

# MongoDB Connection
MONGODB_URI=mongodb://localhost:27017/youtube-learning

# Groq AI API Key (Optional - has fallback)
GROQ_API_KEY=your_groq_api_key_here

# CORS Configuration (Optional)
ALLOWED_ORIGINS=http://localhost:3000
```

### 7. Start MongoDB
```bash
# If using local MongoDB
sudo systemctl start mongod

# Or use MongoDB Atlas cloud database
```

### 8. Start the server
```bash
npm start
```

Server will run on `http://localhost:5000`

## 📡 API Endpoints

### 1. Process YouTube Video
Extract transcript and generate learning content from a YouTube URL.

**Endpoint**: `POST /api/videos/process`

**Request Body**:
```json
{
  "youtubeUrl": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

**Response**:
```json
{
  "youtubeUrl": "https://www.youtube.com/watch?v=VIDEO_ID",
  "videoId": "VIDEO_ID",
  "transcript": "Full video transcript...",
  "summary": "AI-generated summary...",
  "keyPoints": [
    "Key point 1",
    "Key point 2",
    "Key point 3"
  ],
  "quizQuestions": [
    {
      "question": "Question text?",
      "options": ["A", "B", "C", "D"],
      "correctAnswer": "A"
    }
  ],
  "createdAt": "2026-02-10T15:30:00.000Z"
}
```

### 2. Process Direct Transcript
Generate learning content from manually provided transcript.

**Endpoint**: `POST /api/videos/transcript`

**Request Body**:
```json
{
  "transcript": "Your transcript text here...",
  "title": "Video Title (optional)"
}
```

**Response**: Same as above

## 🏗️ Project Structure

```
smart-youtube-backend/
├── controllers/
│   └── videoController.js    # Main business logic
├── models/
│   └── Video.js              # MongoDB schema
├── routes/
│   └── videoRoutes.js        # API route definitions
├── scripts/
│   ├── fetch_transcript.py   # Python transcript fetcher
│   └── transcribe_audio.py   # Whisper audio transcription
├── venv/                      # Python virtual environment
├── index.js                   # Express server entry point
├── package.json               # Node dependencies
├── .env                       # Environment variables
└── README.md                  # This file
```

## 🔄 Transcript Extraction Flow

The system uses a sophisticated fallback mechanism:

1. **Method 1**: `youtube-transcript` npm package
2. **Method 2**: Python `youtube-transcript-api` script
3. **Method 3**: Manual webpage scraping
4. **Method 4**: Audio download + Whisper AI transcription

This ensures maximum reliability across different video types.

## 🤖 AI Content Generation

### With Groq API (Recommended)
- Uses **Llama 3.1 8B Instant** model
- Generates intelligent summaries and quiz questions
- Requires GROQ_API_KEY in `.env`

### Demo/Fallback Mode
- Works without API key
- Provides sample Python programming content
- Perfect for testing and development

## 🗄️ MongoDB Schema

```javascript
{
  youtubeUrl: String,
  videoId: String,
  transcript: String,
  summary: String,
  keyPoints: [String],
  quizQuestions: [{
    question: String,
    options: [String],
    correctAnswer: String
  }],
  createdAt: Date
}
```

## 🔐 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `PORT` | No | Server port (default: 5000) |
| `MONGODB_URI` | Yes | MongoDB connection string |
| `GROQ_API_KEY` | No | Groq AI API key (fallback available) |
| `NODE_ENV` | No | Environment (development/production) |
| `ALLOWED_ORIGINS` | No | CORS allowed origins |

## 🚀 Deployment

### Deploy to Render

1. Push code to GitHub
2. Create new Web Service on Render
3. Connect your repository
4. Set environment variables
5. Deploy!

**Build Command**: `npm install`
**Start Command**: `npm start`

### Deploy to Heroku

```bash
heroku create smart-youtube-backend
heroku config:set MONGODB_URI=your_mongodb_uri
heroku config:set GROQ_API_KEY=your_groq_key
git push heroku main
```

### Deploy to Railway

1. Connect GitHub repository
2. Add environment variables
3. Deploy automatically

## 🐛 Troubleshooting

**Issue**: "Could not fetch transcript from any source"
- **Solution**: Video may have disabled captions. System will attempt audio transcription (takes 1-2 minutes)

**Issue**: MongoDB connection failed
- **Solution**: Ensure MongoDB is running or check MONGODB_URI

**Issue**: Whisper model downloading slowly
- **Solution**: First-time setup downloads ~72MB model. Be patient!

**Issue**: Python script errors
- **Solution**: Activate venv and reinstall Python packages

**Issue**: ffmpeg not found
- **Solution**: Install ffmpeg for your OS

## 📊 Performance Notes

- **Cached videos**: Instant response from MongoDB
- **Standard transcript**: 2-5 seconds
- **Audio transcription**: 45-120 seconds (first time per video)
- **AI generation**: 3-8 seconds with Groq API

## 🔒 Security Considerations

- API keys stored in environment variables
- CORS configured for specific origins
- Input validation on all endpoints
- MongoDB injection prevention with Mongoose
- Rate limiting recommended for production

## 🧪 Testing

```bash
# Test transcript extraction
curl -X POST http://localhost:5000/api/videos/process \
  -H "Content-Type: application/json" \
  -d '{"youtubeUrl":"https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'

# Test direct transcript
curl -X POST http://localhost:5000/api/videos/transcript \
  -H "Content-Type: application/json" \
  -d '{"transcript":"Sample transcript text here...", "title":"Test Video"}'
```

## 📝 Recent Updates

- ✅ Added OpenAI Whisper for videos without captions
- ✅ Implemented yt-dlp for reliable audio downloading
- ✅ Added demo mode for testing without API key
- ✅ Improved error handling and logging
- ✅ Enhanced fallback mechanisms

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is open source and available under the MIT License.

## 👥 Authors

**Prachi Verma**
- GitHub: [@prachiverma24](https://github.com/prachiverma24)

## 🔗 Related Projects

- [Frontend Repository](https://github.com/prachiverma24/smart-youtube-frontend) - React frontend interface

## 💡 Future Enhancements

- [ ] Video progress tracking
- [ ] User authentication with JWT
- [ ] Rate limiting middleware
- [ ] Caching with Redis
- [ ] Support for playlists
- [ ] Webhook notifications
- [ ] Analytics dashboard
- [ ] Multi-language transcript support
- [ ] Custom quiz difficulty levels
- [ ] Export to PDF/DOCX

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review troubleshooting section

---

Built with ❤️ using Node.js, Express, MongoDB, Python, and AI
