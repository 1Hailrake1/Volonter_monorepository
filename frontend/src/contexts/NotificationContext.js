import React, { createContext, useContext, useState, useCallback } from 'react';
import Notification from '../components/Notification';

const NotificationContext = createContext();

export const useNotification = () => {
    const context = useContext(NotificationContext);
    if (!context) {
        throw new Error('useNotification must be used within a NotificationProvider');
    }
    return context;
};

export const NotificationProvider = ({ children }) => {
    const [notification, setNotification] = useState({ message: null, type: 'info' });

    const notify = useCallback((message, type = 'info') => {
        setNotification({ message, type });
    }, []);

    const closeNotification = useCallback(() => {
        setNotification(prev => ({ ...prev, message: null }));
    }, []);

    return (
        <NotificationContext.Provider value={{ notify }}>
            {children}
            <Notification
                message={notification.message}
                type={notification.type}
                onClose={closeNotification}
            />
        </NotificationContext.Provider>
    );
};
