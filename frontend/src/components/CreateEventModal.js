import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiX, FiCheck } from 'react-icons/fi';
import { publicAPI, eventsAPI } from '../api/api';

const CreateEventModal = ({ onClose, onSuccess, initialData = null }) => {
    const [loading, setLoading] = useState(false);
    const [tags, setTags] = useState([]);
    const [skills, setSkills] = useState([]);
    const [formData, setFormData] = useState({
        title: '',
        description: '',
        location: '',
        start_date: '',
        end_date: '',
        required_volunteers: 1,
        event_image_url: '',
        tag_ids: [],
        skill_ids: []
    });

    useEffect(() => {
        loadData();
    }, []);

    useEffect(() => {
        if (initialData) {
            // Helper to format date for datetime-local input (YYYY-MM-DDThh:mm)
            const formatDate = (dateString) => {
                if (!dateString) return '';
                const date = new Date(dateString);
                return new Date(date.getTime() - (date.getTimezoneOffset() * 60000))
                    .toISOString()
                    .slice(0, 16);
            };

            setFormData({
                title: initialData.title,
                description: initialData.description,
                location: initialData.location,
                start_date: formatDate(initialData.start_date),
                end_date: formatDate(initialData.end_date),
                required_volunteers: initialData.required_volunteers,
                event_image_url: initialData.event_image_url || '',
                tag_ids: initialData.tags?.map(t => t.id) || [],
                skill_ids: initialData.skills?.map(s => s.id) || []
            });
        }
    }, [initialData]);

    const loadData = async () => {
        try {
            const [tagsRes, skillsRes] = await Promise.all([
                publicAPI.getTags(),
                publicAPI.getSkills()
            ]);
            setTags(tagsRes.data);
            setSkills(skillsRes.data.skills || []);
        } catch (error) {
            console.error('Error loading data:', error);
        }
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const toggleSelection = (field, id) => {
        setFormData(prev => ({
            ...prev,
            [field]: prev[field].includes(id)
                ? prev[field].filter(item => item !== id)
                : [...prev[field], id]
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            // Validate dates
            // Validate dates
            if (new Date(formData.end_date) <= new Date(formData.start_date)) {
                alert('Дата окончания должна быть позже даты начала');
                setLoading(false);
                return;
            }

            const dataToSend = { ...formData };
            delete dataToSend.contact_info; // Defensive cleanup

            console.log('Submitting event data:', dataToSend);

            if (initialData) {
                await eventsAPI.update(initialData.id, dataToSend);
            } else {
                await eventsAPI.create(dataToSend);
            }
            onSuccess();
        } catch (error) {
            console.error('Error saving event:', error);
            alert('Ошибка при сохранении мероприятия');
        } finally {
            setLoading(false);
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
                style={{ maxWidth: '600px', maxHeight: '90vh', overflowY: 'auto' }}
            >
                <div className="modal-header">
                    <h3>{initialData ? 'Редактировать мероприятие' : 'Создать мероприятие'}</h3>
                    <button className="btn-close" onClick={onClose}><FiX /></button>
                </div>
                <form onSubmit={handleSubmit} className="modal-body">
                    <div className="form-group">
                        <label>Название</label>
                        <input
                            required
                            type="text"
                            name="title"
                            value={formData.title}
                            onChange={handleChange}
                            minLength={5}
                            className="profile-input"
                        />
                    </div>

                    <div className="form-group">
                        <label>Описание</label>
                        <textarea
                            required
                            name="description"
                            value={formData.description}
                            onChange={handleChange}
                            minLength={20}
                            className="profile-input"
                            rows={4}
                        />
                    </div>

                    <div className="form-group">
                        <label>Ссылка на изображение (URL)</label>
                        <input
                            type="text"
                            name="event_image_url"
                            value={formData.event_image_url}
                            onChange={handleChange}
                            placeholder="https://example.com/image.jpg"
                            className="profile-input"
                        />
                    </div>

                    <div className="form-group">
                        <label>Место проведения</label>
                        <input
                            required
                            type="text"
                            name="location"
                            value={formData.location}
                            onChange={handleChange}
                            className="profile-input"
                        />
                    </div>

                    <div className="form-row">
                        <div className="form-group">
                            <label>Начало</label>
                            <input
                                required
                                type="datetime-local"
                                name="start_date"
                                value={formData.start_date}
                                onChange={handleChange}
                                className="profile-input"
                            />
                        </div>
                        <div className="form-group">
                            <label>Окончание</label>
                            <input
                                required
                                type="datetime-local"
                                name="end_date"
                                value={formData.end_date}
                                onChange={handleChange}
                                className="profile-input"
                            />
                        </div>
                    </div>

                    <div className="form-group">
                        <label>Требуется волонтёров</label>
                        <input
                            required
                            type="number"
                            name="required_volunteers"
                            value={formData.required_volunteers}
                            onChange={handleChange}
                            min={1}
                            max={1000}
                            className="profile-input"
                        />
                    </div>

                    <div className="form-group">
                        <label>Теги</label>
                        <div className="tags-container">
                            {tags.map(tag => (
                                <span
                                    key={tag.id}
                                    className={`skill-tag ${formData.tag_ids.includes(tag.id) ? 'active' : ''}`}
                                    onClick={() => toggleSelection('tag_ids', tag.id)}
                                    style={{ cursor: 'pointer', background: formData.tag_ids.includes(tag.id) ? 'var(--accent)' : 'var(--bg-secondary)' }}
                                >
                                    {tag.name}
                                </span>
                            ))}
                        </div>
                    </div>

                    <div className="form-group">
                        <label>Требуемые навыки</label>
                        <div className="tags-container">
                            {skills.map(skill => (
                                <span
                                    key={skill.id}
                                    className={`skill-tag ${formData.skill_ids.includes(skill.id) ? 'active' : ''}`}
                                    onClick={() => toggleSelection('skill_ids', skill.id)}
                                    style={{ cursor: 'pointer', background: formData.skill_ids.includes(skill.id) ? 'var(--accent)' : 'var(--bg-secondary)' }}
                                >
                                    {skill.name}
                                </span>
                            ))}
                        </div>
                    </div>

                    <div className="modal-footer" style={{ marginTop: '20px' }}>
                        <button type="button" className="btn-secondary" onClick={onClose}>
                            Отмена
                        </button>
                        <button type="submit" className="btn-primary" disabled={loading}>
                            {loading ? 'Сохранение...' : (initialData ? 'Сохранить' : 'Создать')}
                        </button>
                    </div>
                </form>
            </motion.div>
        </div>
    );
};

export default CreateEventModal;
