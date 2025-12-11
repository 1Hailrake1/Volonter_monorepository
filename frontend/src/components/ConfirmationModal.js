import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiAlertCircle } from 'react-icons/fi';
import './ConfirmationModal.css';

const ConfirmationModal = ({ title, message, onConfirm, onCancel }) => {
    return (
        <AnimatePresence>
            <motion.div
                className="modal-overlay"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                onClick={onCancel}
            >
                <motion.div
                    className="confirmation-modal"
                    initial={{ scale: 0.9, opacity: 0, y: 20 }}
                    animate={{ scale: 1, opacity: 1, y: 0 }}
                    exit={{ scale: 0.9, opacity: 0, y: 20 }}
                    onClick={(e) => e.stopPropagation()}
                >
                    <div className="confirmation-icon">
                        <FiAlertCircle />
                    </div>

                    <h3 className="confirmation-title">{title || 'Подтверждение'}</h3>
                    <p className="confirmation-message">{message}</p>

                    <div className="confirmation-actions">
                        <button className="btn-cancel" onClick={onCancel}>
                            Отмена
                        </button>
                        <button className="btn-confirm" onClick={onConfirm}>
                            Подтвердить
                        </button>
                    </div>
                </motion.div>
            </motion.div>
        </AnimatePresence>
    );
};

export default ConfirmationModal;
