import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FiCalendar, FiMapPin, FiUsers, FiArrowRight, FiHeart, FiShield, FiTarget, FiAward } from 'react-icons/fi';
import { publicAPI } from '../api/api';
import { format } from 'date-fns';
import { ru } from 'date-fns/locale';
import './PublicPage.css';

const PublicPage = () => {
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(true);

    React.useEffect(() => {
        loadEvents();
    }, []);

    const loadEvents = async () => {
        try {
            const response = await publicAPI.getEvents({ page: 1, page_size: 6 });
            setEvents(response.data.events);
        } catch (error) {
            console.error('Error loading events:', error);
        } finally {
            setLoading(false);
        }
    };

    const scrollToSection = (id) => {
        document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
    };

    return (
        <div className="public-page">
            {/* Navigation Header */}
            <nav className="public-nav">
                <div className="container nav-container">
                    <div className="nav-logo">🤝 Волонтёры</div>
                    <div className="nav-links">
                        <button onClick={() => scrollToSection('stats')}>Статистика</button>
                        <button onClick={() => scrollToSection('about')}>О платформе</button>
                        <button onClick={() => scrollToSection('events')}>Актуальные события</button>
                        <button onClick={() => scrollToSection('rules')}>Правила сообщества</button>
                        <button onClick={() => scrollToSection('contacts')}>Контакты</button>
                    </div>
                    <Link to="/login" className="nav-cta">Войти</Link>
                </div>
            </nav>

            {/* Hero Section */}
            <section className="hero-section">
                <div className="hero-background">
                    <div className="hero-orb orb-1"></div>
                    <div className="hero-orb orb-2"></div>
                    <div className="hero-grid"></div>
                </div>

                <motion.div
                    className="hero-content container"
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8 }}
                >
                    <motion.div className="hero-badge" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
                        <span className="badge-dot"></span>
                        Платформа нового поколения
                    </motion.div>

                    <motion.h1 className="hero-title" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2, duration: 0.8 }}>
                        Технологии <br />
                        <span className="gradient-text">добрых дел</span>
                    </motion.h1>

                    <motion.p className="hero-subtitle" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4, duration: 0.8 }}>
                        Объединяем людей, ресурсы и технологии для решения социальных задач.
                        Эффективная организация волонтёрской деятельности в цифровой среде.
                    </motion.p>

                    <motion.div className="hero-buttons" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6, duration: 0.8 }}>
                        <Link to="/login" className="btn btn-primary btn-large glow shake-pulse">
                            Присоединиться <FiArrowRight />
                        </Link>
                        <button onClick={() => scrollToSection('events')} className="btn btn-secondary btn-large">
                            Мероприятия
                        </button>
                    </motion.div>
                </motion.div>
            </section>

            {/* Stats Section */}
            <section id="stats" className="stats-section">
                <div className="container">
                    <h2 className="stats-title">Наша статистика</h2>
                    <div className="stats-grid">
                        <StatCard icon={<FiUsers />} value="10k+" label="Активных волонтёров" delay={0.1} />
                        <StatCard icon={<FiCalendar />} value="500+" label="Успешных мероприятий" delay={0.2} />
                        <StatCard icon={<FiTarget />} value="50+" label="Городов присутствия" delay={0.3} />
                        <StatCard icon={<FiAward />} value="100+" label="Партнёров платформы" delay={0.4} />
                    </div>
                </div>
            </section>

            {/* About Section */}

            {/* About Section */}
            <section id="about" className="about-section">
                <div className="container">
                    <div className="about-grid">
                        <motion.div
                            className="about-content"
                            initial={{ opacity: 0, x: -30 }}
                            whileInView={{ opacity: 1, x: 0 }}
                            viewport={{ once: true }}
                        >
                            <h2 className="section-title">О платформе</h2>
                            <p className="section-text">
                                Мы создаем цифровую экосистему для развития волонтерства. Наша миссия — сделать помощь доступной, прозрачной и эффективной.
                            </p>
                            <ul className="about-features">
                                <li>
                                    <FiShield className="feature-icon" />
                                    <div>
                                        <h3>Надёжность</h3>
                                        <p>Верифицированные организаторы и волонтёры</p>
                                    </div>
                                </li>
                                <li>
                                    <FiTarget className="feature-icon" />
                                    <div>
                                        <h3>Эффективность</h3>
                                        <p>Умный подбор мероприятий по навыкам</p>
                                    </div>
                                </li>
                                <li>
                                    <FiHeart className="feature-icon" />
                                    <div>
                                        <h3>Сообщество</h3>
                                        <p>Поддержка и развитие культуры взаимопомощи</p>
                                    </div>
                                </li>
                            </ul>
                        </motion.div>

                        <motion.div
                            className="about-image-container"
                            initial={{ opacity: 0, x: 30 }}
                            whileInView={{ opacity: 1, x: 0 }}
                            viewport={{ once: true }}
                        >
                            <div className="about-image glass glow">
                                {/* SVG иллюстрация встроена напрямую */}
                                <svg viewBox="0 0 600 400" xmlns="http://www.w3.org/2000/svg" style={{ width: '100%', height: '100%', borderRadius: 'var(--radius-2xl)' }}>
                                    <defs>
                                        <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                            <stop offset="0%" style={{ stopColor: '#f5d5c8', stopOpacity: 1 }} />
                                            <stop offset="50%" style={{ stopColor: '#e6c9a8', stopOpacity: 1 }} />
                                            <stop offset="100%" style={{ stopColor: '#d4a574', stopOpacity: 1 }} />
                                        </linearGradient>
                                        <linearGradient id="accentGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                            <stop offset="0%" style={{ stopColor: '#d4a574', stopOpacity: 1 }} />
                                            <stop offset="100%" style={{ stopColor: '#c89860', stopOpacity: 1 }} />
                                        </linearGradient>
                                        <filter id="glow">
                                            <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
                                            <feMerge>
                                                <feMergeNode in="coloredBlur"/>
                                                <feMergeNode in="SourceGraphic"/>
                                            </feMerge>
                                        </filter>
                                    </defs>

                                    <rect width="600" height="400" fill="url(#bgGradient)" rx="20"/>

                                    <circle cx="100" cy="80" r="60" fill="#d4a574" opacity="0.1"/>
                                    <circle cx="500" cy="320" r="80" fill="#e8b4a0" opacity="0.15"/>
                                    <circle cx="480" cy="100" r="40" fill="#d4a574" opacity="0.1"/>

                                    <g transform="translate(300, 200)">
                                        <circle cx="0" cy="0" r="50" fill="#ffffff" opacity="0.9"/>
                                        <path d="M -20,-10 Q -20,-25 -10,-25 Q 0,-25 0,-15 Q 0,-25 10,-25 Q 20,-25 20,-10 Q 20,5 0,20 Q -20,5 -20,-10 Z"
                                              fill="url(#accentGradient)" filter="url(#glow)"/>

                                        <g transform="translate(-120, -40)">
                                            <circle cx="0" cy="-30" r="18" fill="#c89860"/>
                                            <path d="M -20,-5 Q -20,10 -15,25 L -10,25 L -10,15 Q -10,5 0,5 Q 10,5 10,15 L 10,25 L 15,25 Q 20,10 20,-5 Z"
                                                  fill="#d4a574"/>
                                            <path d="M -20,-8 L -35,-15 Q -38,-18 -35,-22 L -28,-20 Z" fill="#c89860"/>
                                        </g>

                                        <g transform="translate(120, -40)">
                                            <circle cx="0" cy="-30" r="18" fill="#e8b4a0"/>
                                            <path d="M -20,-5 Q -20,10 -15,25 L -10,25 L -10,15 Q -10,5 0,5 Q 10,5 10,15 L 10,25 L 15,25 Q 20,10 20,-5 Z"
                                                  fill="#e6c9a8"/>
                                            <path d="M 20,-8 L 35,-15 Q 38,-18 35,-22 L 28,-20 Z" fill="#e8b4a0"/>
                                        </g>

                                        <g transform="translate(0, 80)">
                                            <circle cx="0" cy="-30" r="18" fill="#d4a574"/>
                                            <path d="M -20,-5 Q -20,10 -15,25 L -10,25 L -10,15 Q -10,5 0,5 Q 10,5 10,15 L 10,25 L 15,25 Q 20,10 20,-5 Z"
                                                  fill="#c89860"/>
                                        </g>

                                        <line x1="0" y1="0" x2="-100" y2="-40" stroke="#d4a574" strokeWidth="3" opacity="0.6" strokeDasharray="5,5"/>
                                        <line x1="0" y1="0" x2="100" y2="-40" stroke="#d4a574" strokeWidth="3" opacity="0.6" strokeDasharray="5,5"/>
                                        <line x1="0" y1="0" x2="0" y2="50" stroke="#d4a574" strokeWidth="3" opacity="0.6" strokeDasharray="5,5"/>
                                    </g>

                                    <g transform="translate(480, 60)">
                                        <path d="M 0,-15 L 4,-4 L 15,-4 L 6,3 L 10,14 L 0,7 L -10,14 L -6,3 L -15,-4 L -4,-4 Z"
                                              fill="#d4a574" opacity="0.7"/>
                                    </g>

                                    <g transform="translate(100, 100)">
                                        <circle cx="0" cy="0" r="20" fill="#ffffff" opacity="0.5"/>
                                        <path d="M -8,-5 L -8,5 M -3,-8 L -3,8 M 3,-8 L 3,8 M 8,-5 L 8,5"
                                              stroke="#c89860" strokeWidth="2" strokeLinecap="round"/>
                                    </g>

                                    <g transform="translate(520, 350)">
                                        <path d="M 0,-8 Q -3,-12 -8,-12 Q -13,-12 -13,-6 Q -13,-2 0,8 Q 13,-2 13,-6 Q 13,-12 8,-12 Q 3,-12 0,-8 Z"
                                              fill="#e8b4a0" opacity="0.7"/>
                                    </g>

                                    <text x="300" y="370" fontFamily="Arial, sans-serif" fontSize="28" fontWeight="bold"
                                          fill="#2d2a26" textAnchor="middle" opacity="0.8">
                                        Digital Volunteering
                                    </text>

                                    <circle cx="150" cy="340" r="4" fill="#c89860" opacity="0.5"/>
                                    <circle cx="170" cy="350" r="3" fill="#d4a574" opacity="0.5"/>
                                    <circle cx="430" cy="340" r="4" fill="#e8b4a0" opacity="0.5"/>
                                    <circle cx="450" cy="350" r="3" fill="#c89860" opacity="0.5"/>
                                </svg>
                            </div>
                        </motion.div>
                    </div>
                </div>
            </section>

            {/* Events Section */}
            <section id="events" className="events-section">
                <div className="container">
                    <div className="section-header">
                        <motion.h2 className="section-title" initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}>
                            Актуальные <span className="gradient-text">события</span>
                        </motion.h2>
                        <p className="section-subtitle">Примите участие в значимых проектах</p>
                    </div>

                    {loading ? (
                        <div className="events-grid">
                            {[1, 2, 3].map(i => (
                                <div key={i} className="skeleton card" style={{ height: '400px' }} />
                            ))}
                        </div>
                    ) : (
                        <div className="events-grid">
                            {events.map((event, index) => (
                                <EventCard key={event.id} event={event} index={index} />
                            ))}
                        </div>
                    )}

                    <div className="section-footer">
                        <Link to="/login" className="btn btn-ghost pulse-btn">
                            Показать все мероприятия <FiArrowRight />
                        </Link>
                    </div>
                </div>
            </section>

            {/* Rules Section */}
            <section id="rules" className="rules-section">
                <div className="container">
                    <motion.div className="rules-card glass" initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}>
                        <h2 className="section-title center">Правила сообщества</h2>
                        <div className="rules-grid">
                            <div className="rule-item">
                                <span className="rule-number">01</span>
                                <h3>Взаимоуважение</h3>
                                <p>Мы ценим каждого участника и поддерживаем атмосферу доверия и уважения.</p>
                            </div>
                            <div className="rule-item">
                                <span className="rule-number">02</span>
                                <h3>Ответственность</h3>
                                <p>Серьезный подход к взятым обязательствам — основа нашей работы.</p>
                            </div>
                            <div className="rule-item">
                                <span className="rule-number">03</span>
                                <h3>Безопасность</h3>
                                <p>Мы строго следим за безопасностью данных и мероприятий.</p>
                            </div>
                        </div>
                    </motion.div>
                </div>
            </section>

            {/* Footer */}
            <footer id="contacts" className="public-footer">
                <div className="container">
                    <div className="footer-content">
                        <div className="footer-brand">
                            <span className="logo-icon">🤝</span>
                            <h3>Волонтёрская Платформа</h3>
                            <p>Технологии для добрых дел</p>
                        </div>
                        <div className="footer-links">
                            <div className="link-group">
                                <h4>Платформа</h4>
                                <button onClick={() => scrollToSection('about')}>О нас</button>
                                <button onClick={() => scrollToSection('events')}>Мероприятия</button>
                                <button onClick={() => scrollToSection('rules')}>Правила</button>
                            </div>
                            <div className="link-group">
                                <h4>Контакты</h4>
                                <a href="mailto:support@volunteer.ru">support@volunteer.ru</a>
                                <a href="tel:+79990000000">+7 (999) 000-00-00</a>
                            </div>
                        </div>
                    </div>
                    <div className="footer-bottom">
                        <p>© 2025 Volunteer Platform. All rights reserved.</p>
                    </div>
                </div>
            </footer>
        </div>
    );
};

const StatCard = ({ icon, value, label, delay }) => (
    <motion.div
        className="stat-card glass"
        initial={{ opacity: 0, scale: 0.9 }}
        whileInView={{ opacity: 1, scale: 1 }}
        viewport={{ once: true }}
        transition={{ delay, duration: 0.5 }}
        whileHover={{ rotateY: 10, scale: 1.05 }}
        style={{ transformStyle: 'preserve-3d' }}
    >
        <div className="stat-icon">{icon}</div>
        <div className="stat-value gradient-text">{value}</div>
        <div className="stat-label">{label}</div>
    </motion.div>
);

const EventCard = ({ event, index }) => {
    const startDate = new Date(event.start_date);
    const statusTranslations = {
        'approved': 'Одобрено',
        'pending': 'На проверке',
        'completed': 'Завершено',
        'canceled': 'Отменено'
    };

    return (
        <motion.div
            className="event-card card"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: index * 0.1 }}
        >
            <div className="event-image-wrapper">
                {event.event_image_url ? (
                    <img src={event.event_image_url} alt={event.title} className="event-image" />
                ) : (
                    <div className="event-placeholder">
                        <FiCalendar size={40} />
                    </div>
                )}
                <div className="event-status-badge">{statusTranslations[event.status] || event.status}</div>
            </div>

            <div className="event-content">
                <h3 className="event-title">{event.title}</h3>

                <div className="event-meta">
                    <div className="meta-item">
                        <FiCalendar />
                        <span>{format(startDate, 'd MMMM yyyy', { locale: ru })}</span>
                    </div>
                    <div className="meta-item">
                        <FiMapPin />
                        <span>{event.location}</span>
                    </div>
                </div>

                <div className="event-footer">
                    <div className="volunteers-needed">
                        <FiUsers />
                        <span>Нужно: {event.required_volunteers}</span>
                    </div>
                    <Link to={`/events/${event.id}`} className="btn-arrow">
                        <FiArrowRight />
                    </Link>
                </div>
            </div>
        </motion.div>
    );
};

export default PublicPage;
