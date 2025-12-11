import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiTrendingUp, FiAward, FiCalendar, FiUsers, FiX, FiPlus, FiCheck, FiSave, FiList, FiSettings } from 'react-icons/fi';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { usersAPI, publicAPI, eventsAPI } from '../api/api';
import { useNotification } from '../contexts/NotificationContext';
import './DashboardPage.css';

const DashboardPage = ({ user }) => {
    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('overview'); // overview, organized, settings

    // Skills
    const [showSkillModal, setShowSkillModal] = useState(false);
    const [availableSkills, setAvailableSkills] = useState([]);
    const [selectedSkill, setSelectedSkill] = useState(null);

    // Profile Edit
    const [editedProfile, setEditedProfile] = useState({});
    const [saving, setSaving] = useState(false);
    const { notify } = useNotification();

    // Mock data for activity chart
    const activityData = [
        { month: 'Янв', events: 2 },
        { month: 'Фев', events: 3 },
        { month: 'Мар', events: 5 },
        { month: 'Апр', events: 4 },
        { month: 'Май', events: 6 },
        { month: 'Июн', events: 8 },
    ];

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        setLoading(true);
        try {
            const [profileRes, skillsRes] = await Promise.all([
                usersAPI.getMyProfile(),
                publicAPI.getSkills()
            ]);

            setProfile(profileRes.data);
            setEditedProfile({
                fullname: profileRes.data.fullname,
                email: profileRes.data.email,
                location: profileRes.data.location,
            });
            // Fix: response structure is { skills: [...], total: ... }
            setAvailableSkills(skillsRes.data.skills || []);

            // Check if organizer
            const isOrganizer = profileRes.data.roles?.some(r => r.name === 'organizer' || r.name === 'admin');

        } catch (error) {
            console.error('Error loading dashboard data:', error);
            notify('Ошибка загрузки данных', 'error');
        } finally {
            setLoading(false);
        }
    };

    const handleAddSkill = async () => {
        if (!selectedSkill) return;

        const skillToAdd = availableSkills.find(s => s.id === parseInt(selectedSkill));
        if (!skillToAdd) return;

        const currentSkills = profile.skills || [];
        if (currentSkills.some(s => s.id === skillToAdd.id)) return;

        const updatedSkills = [...currentSkills, skillToAdd];

        try {
            await usersAPI.updateProfile({
                id: profile.id,
                ...editedProfile,
                skills: updatedSkills
            });

            setShowSkillModal(false);
            setSelectedSkill(null);

            const res = await usersAPI.getMyProfile();
            setProfile(res.data);
            setEditedProfile({
                fullname: res.data.fullname,
                email: res.data.email,
                location: res.data.location,
            });
            notify('Навык успешно добавлен', 'success');
        } catch (error) {
            console.error('Error adding skill:', error);
            notify('Ошибка при добавлении навыка', 'error');
        }
    };

    const handleSaveProfile = async () => {
        setSaving(true);
        try {
            await usersAPI.updateProfile({
                id: profile.id,
                ...editedProfile,
                skills: profile.skills || []
            });
            const res = await usersAPI.getMyProfile();
            setProfile(res.data);
            notify('Профиль успешно обновлен', 'success');
        } catch (error) {
            console.error('Error saving profile:', error);
            notify('Ошибка при сохранении профиля', 'error');
        } finally {
            setSaving(false);
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

    const stats = profile?.statistics || {};
    const userSkillIds = profile?.skills?.map(s => s.id) || [];
    const filteredSkills = availableSkills.filter(skill => !userSkillIds.includes(skill.id));
    const isOrganizer = profile?.roles?.some(r => r.name === 'organizer' || r.name === 'admin');

    return (
        <div className="page-container dashboard-page">
            <div className="page-content">
                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="dashboard-header"
                >
                    <div>
                        <h1>Личный кабинет</h1>
                        <p className="subtitle">Добро пожаловать, {profile?.fullname}!</p>
                    </div>
                </motion.div>

                {/* Custom Tabs */}
                <div style={{ display: 'flex', gap: '20px', marginBottom: '30px', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '10px' }}>
                    <button
                        className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
                        onClick={() => setActiveTab('overview')}
                        style={{ background: 'none', border: 'none', color: activeTab === 'overview' ? 'var(--accent)' : 'var(--gray-400)', fontSize: '18px', cursor: 'pointer', paddingBottom: '5px', borderBottom: activeTab === 'overview' ? '2px solid var(--accent)' : 'none' }}
                    >
                        <FiTrendingUp style={{ marginRight: '8px' }} /> Обзор
                    </button>
                    {isOrganizer && (
                        <button
                            className={`tab-btn ${activeTab === 'organized' ? 'active' : ''}`}
                            onClick={() => setActiveTab('organized')}
                            style={{ background: 'none', border: 'none', color: activeTab === 'organized' ? 'var(--accent)' : 'var(--gray-400)', fontSize: '18px', cursor: 'pointer', paddingBottom: '5px', borderBottom: activeTab === 'organized' ? '2px solid var(--accent)' : 'none' }}
                        >
                            <FiList style={{ marginRight: '8px' }} />  Мои мероприятия
                        </button>
                    )}
                    <button
                        className={`tab-btn ${activeTab === 'settings' ? 'active' : ''}`}
                        onClick={() => setActiveTab('settings')}
                        style={{ background: 'none', border: 'none', color: activeTab === 'settings' ? 'var(--accent)' : 'var(--gray-400)', fontSize: '18px', cursor: 'pointer', paddingBottom: '5px', borderBottom: activeTab === 'settings' ? '2px solid var(--accent)' : 'none' }}
                    >
                        <FiSettings style={{ marginRight: '8px' }} /> Настройки
                    </button>
                </div>

                {/* OVERVIEW TAB */}
                {activeTab === 'overview' && (
                    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                        <div className="stats-grid">
                            <StatCard
                                icon={<FiCalendar />}
                                label="Мероприятий посещено"
                                value={stats.total_events_participated || 0}
                                color="var(--accent)"
                                delay={0.1}
                            />
                            <StatCard
                                icon={<FiUsers />}
                                label="Организовано"
                                value={stats.total_events_organized || 0}
                                color="var(--secondary)"
                                delay={0.2}
                            />
                            <StatCard
                                icon={<FiAward />}
                                label="Средний рейтинг"
                                value={stats.average_rating?.toFixed(1) || 'N/A'}
                                color="var(--success)"
                                delay={0.3}
                            />
                            <StatCard
                                icon={<FiTrendingUp />}
                                label="Отзывов получено"
                                value={stats.reviews_count || 0}
                                color="var(--warning)"
                                delay={0.4}
                            />
                        </div>

                        <motion.div
                            className="card chart-card"
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.7 }}
                        >
                            <h3>Активность</h3>
                            <ResponsiveContainer width="100%" height={300}>
                                <AreaChart data={activityData}>
                                    <defs>
                                        <linearGradient id="colorEvents" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="var(--accent)" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="var(--accent)" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                                    <XAxis dataKey="month" stroke="var(--gray-400)" />
                                    <YAxis stroke="var(--gray-400)" />
                                    <Tooltip
                                        contentStyle={{
                                            background: 'var(--primary-light)',
                                            border: '1px solid rgba(255,255,255,0.1)',
                                            borderRadius: '8px',
                                        }}
                                    />
                                    <Area
                                        type="monotone"
                                        dataKey="events"
                                        stroke="var(--accent)"
                                        fillOpacity={1}
                                        fill="url(#colorEvents)"
                                    />
                                </AreaChart>
                            </ResponsiveContainer>
                        </motion.div>
                    </motion.div>
                )}

                {/* SETTINGS TAB (Profile & Skills) */}
                {activeTab === 'settings' && (
                    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                        <div className="card profile-card" style={{ marginBottom: '20px' }}>
                            <div className="card-header">
                                <h3>Профиль</h3>
                                <button className="btn-icon" onClick={handleSaveProfile} disabled={saving}>
                                    <FiSave /> {saving ? 'Сохранение...' : 'Сохранить изменения'}
                                </button>
                            </div>
                            <div className="profile-fields">
                                <div className="field-group">
                                    <label>Имя</label>
                                    <input
                                        type="text"
                                        value={editedProfile.fullname || ''}
                                        onChange={(e) => setEditedProfile({ ...editedProfile, fullname: e.target.value })}
                                        className="profile-input"
                                    />
                                </div>
                                <div className="field-group">
                                    <label>Email</label>
                                    <input
                                        disabled
                                        type="email"
                                        value={editedProfile.email || ''}
                                        className="profile-input"
                                        style={{ opacity: 0.7 }}
                                    />
                                </div>
                                <div className="field-group">
                                    <label>Город</label>
                                    <input
                                        type="text"
                                        value={editedProfile.location || ''}
                                        onChange={(e) => setEditedProfile({ ...editedProfile, location: e.target.value })}
                                        className="profile-input"
                                    />
                                </div>
                            </div>
                        </div>

                        <div className="card skills-card">
                            <div className="card-header">
                                <h3>Навыки</h3>
                                <button className="btn-icon" onClick={() => setShowSkillModal(true)}>
                                    <FiPlus /> Добавить
                                </button>
                            </div>
                            <div className="skills-list">
                                {profile?.skills?.length > 0 ? (
                                    profile.skills.map((skill, index) => (
                                        <motion.span
                                            key={skill.id}
                                            className="skill-tag"
                                            initial={{ opacity: 0, scale: 0.8 }}
                                            animate={{ opacity: 1, scale: 1 }}
                                            transition={{ delay: 0.7 + index * 0.05 }}
                                        >
                                            <FiCheck className="skill-icon" />
                                            {skill.name}
                                        </motion.span>
                                    ))
                                ) : (
                                    <p className="empty-state">Навыки не добавлены</p>
                                )}
                            </div>
                        </div>
                    </motion.div>
                )}


                {/* Add Skill Modal */}
                <AnimatePresence>
                    {showSkillModal && (
                        <motion.div
                            className="modal-overlay"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            onClick={() => setShowSkillModal(false)}
                        >
                            <motion.div
                                className="modal-content"
                                initial={{ scale: 0.9, opacity: 0 }}
                                animate={{ scale: 1, opacity: 1 }}
                                exit={{ scale: 0.9, opacity: 0 }}
                                onClick={(e) => e.stopPropagation()}
                            >
                                <div className="modal-header">
                                    <h3>Добавить навык</h3>
                                    <button className="btn-close" onClick={() => setShowSkillModal(false)}>
                                        <FiX />
                                    </button>
                                </div>
                                <div className="modal-body">
                                    {filteredSkills.length > 0 ? (
                                        <select
                                            className="skill-select"
                                            value={selectedSkill || ''}
                                            onChange={(e) => setSelectedSkill(e.target.value)}
                                        >
                                            <option value="">Выберите навык</option>
                                            {filteredSkills.map(skill => (
                                                <option key={skill.id} value={skill.id}>
                                                    {skill.name}
                                                </option>
                                            ))}
                                        </select>
                                    ) : (
                                        <p className="empty-state">Все навыки уже добавлены</p>
                                    )}
                                </div>
                                <div className="modal-footer">
                                    <button className="btn-secondary" onClick={() => setShowSkillModal(false)}>
                                        Отмена
                                    </button>
                                    <button
                                        className="btn-primary"
                                        onClick={handleAddSkill}
                                        disabled={!selectedSkill}
                                    >
                                        Добавить
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

const StatCard = ({ icon, label, value, color, delay }) => (
    <motion.div
        className="stat-card glass-card"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay }}
        whileHover={{ y: -5 }}
    >
        <div className="stat-icon-small" style={{ color }}>
            {icon}
        </div>
        <div className="stat-content">
            <div className="stat-value">{value}</div>
            <div className="stat-label">{label}</div>
        </div>
    </motion.div>
);

export default DashboardPage;
