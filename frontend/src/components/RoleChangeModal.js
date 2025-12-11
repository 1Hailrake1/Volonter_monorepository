import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiX, FiCheck } from 'react-icons/fi';
import { adminAPI } from '../api/api';
import { useNotification } from '../contexts/NotificationContext';

const RoleChangeModal = ({ user, onClose, onSuccess }) => {
    const [availableRoles, setAvailableRoles] = useState([]);
    const [selectedRoleIds, setSelectedRoleIds] = useState([]);
    const [loading, setLoading] = useState(false);
    const [loadingRoles, setLoadingRoles] = useState(true);
    const { notify } = useNotification();

    useEffect(() => {
        loadRoles();
        if (user && user.roles) {
            setSelectedRoleIds(user.roles.map(r => r.id));
        }
    }, [user]);

    const loadRoles = async () => {
        try {
            const response = await adminAPI.getRoles();
            setAvailableRoles(response.data.roles || []);
        } catch (error) {
            console.error('Error loading roles:', error);
            notify('Не удалось загрузить список ролей', 'error');
        } finally {
            setLoadingRoles(false);
        }
    };

    const toggleRole = (roleId) => {
        setSelectedRoleIds(prev =>
            prev.includes(roleId)
                ? prev.filter(id => id !== roleId)
                : [...prev, roleId]
        );
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        setLoading(true);
        try {
            // Map selected IDs back to role objects (backend expects list[RoleRead])
            const newRoles = availableRoles.filter(role => selectedRoleIds.includes(role.id));

            await adminAPI.changeUserRole(user.id, newRoles);
            notify(`Роли пользователя ${user.fullname} обновлены`, 'success');
            onSuccess();
            onClose();
        } catch (error) {
            console.error('Error changing roles:', error);
            notify('Ошибка при изменении ролей', 'error');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <motion.div
                className="modal-content glass-card"
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
                onClick={e => e.stopPropagation()}
                style={{ maxWidth: '500px' }}
            >
                <div className="modal-header">
                    <h3>Управление ролями</h3>
                    <button className="btn-close" onClick={onClose}><FiX /></button>
                </div>

                <div className="modal-body">
                    <p style={{ marginBottom: '20px', color: 'var(--text-secondary)' }}>
                        Пользователь: <strong>{user?.fullname || user?.email}</strong>
                    </p>

                    {loadingRoles ? (
                        <div className="loading-spinner"><div className="spinner"></div></div>
                    ) : (
                        <div className="roles-list">
                            {availableRoles.map(role => (
                                <div
                                    key={role.id}
                                    className={`role-option ${selectedRoleIds.includes(role.id) ? 'selected' : ''}`}
                                    onClick={() => toggleRole(role.id)}
                                    style={{
                                        padding: '12px',
                                        margin: '8px 0',
                                        borderRadius: '8px',
                                        background: selectedRoleIds.includes(role.id) ? 'rgba(76, 175, 80, 0.1)' : 'var(--bg-secondary)',
                                        border: `1px solid ${selectedRoleIds.includes(role.id) ? 'var(--success)' : 'transparent'}`,
                                        cursor: 'pointer',
                                        display: 'flex',
                                        justifyContent: 'space-between',
                                        alignItems: 'center',
                                        transition: 'all 0.2s'
                                    }}
                                >
                                    <div>
                                        <h4 style={{ margin: 0 }}>{role.role_name}</h4>
                                        <small style={{ color: 'var(--text-secondary)' }}>{role.description}</small>
                                    </div>
                                    {selectedRoleIds.includes(role.id) && <FiCheck color="var(--success)" />}
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                <div className="modal-footer" style={{ marginTop: '20px', justifyContent: 'flex-end', display: 'flex', gap: '10px' }}>
                    <button className="btn-secondary" onClick={onClose}>Отмена</button>
                    <button
                        className="btn-primary"
                        onClick={handleSubmit}
                        disabled={loading || loadingRoles}
                    >
                        {loading ? 'Сохранение...' : 'Сохранить изменения'}
                    </button>
                </div>
            </motion.div>
        </div>
    );
};

export default RoleChangeModal;
