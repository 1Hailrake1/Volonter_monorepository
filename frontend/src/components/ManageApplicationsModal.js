import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FiX, FiCheck, FiUser } from 'react-icons/fi';
import { applicationsAPI } from '../api/api';

const ManageApplicationsModal = ({ eventId, eventTitle, onClose }) => {
    const [applications, setApplications] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadApplications();
    }, [eventId]);

    const loadApplications = async () => {
        try {
            const response = await applicationsAPI.getEventApplications(eventId, { page: 1, page_size: 100 });
            setApplications(response.data.applications || []);
        } catch (error) {
            console.error('Error loading applications:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleStatusUpdate = async (appId, status) => {
        try {
            await applicationsAPI.updateStatus(appId, status);
            // Optimistic update
            setApplications(prev => prev.map(app =>
                app.id === appId ? { ...app, status: status } : app
            ));
        } catch (error) {
            console.error(`Error updating status to ${status}:`, error);
            alert('Ошибка при обновлении статуса');
        }
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <motion.div
                className="modal-content"
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
                onClick={e => e.stopPropagation()}
                style={{ maxWidth: '800px', maxHeight: '90vh', overflowY: 'auto' }}
            >
                <div className="modal-header">
                    <h3>Заявки: {eventTitle}</h3>
                    <button className="btn-close" onClick={onClose}><FiX /></button>
                </div>

                <div className="modal-body">
                    {loading ? (
                        <div className="loading-spinner">
                            <div className="spinner"></div>
                            <p>Загрузка...</p>
                        </div>
                    ) : applications.length === 0 ? (
                        <p className="empty-state">Нет заявок на это мероприятие</p>
                    ) : (
                        <div className="applications-list">
                            {applications.map(app => (
                                <div key={app.id} className="application-item" style={{
                                    padding: '15px',
                                    background: 'var(--bg-secondary)',
                                    borderRadius: '12px',
                                    marginBottom: '10px',
                                    border: '1px solid rgba(255,255,255,0.05)'
                                }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                        <div>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                                                <strong>{app.volunteer?.fullname || 'Без имени'}</strong>
                                                <span className={`status-badge status-${app.status}`}>
                                                    {app.status === 'approved' && 'Одобрено'}
                                                    {app.status === 'pending' && 'Ожидает'}
                                                    {app.status === 'rejected' && 'Отклонено'}
                                                    {app.status === 'canceled' && 'Отменено'}
                                                </span>
                                            </div>
                                            <p style={{ fontSize: '14px', color: 'var(--gray-400)', marginTop: '5px' }}>
                                                {app.volunteer?.email || 'Нет email'}
                                            </p>
                                            {app.message && (
                                                <div style={{
                                                    marginTop: '10px',
                                                    fontSize: '14px',
                                                    fontStyle: 'italic',
                                                    padding: '8px',
                                                    background: 'rgba(0,0,0,0.2)',
                                                    borderRadius: '6px'
                                                }}>
                                                    "{app.message}"
                                                </div>
                                            )}
                                        </div>

                                        {app.status === 'pending' && (
                                            <div style={{ display: 'flex', gap: '8px' }}>
                                                <button
                                                    className="btn-icon"
                                                    onClick={() => handleStatusUpdate(app.id, 'approved')}
                                                    style={{ color: 'var(--success)', background: 'rgba(34, 197, 94, 0.1)' }}
                                                    title="Одобрить"
                                                >
                                                    <FiCheck />
                                                </button>
                                                <button
                                                    className="btn-icon"
                                                    onClick={() => handleStatusUpdate(app.id, 'rejected')}
                                                    style={{ color: 'var(--error)', background: 'rgba(239, 68, 68, 0.1)' }}
                                                    title="Отклонить"
                                                >
                                                    <FiX />
                                                </button>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </motion.div>
        </div>
    );
};

export default ManageApplicationsModal;
