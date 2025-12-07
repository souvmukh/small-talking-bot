import React, { useState, useEffect } from 'react';
import VoiceAssistantWindow from './components/VoiceAssistantWindow';
import api from './services/api';
import './index.css';

function App() {
    const [status, setStatus] = useState('idle'); // idle, listening, speaking, processing
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    // Poll for status updates
    useEffect(() => {
        let intervalId;

        const pollStatus = async () => {
            try {
                const data = await api.getStatus();
                if (data.status) {
                    setStatus(data.status);
                }
            } catch (err) {
                // Silently fail - backend might not be running yet
                console.log('Status poll failed:', err.message);
            }
        };

        // Poll every 1 second when conversation is active
        if (status !== 'idle') {
            intervalId = setInterval(pollStatus, 1000);
        }

        return () => {
            if (intervalId) {
                clearInterval(intervalId);
            }
        };
    }, [status]);

    const handleStart = async () => {
        setIsLoading(true);
        setError(null);

        try {
            const response = await api.startConversation();
            if (response.success) {
                setStatus('listening');
            } else {
                setError(response.message || 'Failed to start conversation');
            }
        } catch (err) {
            setError('Could not connect to voice assistant. Make sure the API server is running.');
            console.error('Start conversation error:', err);
        } finally {
            setIsLoading(false);
        }
    };

    const handleStop = async () => {
        setIsLoading(true);
        setError(null);

        try {
            const response = await api.stopConversation();
            if (response.success) {
                setStatus('idle');
            } else {
                setError(response.message || 'Failed to stop conversation');
            }
        } catch (err) {
            setError('Could not stop conversation. The process may have already ended.');
            console.error('Stop conversation error:', err);
            // Force status to idle even if API call fails
            setStatus('idle');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="App">
            <VoiceAssistantWindow
                status={status}
                onStart={handleStart}
                onStop={handleStop}
                isLoading={isLoading}
            />
            {error && (
                <div style={{
                    position: 'fixed',
                    bottom: '20px',
                    left: '50%',
                    transform: 'translateX(-50%)',
                    background: 'rgba(239, 68, 68, 0.9)',
                    color: 'white',
                    padding: '12px 24px',
                    borderRadius: '8px',
                    backdropFilter: 'blur(10px)',
                    maxWidth: '400px',
                    textAlign: 'center'
                }}>
                    {error}
                </div>
            )}
        </div>
    );
}

export default App;
