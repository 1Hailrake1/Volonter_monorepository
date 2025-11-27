import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiSearch, FiGrid, FiList, FiMapPin, FiCalendar, FiUsers, FiArrowRight, FiX } from 'react-icons/fi';
import { format } from 'date-fns';
import { eventsAPI, publicAPI, applicationsAPI } from '../api/api';
import './EventsPage.css';

const EventsPage = () => {
    const [events, setEvents] = useState([]);
    const [allEvents, setAllEvents] = useState([]); // Store all events for search
    const [loading, setLoading] = useState(true);
    const [viewMode, setViewMode] = useState('grid');
    const [tags, setTags] = useState([]);
    const [selectedEvent, setSelectedEvent] = useState(null);
    const [applicationMessage, setApplicationMessage] = useState('');
    const [filters, setFilters] = useState({
        search: '',
        location: '',
        tag_ids: [],
        status: '',
    });

    const statusTranslations = {
        'approved': 'Одобрено',
        'pending': 'На проверке',
        'completed': 'Завершено',
        'canceled': 'Отменено'
    };

    useEffect(() => {
        loadTags();
        loadEvents();
    }, []);

    useEffect(() => {
        if (allEvents.length > 0) {
            applyFilters();
        }
    }, [filters, allEvents]);

    const loadTags = async () => {
        try {
            const response = await publicAPI.getTags();
            setTags(response.data);
        } catch (error) {
            console.error('Error loading tags:', error);
        }
    };

    const loadEvents = async () => {
        setLoading(true);
        try {
            const params = {
                page: 1,
                page_size: 100, // Load more events
            };

            if (filters.location) params.location = filters.location;
            if (filters.tag_ids.length > 0) params.tag_ids = filters.tag_ids.join(',');
            if (filters.status) params.status = filters.status;

            const response = await eventsAPI.getList(params);
            setAllEvents(response.data.events || []);
        } catch (error) {
            console.error('Error loading events:', error);
            setAllEvents([]);
        } finally {
            setLoading(false);
        }
    };

    const applyFilters = () => {
        let filtered = [...allEvents];

        // Apply search filter
        if (filters.search) {
            const searchLower = filters.search.toLowerCase();
            filtered = filtered.filter(event =>
                event.title.toLowerCase().includes(searchLower) ||
                event.location.toLowerCase().includes(searchLower)
            );
        }

        setEvents(filtered);
    };

    const handleFilterChange = (key, value) => {
        setFilters(prev => ({ ...prev, [key]: value }));
    };

    const toggleTag = (tagId) => {
        setFilters(prev => ({
            ...prev,
            tag_ids: prev.tag_ids.includes(tagId)
                ? prev.tag_ids.filter(id => id !== tagId)
                : [...prev.tag_ids, tagId]
        }));
    };

    const clearFilters = () => {
        setFilters({
            search: '',
            location: '',
            tag_ids: [],
            status: '',
        });
        setEvents(allEvents);
    };

    const handleApply = async () => {
        if (!selectedEvent) return;

        try {
            await applicationsAPI.create({
                event_id: selectedEvent.id,
                message: applicationMessage
            });
            alert('Заявка успешно отправлена!');
            setSelectedEvent(null);
            setApplicationMessage('');
        } catch (error) {
            console.error('Error applying:', error);
            alert('Ошибка при отправке заявки');
        }
    };

    return (
        <div className="page-container events-page">
            <div className="page-content">
                {/* Header */}
                <motion.div
                    className="events-header"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                >
                    <div>
                        <h1>Мероприятия</h1>
                        <p className="subtitle">Найдите подходящее мероприятие</p>
                    </div>
                    <div className="view-toggle">
                        <button
                            className={`toggle-btn ${viewMode === 'grid' ? 'active' : ''}`}
                            onClick={() => setViewMode('grid')}
                        >
                            <FiGrid />
                        </button>
                        <button
                            className={`toggle-btn ${viewMode === 'list' ? 'active' : ''}`}
                            onClick={() => setViewMode('list')}
                        >
                            <FiList />
                        </button>
                    </div>
                </motion.div>

                <div className="events-layout">
                    {/* Filters Sidebar */}
                    <motion.aside
                        className="filters-sidebar"
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.1 }}
                    >
                        <div className="filter-section">
                            <h3>Поиск</h3>
                            <div className="search-box">
                                <FiSearch />
                                <input
                                    type="text"
                                    placeholder="Название или город..."
                                    value={filters.search}
                                    onChange={(e) => handleFilterChange('search', e.target.value)}
                                />
                            </div>
                        </div>

                        <div className="filter-section">
                            <h3>Город</h3>
                            <input
                                type="text"
                                className="filter-input"
                                placeholder="Например: Москва"
                                value={filters.location}
                                onChange={(e) => handleFilterChange('location', e.target.value)}
                            />
                        </div>

                        <div className="filter-section">
                            <h3>Теги</h3>
                            <div className="tags-filter">
                                {tags.map(tag => (
                                    <button
                                        key={tag.id}
                                        className={`tag-btn ${filters.tag_ids.includes(tag.id) ? 'active' : ''}`}
                                        onClick={() => toggleTag(tag.id)}
                                    >
                                        {tag.name}
                                    </button>
                                ))}
                            </div>
                        </div>

                        <div className="filter-section">
                            <h3>Статус</h3>
                            <select
                                className="filter-select"
                                value={filters.status}
                                onChange={(e) => handleFilterChange('status', e.target.value)}
                            >
                                <option value="">Все</option>
                                <option value="approved">Одобрено</option>
                                <option value="pending">На проверке</option>
                                <option value="completed">Завершено</option>
                            </select>
                        </div>

                        <button className="btn-clear" onClick={clearFilters}>
                            Сбросить фильтры
                        </button>
                    </motion.aside>

                    {/* Events Content */}
                    <div className="events-content">
                        {loading ? (
                            <div className="loading-spinner">
                                <div className="spinner"></div>
                                <p>Загрузка мероприятий...</p>
                            </div>
                        ) : events.length > 0 ? (
                            <div className={`events-${viewMode}`}>
                                {events.map((event, index) => (
                                    <EventCard
                                        key={event.id}
                                        event={event}
                                        viewMode={viewMode}
                                        index={index}
                                        onDetails={() => setSelectedEvent(event)}
                                        statusTranslations={statusTranslations}
                                    />
                                ))}
                            </div>
                        ) : (
                            <div className="empty-state">
                                <p>Мероприятия не найдены</p>
                                <button className="btn-primary" onClick={clearFilters}>
                                    Сбросить фильтры
                                </button>
                            </div>
                        )}
                    </div>
                </div>

                {/* Event Detail Modal */}
                <AnimatePresence>
                    {selectedEvent && (
                        <motion.div
                            className="modal-overlay"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            onClick={() => setSelectedEvent(null)}
                        >
                            <motion.div
                                className="modal-content event-modal"
                                initial={{ scale: 0.9, opacity: 0 }}
                                animate={{ scale: 1, opacity: 1 }}
                                exit={{ scale: 0.9, opacity: 0 }}
                                onClick={(e) => e.stopPropagation()}
                            >
                                <div className="modal-header">
                                    <h3>{selectedEvent.title}</h3>
                                    <button className="btn-close" onClick={() => setSelectedEvent(null)}>
                                        <FiX />
                                    </button>
                                </div>
                                <div className="modal-body">
                                    {selectedEvent.event_image_url && (
                                        <img src={selectedEvent.event_image_url} alt={selectedEvent.title} className="event-modal-image" />
                                    )}
                                    <div className="event-modal-info">
                                        <div className="info-row">
                                            <FiCalendar />
                                            <span>{format(new Date(selectedEvent.start_date), 'dd.MM.yyyy HH:mm')}</span>
                                        </div>
                                        <div className="info-row">
                                            <FiMapPin />
                                            <span>{selectedEvent.location}</span>
                                        </div>
                                        <div className="info-row">
                                            <FiUsers />
                                            <span>Требуется: {selectedEvent.required_volunteers} волонтёров</span>
                                        </div>
                                        <div className="info-row">
                                            <span className="status-badge">{statusTranslations[selectedEvent.status]}</span>
                                        </div>
                                    </div>
                                    <div className="event-description">
                                        <h4>Описание</h4>
                                        <p>{selectedEvent.description || 'Описание отсутствует'}</p>
                                    </div>
                                    <div className="application-form">
                                        <h4>Сопроводительное сообщение (необязательно)</h4>
                                        <textarea
                                            className="application-textarea"
                                            placeholder="Расскажите о себе и почему хотите участвовать..."
                                            value={applicationMessage}
                                            onChange={(e) => setApplicationMessage(e.target.value)}
                                            rows={4}
                                        />
                                    </div>
                                </div>
                                <div className="modal-footer">
                                    <button className="btn-secondary" onClick={() => setSelectedEvent(null)}>
                                        Отмена
                                    </button>
                                    <button className="btn-primary" onClick={handleApply}>
                                        Подать заявку
                                    </button>
                                </div>
                            </motion.div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </div>
    );
};

const EventCard = ({ event, viewMode, index, onDetails, statusTranslations }) => {
    const statusColors = {
        approved: 'var(--success)',
        pending: 'var(--warning)',
        completed: 'var(--gray-500)',
        canceled: 'var(--error)',
    };

    return (
        <motion.div
            className={`event-card ${viewMode}`}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            whileHover={{ y: -5 }}
        >
            <div className="event-image">
                {event.event_image_url ? (
                    <img src={event.event_image_url} alt={event.title} />
                ) : (
                    <div className="event-placeholder">
                        <span>Нет изображения</span>
                    </div>
                )}
                <div className="event-status" style={{ background: statusColors[event.status] }}>
                    {statusTranslations[event.status]}
                </div>
            </div>
            <div className="event-body">
                <h3>{event.title}</h3>
                <div className="event-meta">
                    <div className="meta-item">
                        <FiMapPin />
                        <span>{event.location}</span>
                    </div>
                    <div className="meta-item">
                        <FiCalendar />
                        <span>{format(new Date(event.start_date), 'dd.MM.yyyy')}</span>
                    </div>
                    <div className="meta-item">
                        <FiUsers />
                        <span>{event.approved_volunteers_count || 0}/{event.required_volunteers}</span>
                    </div>
                </div>
                {event.tags && event.tags.length > 0 && (
                    <div className="event-tags">
                        {event.tags.map(tag => (
                            <span key={tag.id} className="tag">{tag.name}</span>
                        ))}
                    </div>
                )}
                <button className="btn-view" onClick={onDetails}>
                    Подробнее <FiArrowRight />
                </button>
            </div>
        </motion.div>
    );
};

export default EventsPage;
