import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FiSearch, FiCalendar, FiMapPin, FiClock, FiX } from 'react-icons/fi';
import { applicationsAPI } from '../api/api';
import { format, parseISO, isValid } from 'date-fns';
import { ru } from 'date-fns/locale';
import { useConfirm } from '../contexts/ConfirmationContext';
import { useNotification } from '../contexts/NotificationContext';
import './MyApplicationsPage.css';

const MyApplicationsPage = () => {
    const [applications, setApplications] = useState([]);
    const [filteredApplications, setFilteredApplications] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [statusFilter, setStatusFilter] = useState('all');
    const { confirm } = useConfirm();
    const { notify } = useNotification();

    const statusTranslations = {
        pending: 'На рассмотрении',
        approved: 'Одобрено',
        rejected: 'Отклонено'
    };

    const statusColors = {
        pending: 'var(--warning)',
        approved: 'var(--success)',
        rejected: 'var(--error)'
    };

    useEffect(() => {
        loadApplications();
    }, []);

    useEffect(() => {
        filterApplications();
    }, [searchTerm, statusFilter, applications]);

    const loadApplications = async () => {
        setLoading(true);
        try {
            const response = await applicationsAPI.getMyApplications();
            const data = response.data;
            setApplications(Array.isArray(data) ? data : (data?.applications || []));
        } catch (error) {
            console.error('Error loading applications:', error);
            setApplications([]);
            notify('Ошибка при загрузке заявок', 'error');
        } finally {
            setLoading(false);
        }
    };

    const filterApplications = () => {
        if (!Array.isArray(applications)) {
            setFilteredApplications([]);
            return;
        }

        let filtered = [...applications];

        if (searchTerm) {
            const searchLower = searchTerm.toLowerCase();
            filtered = filtered.filter(app =>
                app.event?.title?.toLowerCase().includes(searchLower) ||
                app.event?.location?.toLowerCase().includes(searchLower)
            );
        }

        if (statusFilter !== 'all') {
            filtered = filtered.filter(app => app.status === statusFilter);
        }

        setFilteredApplications(filtered);
    };

    const handleCancelApplication = (applicationId) => {
        confirm({
            title: 'Отмена заявки',
            message: 'Вы уверены, что хотите отменить эту заявку?',
            onConfirm: async () => {
                try {
                    await applicationsAPI.cancel(applicationId);
                    notify('Заявка успешно отменена', 'success');
                    await loadApplications();
                } catch (error) {
                    console.error('Error canceling application:', error);
                    notify('Ошибка при отмене заявки', 'error');
                }
            }
        });
    };

    if (loading) {
        return (
            <div className="page-container">
                <div className="loading-spinner">
                    <div className="spinner"></div>
                    <p>Загрузка заявок...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="page-container applications-page">
            <div className="page-content">
                <motion.div
                    className="applications-header"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                >
                    <div>
                        <h1>Мои заявки</h1>
                        <p className="subtitle">Управление заявками на мероприятия</p>
                    </div>
                </motion.div>

                <motion.div
                    className="filters-bar"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                >
                    <div className="search-box">
                        <FiSearch />
                        <input
                            type="text"
                            placeholder="Поиск по названию или городу..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>

                    <select
                        className="status-filter"
                        value={statusFilter}
                        onChange={(e) => setStatusFilter(e.target.value)}
                    >
                        <option value="all">Все статусы</option>
                        <option value="pending">На рассмотрении</option>
                        <option value="approved">Одобрено</option>
                        <option value="rejected">Отклонено</option>
                    </select>
                </motion.div>

                {filteredApplications.length > 0 ? (
                    <div className="applications-list">
                        {filteredApplications.map((application, index) => (
                            <ApplicationCard
                                key={application.id}
                                application={application}
                                index={index}
                                onCancel={handleCancelApplication}
                                statusTranslations={statusTranslations}
                                statusColors={statusColors}
                            />
                        ))}
                    </div>
                ) : (
                    <div className="empty-state">
                        <p>Заявки не найдены</p>
                        {(searchTerm || statusFilter !== 'all') && (
                            <button
                                className="btn-primary"
                                onClick={() => {
                                    setSearchTerm('');
                                    setStatusFilter('all');
                                }}
                            >
                                Сбросить фильтры
                            </button>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

const ApplicationCard = ({ application, index, onCancel, statusTranslations, statusColors }) => {
    const event = application.event || {};
    const canCancel = application.status === 'pending';

    // ИСПРАВЛЕНИЕ: Безопасное форматирование дат
    const formatSafeDate = (dateString, formatStr) => {
        if (!dateString) return 'Дата не указана';

        try {
            const date = parseISO(dateString);
            if (!isValid(date)) return 'Неверная дата';
            return format(date, formatStr, { locale: ru });
        } catch (error) {
            console.error('Date formatting error:', error, dateString);
            return 'Неверная дата';
        }
    };

    return (
        <motion.div
            className="application-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
        >
            <div className="application-header">
                <div>
                    <h3>{event.title || 'Без названия'}</h3>
                    <div className="application-meta">
                        <div className="meta-item">
                            <FiCalendar />
                            <span>{formatSafeDate(event.start_date, 'd MMMM yyyy')}</span>
                        </div>
                        <div className="meta-item">
                            <FiMapPin />
                            <span>{event.location || 'Место не указано'}</span>
                        </div>
                    </div>
                </div>
                <div
                    className="status-badge"
                    style={{ background: statusColors[application.status] }}
                >
                    {statusTranslations[application.status]}
                </div>
            </div>

            {application.message && (
                <div className="application-message">
                    <strong>Сопроводительное сообщение:</strong>
                    <p>{application.message}</p>
                </div>
            )}

            <div className="application-footer">
                <div className="application-date">
                    <FiClock />
                    <span>
                        Подано: {formatSafeDate(application.date_created, 'd MMMM yyyy, HH:mm')}
                    </span>
                </div>
                {canCancel && (
                    <button
                        className="btn-cancel"
                        onClick={() => onCancel(application.id)}
                    >
                        <FiX />
                        Отменить заявку
                    </button>
                )}
            </div>
        </motion.div>
    );
};

export default MyApplicationsPage;