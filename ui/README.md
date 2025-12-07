# Voice Assistant UI - Setup Guide

## Overview
This React UI provides a modern, floating window interface to control your Python voice assistant chatbot.

## Architecture
- **Frontend**: React + Vite with glassmorphism design
- **Backend**: Flask API server that manages the Python chatbot process
- **Communication**: REST API with status polling

## Setup Instructions

### 1. Install Flask API Dependencies

```bash
cd c:\_c_github\talker\api
pip install -r requirements.txt
```

### 2. Install React UI Dependencies

```bash
cd c:\_c_github\talker\ui
npm install
```

### 3. Start the Flask API Server

```bash
cd c:\_c_github\talker\api
python api_server.py
```

The API will run on `http://localhost:5000`

### 4. Start the React Development Server

In a **new terminal**:

```bash
cd c:\_c_github\talker\ui
npm run dev
```

The UI will run on `http://localhost:5173`

### 5. Open the UI

Open your browser to: `http://localhost:5173`

## Usage

1. **Start Conversation**: Click the green "Start Conversation" button
   - This starts the Python chatbot (`main.py`) in the background
   - The avatar will pulse green and status will show "Listening"

2. **Speak**: Talk to your voice assistant as normal

3. **Stop Conversation**: Click the red "Stop Conversation" button
   - This terminates the Python chatbot process
   - Status returns to "Idle"

## Features

✨ **Draggable Window**: Drag the window anywhere on screen
🎨 **Glassmorphism Design**: Modern, premium aesthetic
🔄 **Real-time Status**: Automatic status updates (Idle/Listening/Speaking/Processing)
💫 **Smooth Animations**: Framer Motion animations throughout
👤 **Animated Avatar**: Visual feedback for conversation states
🎯 **Error Handling**: User-friendly error messages

## API Endpoints

- `POST /api/conversation/start` - Start the voice assistant
- `POST /api/conversation/stop` - Stop the voice assistant
- `GET /api/status` - Get current status
- `GET /api/health` - Health check

## Troubleshooting

**UI can't connect to API**:
- Make sure Flask API server is running on port 5000
- Check console for CORS errors

**Voice assistant won't start**:
- Verify `main.py` path in `api_server.py`
- Check that all Python dependencies are installed
- Look at Flask API console for error messages

**Status not updating**:
- Status polling happens every 1 second when active
- Check browser console for errors

## Development

**Build for Production**:
```bash
cd c:\_c_github\talker\ui
npm run build
```

**Preview Production Build**:
```bash
npm run preview
```

## File Structure

```
talker/
├── ui/                          # React frontend
│   ├── src/
│   │   ├── components/          # React components
│   │   │   ├── Avatar.jsx
│   │   │   ├── ControlButtons.jsx
│   │   │   ├── StatusIndicator.jsx
│   │   │   └── VoiceAssistantWindow.jsx
│   │   ├── services/
│   │   │   └── api.js           # API service layer
│   │   ├── App.jsx              # Main app component
│   │   ├── main.jsx             # Entry point
│   │   └── index.css            # Styles
│   ├── package.json
│   └── vite.config.js
│
├── api/                         # Flask backend
│   ├── api_server.py            # Flask REST API
│   ├── process_manager.py       # Subprocess management
│   └── requirements.txt
└── src/
    └── main.py                  # Voice assistant script
```
