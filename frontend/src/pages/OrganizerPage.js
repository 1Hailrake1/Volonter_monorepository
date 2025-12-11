import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiPlus, FiEdit2, FiUsers, FiCalendar, FiMapPin, FiTrash2 } from 'react-icons/fi';
import { format } from 'date-fns';
import { eventsAPI } from '../api/api';
import CreateEventModal from '../components/CreateEventModal';
import ManageApplicationsModal from '../components/ManageApplicationsModal';
import { useNotification } from '../contexts/NotificationContext';
import { useConfirm } from '../contexts/ConfirmationContext';
import './OrganizerPage.css';

const OrganizerPage = () => {
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [editingEvent, setEditingEvent] = useState(null);
    const [managingAppsEvent, setManagingAppsEvent] = useState(null);
    const { notify } = useNotification();
    const { confirm } = useConfirm();

    useEffect(() => {
        loadMyEvents();
    }, []);

    const loadMyEvents = async () => {
        setLoading(true);
        try {
            const response = await eventsAPI.getMyEvents();
            setEvents(response.data);
        } catch (error) {
            console.error('Error loading my events:', error);
            notify('Ошибка при загрузке мероприятий', 'error');
        } finally {
            setLoading(false);
        }
    };

    const handleDeleteEvent = (id) => {
        confirm({
            title: 'Удаление мероприятия',
            message: 'Вы уверены, что хотите удалить это мероприятие?',
            onConfirm: async () => {
                try {
                    await eventsAPI.delete(id);
                    notify('Мероприятие удалено', 'success');
                    loadMyEvents();
                } catch (error) {
                    console.error('Error deleting event:', error);
                    notify('Ошибка при удалении', 'error');
                }
            }
        });
    };

    const handleCreateSuccess = () => {
        setShowCreateModal(false);
        notify('Мероприятие создано!', 'success');
        loadMyEvents();
    };

    const handleEditSuccess = () => {
        setEditingEvent(null);
        notify('Мероприятие обновлено!', 'success');
        loadMyEvents();
    };

    return (
        <div className="page-container organizer-page">
            <div className="page-content">
                <motion.div
                    className="organizer-header"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                >
                    <div>
                        <h1>Кабинет организатора</h1>
                        <p className="subtitle">Управляйте своими мероприятиями и заявками</p>
                    </div>
                    <button className="btn-primary" onClick={() => setShowCreateModal(true)}>
                        <FiPlus style={{ marginRight: '8px' }} /> Создать мероприятие
                    </button>
                </motion.div>

                {loading ? (
                    <div className="loading-spinner">
                        <div className="spinner"></div>
                        <p>Загрузка ваших мероприятий...</p>
                    </div>
                ) : events.length > 0 ? (
                    <div className="organizer-grid">
                        {events.map((event, index) => (
                            <motion.div
                                key={event.id}
                                className="card event-card organizer-card"
                                initial={{ opacity: 0, scale: 0.95 }}
                                animate={{ opacity: 1, scale: 1 }}
                                transition={{ delay: index * 0.1 }}
                            >
                                <div className={`status-stripe status-${event.status}`}></div>
                                <div className="card-content">
                                    <div className="event-header">
                                        <h3>{event.title}</h3>
                                        <span className={`status-badge status-${event.status}`}>
                                            {event.status === 'approved' && 'Одобрено'}
                                            {event.status === 'pending' && 'На проверке'}
                                            {event.status === 'completed' && 'Завершено'}
                                            {event.status === 'canceled' && 'Отменено'}
                                        </span>
                                    </div>

                                    <div className="event-details">
                                        <p><FiCalendar /> {format(new Date(event.start_date), 'dd.MM.yyyy HH:mm')}</p>
                                        <p><FiMapPin /> {event.location}</p>
                                        <p><FiUsers /> {event.approved_volunteers_count || 0} / {event.required_volunteers} волонтёров</p>
                                    </div>

                                    <div className="card-actions">
                                        <button
                                            className="btn-secondary"
                                            onClick={() => setManagingAppsEvent(event)}
                                        >
                                            <FiUsers style={{ marginRight: '5px' }} /> Заявки
                                        </button>
                                        <button
                                            className="btn-icon-secondary"
                                            onClick={() => setEditingEvent(event)}
                                            title="Редактировать"
                                        >
                                            <FiEdit2 />
                                        </button>
                                        {/* Optional Delete Button */}
                                        <button
                                            className="btn-icon-danger"
                                            onClick={() => handleDeleteEvent(event.id)}
                                            title="Удалить"
                                        >
                                            <FiTrash2 />
                                        </button>
                                    </div>
                                </div>
                            </motion.div>
                        ))}
                    </div>
                ) : (
                    <div className="empty-state">
                        <p>У вас пока нет созданных мероприятий.</p>
                        <button className="btn-primary" onClick={() => setShowCreateModal(true)}>
                            Создать первое мероприятие
                        </button>
                    </div>
                )}
            </div>

            {/* Modals */}
            <AnimatePresence>
                {showCreateModal && (
                    <CreateEventModal
                        onClose={() => setShowCreateModal(false)}
                        onSuccess={handleCreateSuccess}
                    />
                )}
                {editingEvent && (
                    <CreateEventModal
                        initialData={editingEvent}
                        onClose={() => setEditingEvent(null)}
                        onSuccess={handleEditSuccess}
                    />
                )}
                {managingAppsEvent && (
                    <ManageApplicationsModal
                        eventId={managingAppsEvent.id}
                        onClose={() => setManagingAppsEvent(null)}
                    />
                )}
            </AnimatePresence>
        </div>
    );
};

export default OrganizerPage;
