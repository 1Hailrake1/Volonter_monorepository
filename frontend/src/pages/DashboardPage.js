import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiTrendingUp, FiAward, FiCalendar, FiUsers, FiX, FiPlus, FiCheck, FiSave } from 'react-icons/fi';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { usersAPI, publicAPI } from '../api/api';
import './DashboardPage.css';

const DashboardPage = ({ user }) => {
    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(true);
    const [showSkillModal, setShowSkillModal] = useState(false);
    const [availableSkills, setAvailableSkills] = useState([]);
    const [selectedSkill, setSelectedSkill] = useState(null);
    const [editMode, setEditMode] = useState(false);
    const [editedProfile, setEditedProfile] = useState({});
    const [saving, setSaving] = useState(false);

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
        loadProfile();
        loadSkills();
    }, []);

    const loadProfile = async () => {
        try {
            const response = await usersAPI.getMyProfile();
            setProfile(response.data);
            setEditedProfile({
                fullname: response.data.fullname,
                email: response.data.email,
                location: response.data.location,
            });
        } catch (error) {
            console.error('Error loading profile:', error);
        } finally {
            setLoading(false);
        }
    };

    const loadSkills = async () => {
        try {
            const response = await publicAPI.getSkills();
            setAvailableSkills(response.data);
        } catch (error) {
            console.error('Error loading skills:', error);
        }
    };

    const handleAddSkill = async () => {
        if (!selectedSkill) return;

        try {
            await usersAPI.addSkill(selectedSkill);
            setShowSkillModal(false);
            setSelectedSkill(null);
            await loadProfile();
        } catch (error) {
            console.error('Error adding skill:', error);
            alert('Ошибка при добавлении навыка');
        }
    };

    const handleSaveProfile = async () => {
        setSaving(true);
        try {
            await usersAPI.updateProfile(editedProfile);
            await loadProfile();
            setEditMode(false);
        } catch (error) {
            console.error('Error saving profile:', error);
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

                {/* Stats Grid */}
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

                {/* Profile Edit Section */}
                <motion.div
                    className="card profile-card"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.5 }}
                >
                    <div className="card-header">
                        <h3>Профиль</h3>
                        {!editMode ? (
                            <button className="btn-icon" onClick={() => setEditMode(true)}>
                                Редактировать
                            </button>
                        ) : (
                            <div className="edit-actions">
                                <button className="btn-secondary" onClick={() => setEditMode(false)}>
                                    Отмена
                                </button>
                                <button className="btn-icon" onClick={handleSaveProfile} disabled={saving}>
                                    <FiSave /> {saving ? 'Сохранение...' : 'Сохранить'}
                                </button>
                            </div>
                        )}
                    </div>
                    <div className="profile-fields">
                        <div className="field-group">
                            <label>Имя</label>
                            {editMode ? (
                                <input
                                    type="text"
                                    value={editedProfile.fullname}
                                    onChange={(e) => setEditedProfile({ ...editedProfile, fullname: e.target.value })}
                                    className="profile-input"
                                />
                            ) : (
                                <p>{profile?.fullname}</p>
                            )}
                        </div>
                        <div className="field-group">
                            <label>Email</label>
                            {editMode ? (
                                <input
                                    type="email"
                                    value={editedProfile.email}
                                    onChange={(e) => setEditedProfile({ ...editedProfile, email: e.target.value })}
                                    className="profile-input"
                                />
                            ) : (
                                <p>{profile?.email}</p>
                            )}
                        </div>
                        <div className="field-group">
                            <label>Город</label>
                            {editMode ? (
                                <input
                                    type="text"
                                    value={editedProfile.location || ''}
                                    onChange={(e) => setEditedProfile({ ...editedProfile, location: e.target.value })}
                                    className="profile-input"
                                />
                            ) : (
                                <p>{profile?.location || 'Не указан'}</p>
                            )}
                        </div>
                    </div>
                </motion.div>

                {/* Skills Section */}
                <motion.div
                    className="card skills-card"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.6 }}
                >
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
                </motion.div>

                {/* Activity Chart */}
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
