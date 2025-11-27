import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
    FiCalendar, FiMapPin, FiUsers, FiClock, FiTag,
    FiArrowLeft, FiCheck, FiX, FiInfo, FiAlertCircle
} from 'react-icons/fi';
import { eventsAPI, applicationsAPI } from '../api/api';
import { format } from 'date-fns';
import { ru } from 'date-fns/locale';

const EventDetailsPage = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [event, setEvent] = useState(null);
    const [loading, setLoading] = useState(true);
    const [applying, setApplying] = useState(false);
    const [applicationMessage, setApplicationMessage] = useState('');
    const [showApplicationForm, setShowApplicationForm] = useState(false);

    const statusTranslations = {
        'approved': 'Одобрено',
        'pending': 'На проверке',
        'completed': 'Завершено',
        'canceled': 'Отменено'
    };

    const statusColors = {
        approved: '#7fb069',
        pending: '#f4a261',
        completed: '#9c9691',
        canceled: '#e76f51',
    };

    useEffect(() => {
        loadEvent();
    }, [id]);

    const loadEvent = async () => {
        setLoading(true);
        try {
            const response = await eventsAPI.getById(id);
            setEvent(response.data);
        } catch (error) {
            console.error('Error loading event:', error);
            if (error.response?.status === 404) {
                alert('Мероприятие не найдено');
                navigate('/events');
            }
        } finally {
            setLoading(false);
        }
    };

    const handleApply = async () => {
        if (!applicationMessage.trim()) {
            alert('Пожалуйста, напишите сопроводительное сообщение');
            return;
        }

        setApplying(true);
        try {
            await applicationsAPI.create({
                event_id: event.id,
                message: applicationMessage
            });
            alert('Заявка успешно отправлена!');
            setShowApplicationForm(false);
            setApplicationMessage('');
            await loadEvent();
        } catch (error) {
            console.error('Error applying:', error);
            alert(error.response?.data?.detail || 'Ошибка при отправке заявки');
        } finally {
            setApplying(false);
        }
    };

    if (loading) {
        return (
            <div className="page-container" style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <div style={{ textAlign: 'center' }}>
                    <div className="spinner" style={{ margin: '0 auto 1rem' }}></div>
                    <p style={{ color: 'var(--text-secondary)' }}>Загрузка мероприятия...</p>
                </div>
            </div>
        );
    }

    if (!event) {
        return (
            <div className="page-container" style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <div style={{ textAlign: 'center' }}>
                    <FiAlertCircle size={64} color="var(--error)" style={{ marginBottom: '1rem' }} />
                    <h2>Мероприятие не найдено</h2>
                    <Link to="/events" className="btn btn-primary" style={{ marginTop: '1rem' }}>
                        Вернуться к списку
                    </Link>
                </div>
            </div>
        );
    }

    const canApply = event.status === 'approved' &&
                     event.approved_volunteers_count < event.required_volunteers;

    return (
        <div className="page-container" style={{ background: 'var(--primary)', paddingBottom: '4rem' }}>
            <div className="page-content" style={{ maxWidth: '1000px' }}>
                {/* Back Button */}
                <motion.button
                    onClick={() => navigate('/events')}
                    className="btn btn-ghost"
                    style={{ marginBottom: '2rem', display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}
                    whileHover={{ x: -5 }}
                >
                    <FiArrowLeft /> Назад к списку
                </motion.button>

                {/* Event Header */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="card"
                    style={{ marginBottom: '2rem' }}
                >
                    {event.event_image_url && (
                        <img
                            src={event.event_image_url}
                            alt={event.title}
                            style={{
                                width: '100%',
                                height: '400px',
                                objectFit: 'cover',
                                borderRadius: 'var(--radius-xl)',
                                marginBottom: '2rem'
                            }}
                        />
                    )}

                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem' }}>
                        <h1 style={{ fontSize: '2.5rem', fontWeight: '700', color: 'var(--text-primary)' }}>
                            {event.title}
                        </h1>
                        <span
                            style={{
                                padding: '0.5rem 1rem',
                                background: statusColors[event.status],
                                color: 'white',
                                borderRadius: 'var(--radius-full)',
                                fontSize: '0.875rem',
                                fontWeight: '600',
                                whiteSpace: 'nowrap'
                            }}
                        >
                            {statusTranslations[event.status]}
                        </span>
                    </div>

                    {/* Event Meta */}
                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                        gap: '1.5rem',
                        padding: '1.5rem',
                        background: 'var(--gray-50)',
                        borderRadius: 'var(--radius-lg)',
                        marginBottom: '2rem'
                    }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                            <FiCalendar size={20} color="var(--accent)" />
                            <div>
                                <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>Начало</div>
                                <div style={{ fontWeight: '600', color: 'var(--text-primary)' }}>
                                    {format(new Date(event.start_date), 'd MMMM yyyy, HH:mm', { locale: ru })}
                                </div>
                            </div>
                        </div>

                        {event.end_date && (
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                <FiClock size={20} color="var(--accent)" />
                                <div>
                                    <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>Окончание</div>
                                    <div style={{ fontWeight: '600', color: 'var(--text-primary)' }}>
                                        {format(new Date(event.end_date), 'd MMMM yyyy, HH:mm', { locale: ru })}
                                    </div>
                                </div>
                            </div>
                        )}

                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                            <FiMapPin size={20} color="var(--accent)" />
                            <div>
                                <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>Место</div>
                                <div style={{ fontWeight: '600', color: 'var(--text-primary)' }}>{event.location}</div>
                            </div>
                        </div>

                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                            <FiUsers size={20} color="var(--accent)" />
                            <div>
                                <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>Волонтёры</div>
                                <div style={{ fontWeight: '600', color: 'var(--text-primary)' }}>
                                    {event.approved_volunteers_count || 0} / {event.required_volunteers}
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Tags */}
                    {event.tags && event.tags.length > 0 && (
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '2rem' }}>
                            {event.tags.map(tag => (
                                <span
                                    key={tag.id}
                                    style={{
                                        display: 'inline-flex',
                                        alignItems: 'center',
                                        gap: '0.375rem',
                                        padding: '0.375rem 0.875rem',
                                        background: 'rgba(212, 165, 116, 0.1)',
                                        border: '1px solid rgba(212, 165, 116, 0.2)',
                                        borderRadius: 'var(--radius-full)',
                                        fontSize: '0.875rem',
                                        fontWeight: '500',
                                        color: 'var(--accent-dark)'
                                    }}
                                >
                                    <FiTag size={14} />
                                    {tag.name}
                                </span>
                            ))}
                        </div>
                    )}

                    {/* Description */}
                    <div style={{ marginBottom: '2rem' }}>
                        <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem', color: 'var(--text-primary)' }}>
                            Описание
                        </h3>
                        <p style={{ color: 'var(--text-secondary)', lineHeight: '1.8', fontSize: '1rem' }}>
                            {event.description || 'Описание отсутствует'}
                        </p>
                    </div>

                    {/* Apply Button */}
                    {canApply && !showApplicationForm && (
                        <button
                            onClick={() => setShowApplicationForm(true)}
                            className="btn btn-primary"
                            style={{ width: '100%', justifyContent: 'center', fontSize: '1.125rem', padding: '1rem' }}
                        >
                            <FiCheck /> Подать заявку на участие
                        </button>
                    )}

                    {!canApply && event.status === 'approved' && (
                        <div style={{
                            padding: '1rem',
                            background: 'rgba(156, 150, 145, 0.1)',
                            border: '1px solid rgba(156, 150, 145, 0.2)',
                            borderRadius: 'var(--radius-lg)',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.75rem',
                            color: 'var(--text-secondary)'
                        }}>
                            <FiInfo size={20} />
                            <span>Все места заняты</span>
                        </div>
                    )}
                </motion.div>

                {/* Application Form */}
                <AnimatePresence>
                    {showApplicationForm && (
                        <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            exit={{ opacity: 0, height: 0 }}
                            className="card"
                        >
                            <h3 style={{ fontSize: '1.5rem', fontWeight: '600', marginBottom: '1.5rem', color: 'var(--text-primary)' }}>
                                Подать заявку
                            </h3>

                            <div style={{ marginBottom: '1.5rem' }}>
                                <label style={{ display: 'block', fontWeight: '600', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>
                                    Сопроводительное сообщение *
                                </label>
                                <textarea
                                    value={applicationMessage}
                                    onChange={(e) => setApplicationMessage(e.target.value)}
                                    placeholder="Расскажите, почему вы хотите участвовать в этом мероприятии..."
                                    rows={6}
                                    style={{
                                        width: '100%',
                                        padding: '1rem',
                                        background: 'var(--gray-50)',
                                        border: '1px solid var(--gray-200)',
                                        borderRadius: 'var(--radius-lg)',
                                        fontSize: '1rem',
                                        fontFamily: 'inherit',
                                        resize: 'vertical',
                                        color: 'var(--text-primary)'
                                    }}
                                />
                            </div>

                            <div style={{ display: 'flex', gap: '1rem' }}>
                                <button
                                    onClick={() => {
                                        setShowApplicationForm(false);
                                        setApplicationMessage('');
                                    }}
                                    className="btn btn-secondary"
                                    style={{ flex: 1 }}
                                >
                                    <FiX /> Отмена
                                </button>
                                <button
                                    onClick={handleApply}
                                    disabled={applying || !applicationMessage.trim()}
                                    className="btn btn-primary"
                                    style={{ flex: 1 }}
                                >
                                    {applying ? 'Отправка...' : <><FiCheck /> Отправить заявку</>}
                                </button>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </div>
    );
};

export default EventDetailsPage;