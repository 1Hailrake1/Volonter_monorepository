import React, { createContext, useContext, useState, useCallback } from 'react';
import ConfirmationModal from '../components/ConfirmationModal';

const ConfirmationContext = createContext();

export const useConfirm = () => {
    const context = useContext(ConfirmationContext);
    if (!context) {
        throw new Error('useConfirm must be used within a ConfirmationProvider');
    }
    return context;
};

export const ConfirmationProvider = ({ children }) => {
    const [confirmationState, setConfirmationState] = useState({
        isOpen: false,
        title: '',
        message: '',
        onConfirm: null,
        onCancel: null
    });

    const confirm = useCallback(({ title, message, onConfirm, onCancel }) => {
        setConfirmationState({
            isOpen: true,
            title,
            message,
            onConfirm,
            onCancel
        });
    }, []);

    const close = useCallback(() => {
        setConfirmationState(prev => ({ ...prev, isOpen: false }));
    }, []);

    const handleConfirm = useCallback(() => {
        if (confirmationState.onConfirm) {
            confirmationState.onConfirm();
        }
        close();
    }, [confirmationState, close]);

    const handleCancel = useCallback(() => {
        if (confirmationState.onCancel) {
            confirmationState.onCancel();
        }
        close();
    }, [confirmationState, close]);

    return (
        <ConfirmationContext.Provider value={{ confirm }}>
            {children}
            {confirmationState.isOpen && (
                <ConfirmationModal
                    title={confirmationState.title}
                    message={confirmationState.message}
                    onConfirm={handleConfirm}
                    onCancel={handleCancel}
                />
            )}
        </ConfirmationContext.Provider>
    );
};
