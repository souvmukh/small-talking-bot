import React, { useState } from 'react';
import { motion } from 'framer-motion';
import Avatar from './Avatar';
import StatusIndicator from './StatusIndicator';
import ControlButtons from './ControlButtons';

const VoiceAssistantWindow = ({ status, onStart, onStop, isLoading }) => {
    const [position, setPosition] = useState({ x: 0, y: 0 });
    const [isDragging, setIsDragging] = useState(false);

    return (
        <motion.div
            className="voice-assistant-window"
            drag
            dragMomentum={false}
            onDragStart={() => setIsDragging(true)}
            onDragEnd={() => setIsDragging(false)}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, type: 'spring' }}
            style={{ cursor: isDragging ? 'grabbing' : 'grab' }}
        >
            <div className="window-header">
                <h1 className="window-title">Plu</h1>
                <p className="window-subtitle">Your Voice Assistant</p>
            </div>

            <Avatar status={status} />
            <StatusIndicator status={status} />
            <ControlButtons
                status={status}
                onStart={onStart}
                onStop={onStop}
                isLoading={isLoading}
            />
        </motion.div>
    );
};

export default VoiceAssistantWindow;
