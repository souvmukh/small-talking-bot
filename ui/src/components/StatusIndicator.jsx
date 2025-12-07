import React from 'react';
import { motion } from 'framer-motion';

const StatusIndicator = ({ status }) => {
    const getStatusText = () => {
        switch (status) {
            case 'listening':
                return 'Listening...';
            case 'speaking':
                return 'Speaking...';
            case 'processing':
                return 'Processing...';
            default:
                return 'Idle';
        }
    };

    const getStatusClass = () => {
        return `status-badge ${status}`;
    };

    return (
        <div className="status-container">
            <motion.div
                className={getStatusClass()}
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
            >
                <span className="status-dot"></span>
                <span>{getStatusText()}</span>
            </motion.div>
        </div>
    );
};

export default StatusIndicator;
