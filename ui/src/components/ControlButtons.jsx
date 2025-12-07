import React from 'react';
import { Play, Square, Loader2 } from 'lucide-react';
import { motion } from 'framer-motion';

const ControlButtons = ({ status, onStart, onStop, isLoading }) => {
    const isConversationActive = status === 'listening' || status === 'speaking' || status === 'processing';

    return (
        <div className="controls-container">
            <motion.button
                className="control-button button-start"
                onClick={onStart}
                disabled={isConversationActive || isLoading}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
            >
                {isLoading && !isConversationActive ? (
                    <>
                        <Loader2 className="button-icon spinner" />
                        <span className="button-text">Starting...</span>
                    </>
                ) : (
                    <>
                        <Play className="button-icon" fill="white" />
                        <span className="button-text">Start Conversation</span>
                    </>
                )}
            </motion.button>

            <motion.button
                className="control-button button-stop"
                onClick={onStop}
                disabled={!isConversationActive || isLoading}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
            >
                {isLoading && isConversationActive ? (
                    <>
                        <Loader2 className="button-icon spinner" />
                        <span className="button-text">Stopping...</span>
                    </>
                ) : (
                    <>
                        <Square className="button-icon" fill="white" />
                        <span className="button-text">Stop Conversation</span>
                    </>
                )}
            </motion.button>
        </div>
    );
};

export default ControlButtons;
