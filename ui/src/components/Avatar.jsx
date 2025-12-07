import React from 'react';
import { UserCircle2 } from 'lucide-react';
import { motion } from 'framer-motion';

const Avatar = ({ status }) => {
    const getAvatarClass = () => {
        if (status === 'listening') return 'avatar listening';
        if (status === 'speaking') return 'avatar speaking';
        return 'avatar';
    };

    return (
        <div className="avatar-container">
            <motion.div
                className={getAvatarClass()}
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: 'spring', stiffness: 260, damping: 20 }}
            >
                <UserCircle2 className="avatar-icon" strokeWidth={1.5} />
                {(status === 'listening' || status === 'speaking') && (
                    <motion.div
                        className="avatar-ring"
                        initial={{ scale: 0.8, opacity: 0 }}
                        animate={{ scale: 1.2, opacity: 0 }}
                        transition={{ duration: 2, repeat: Infinity }}
                    />
                )}
            </motion.div>
        </div>
    );
};

export default Avatar;
