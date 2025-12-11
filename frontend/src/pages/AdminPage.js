import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiUsers, FiCalendar, FiFileText, FiCheck, FiX, FiEdit } from 'react-icons/fi';
import { adminAPI, eventsAPI } from '../api/api';
import RoleChangeModal from '../components/RoleChangeModal';
import { useNotification } from '../contexts/NotificationContext';
import { useConfirm } from '../contexts/ConfirmationContext';
import { format } from 'date-fns';
import { ru } from 'date-fns/locale';
import './AdminPage.css';

const AdminPage = () => {
    const [stats, setStats] = useState(null);
    const [pendingEvents, setPendingEvents] = useState([]);
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('overview');
    const [editingUser, setEditingUser] = useState(null);
    const { notify } = useNotification();
    const { confirm } = useConfirm();

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        setLoading(true);
        try {
            const [statsRes, eventsRes, usersRes] = await Promise.all([
                adminAPI.getStatistics(),
                eventsAPI.getList({ status: 'pending', page: 1, page_size: 50 }),
                adminAPI.getUsers({ page: 1, page_size: 50 })
            ]);

            setStats(statsRes.data);
            setPendingEvents(eventsRes.data.events || []);
            setUsers(usersRes.data.users || []);
        } catch (error) {
            console.error('Error loading admin data:', error);
            notify('Ошибка загрузки данных', 'error');
        } finally {
            setLoading(false);
        }
    };

    const handleRoleChangeSuccess = () => {
        setEditingUser(null);
        loadData();
    };

    const handleApproveEvent = async (eventId) => {
        try {
            await eventsAPI.updateStatus(eventId, 'approved');
            notify('Мероприятие одобрено', 'success');
            await loadData();
        } catch (error) {
            console.error('Error approving event:', error);
            notify('Ошибка при одобрении мероприятия', 'error');
        }
    };

    const handleRejectEvent = (eventId) => {
        confirm({
            title: 'Отклонение мероприятия',
            message: 'Вы уверены, что хотите отклонить это мероприятие?',
            onConfirm: async () => {
                try {
                    await eventsAPI.updateStatus(eventId, 'canceled');
                    notify('Мероприятие отклонено', 'success');
                    await loadData();
                } catch (error) {
                    console.error('Error rejecting event:', error);
                    notify('Ошибка при отклонении мероприятия', 'error');
                }
            }
        });
    };

    const handleBlockUser = (userId) => {
        confirm({
            title: 'Блокировка пользователя',
            message: 'Вы уверены, что хотите заблокировать этого пользователя?',
            onConfirm: async () => {
                try {
                    await adminAPI.blockUser(userId);
                    notify('Пользователь заблокирован', 'success');
                    await loadData();
                } catch (error) {
                    console.error('Error blocking user:', error);
                    notify('Ошибка при блокировке пользователя', 'error');
                }
            }
        });
    };

    const handleUnblockUser = async (userId) => {
        try {
            await adminAPI.unblockUser(userId);
            notify('Пользователь разблокирован', 'success');
            await loadData();
        } catch (error) {
            console.error('Error unblocking user:', error);
            notify('Ошибка при разблокировке пользователя', 'error');
        }
    };

    if (loading) {
        return (
            <div className="page-container">
                <div className="loading-spinner">
                    <div className="spinner"></div>
                    <p>Загрузка...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="page-container admin-page">
            <div className="page-content">
                {/* Header */}
                <motion.div
                    className="admin-header"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                >
                    <div>
                        <h1>Админ-панель</h1>
                        <p className="subtitle">Управление платформой</p>
                    </div>
                </motion.div>

                {/* Tabs */}
                <div className="admin-tabs">
                    <button
                        className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
                        onClick={() => setActiveTab('overview')}
                    >
                        Обзор
                    </button>
                    <button
                        className={`tab-btn ${activeTab === 'events' ? 'active' : ''}`}
                        onClick={() => setActiveTab('events')}
                    >
                        Мероприятия ({pendingEvents.length})
                    </button>
                    <button
                        className={`tab-btn ${activeTab === 'users' ? 'active' : ''}`}
                        onClick={() => setActiveTab('users')}
                    >
                        Пользователи
                    </button>
                </div>

                {/* Overview Tab */}
                {activeTab === 'overview' && stats && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="overview-section"
                    >
                        <div className="stats-grid">
                            <StatCard
                                icon={<FiUsers />}
                                title="Всего пользователей"
                                value={stats.total_users || 0}
                                color="var(--accent)"
                            />
                            <StatCard
                                icon={<FiCalendar />}
                                title="Всего мероприятий"
                                value={stats.total_events || 0}
                                color="var(--secondary)"
                            />
                            <StatCard
                                icon={<FiFileText />}
                                title="Всего заявок"
                                value={stats.total_applications || 0}
                                color="var(--success)"
                            />
                            <StatCard
                                icon={<FiCalendar />}
                                title="На рассмотрении"
                                value={pendingEvents.length}
                                color="var(--warning)"
                            />
                        </div>
                    </motion.div>
                )}

                {/* Events Tab */}
                {activeTab === 'events' && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="events-section"
                    >
                        <h2>Мероприятия на рассмотрении</h2>
                        {pendingEvents.length > 0 ? (
                            <div className="events-table">
                                {pendingEvents.map((event) => (
                                    <EventRow
                                        key={event.id}
                                        event={event}
                                        onApprove={handleApproveEvent}
                                        onReject={handleRejectEvent}
                                    />
                                ))}
                            </div>
                        ) : (
                            <div className="empty-state">
                                <p>Нет мероприятий на рассмотрении</p>
                            </div>
                        )}
                    </motion.div>
                )}

                {/* Users Tab */}
                {activeTab === 'users' && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="users-section"
                    >
                        <h2>Пользователи платформы</h2>
                        {users.length > 0 ? (
                            <div className="users-table">
                                {users.map((user) => (
                                    <UserRow
                                        key={user.id}
                                        user={user}
                                        onBlock={handleBlockUser}
                                        onUnblock={handleUnblockUser}
                                        onEditRole={() => setEditingUser(user)} // Pass handler
                                    />
                                ))}
                            </div>
                        ) : (
                            <div className="empty-state">
                                <p>Пользователи не найдены</p>
                            </div>
                        )}
                    </motion.div>
                )}
            </div>

            {/* Role Change Modal */}
            <AnimatePresence>
                {editingUser && (
                    <RoleChangeModal
                        user={editingUser}
                        onClose={() => setEditingUser(null)}
                        onSuccess={handleRoleChangeSuccess}
                    />
                )}
            </AnimatePresence>
        </div>
    );
};

const StatCard = ({ icon, title, value, color }) => (
    <motion.div
        className="stat-card"
        whileHover={{ y: -4 }}
    >
        <div className="stat-icon" style={{ color }}>
            {icon}
        </div>
        <div className="stat-content">
            <div className="stat-value">{value}</div>
            <div className="stat-label">{title}</div>
        </div>
    </motion.div>
);

const EventRow = ({ event, onApprove, onReject }) => (
    <div className="table-row">
        <div className="row-content">
            <div>
                <h4>{event.title}</h4>
                <div className="row-meta">
                    <span>{event.location}</span>
                    <span>•</span>
                    <span>{format(new Date(event.start_date), 'd MMMM yyyy', { locale: ru })}</span>
                    <span>•</span>
                    <span>Требуется: {event.required_volunteers} волонтёров</span>
                </div>
            </div>
        </div>
        <div className="row-actions">
            <button
                className="btn-approve"
                onClick={() => onApprove(event.id)}
                title="Одобрить"
            >
                <FiCheck />
            </button>
            <button
                className="btn-reject"
                onClick={() => onReject(event.id)}
                title="Отклонить"
            >
                <FiX />
            </button>
        </div>
    </div>
);

const UserRow = ({ user, onBlock, onUnblock, onEditRole }) => (
    <div className="table-row">
        <div className="row-content">
            <div>
                <h4>{user.fullname || 'Без имени'}</h4>
                <div className="row-meta">
                    <span>{user.email}</span>
                    <span>•</span>
                    <span>Рег: {user.date_created ? format(new Date(user.date_created), 'dd.MM.yyyy', { locale: ru }) : '-'}</span>
                    {user.location && (
                        <>
                            <span>•</span>
                            <span>{user.location}</span>
                        </>
                    )}
                </div>
            </div>
        </div>
        <div className="row-info">
            <span className="role-badge">
                {user.roles?.[0]?.name || 'Пользователь'}
                {user.roles?.length > 1 && ` +${user.roles.length - 1}`}
            </span>
        </div>
        <div className="row-actions">
            {/* Edit Role Button */}
            <button
                className="btn-primary"
                style={{ padding: '8px', marginRight: '5px' }}
                onClick={onEditRole}
                title="Изменить роль"
            >
                <FiEdit />
            </button>

            {user.is_active !== false ? (
                <button
                    className="btn-reject"
                    onClick={() => onBlock(user.id)}
                    title="Заблокировать"
                >
                    <FiX />
                </button>
            ) : (
                <button
                    className="btn-approve"
                    onClick={() => onUnblock(user.id)}
                    title="Разблокировать"
                >
                    <FiCheck />
                </button>
            )}
        </div>
    </div>
);

export default AdminPage;
