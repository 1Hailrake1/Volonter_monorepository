import React, { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiCheckCircle, FiAlertCircle, FiX } from 'react-icons/fi';
import './Notification.css';

const Notification = ({ message, type = 'info', onClose }) => {
    useEffect(() => {
        if (message) {
            const timer = setTimeout(() => {
                onClose();
            }, 5000);
            return () => clearTimeout(timer);
        }
    }, [message, onClose]);

    return (
        <AnimatePresence>
            {message && (
                <motion.div
                    className={`notification-container ${type}`}
                    initial={{ opacity: 0, y: 50, scale: 0.9 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: 20, scale: 0.9 }}
                    transition={{ duration: 0.3 }}
                >
                    <div className="notification-icon">
                        {type === 'success' ? <FiCheckCircle /> : <FiAlertCircle />}
                    </div>
                    <div className="notification-content">
                        {message}
                    </div>
                    <button className="notification-close" onClick={onClose}>
                        <FiX />
                    </button>
                </motion.div>
            )}
        </AnimatePresence>
    );
};

export default Notification;
