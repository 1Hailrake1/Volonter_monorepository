import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { FiMail, FiLock, FiUser, FiMapPin, FiCalendar, FiArrowRight, FiCheck } from 'react-icons/fi';
import { authAPI } from '../api/api';
import './AuthPage.css';

const AuthPage = ({ onLogin }) => {
    const navigate = useNavigate();
    const [mode, setMode] = React.useState('choice'); // choice, register, login
    const [step, setStep] = React.useState('form'); // form, code
    const [loading, setLoading] = React.useState(false);
    const [error, setError] = React.useState('');
    const [countdown, setCountdown] = React.useState(300); // 5 минут

    // Form data
    const [formData, setFormData] = React.useState({
        email: '',
        password: '',
        fullname: '',
        location: '',
        date_birth: '',
    });
    const [code, setCode] = React.useState('');

    // Countdown timer
    React.useEffect(() => {
        if (step === 'code' && countdown > 0) {
            const timer = setTimeout(() => setCountdown(countdown - 1), 1000);
            return () => clearTimeout(timer);
        }
        if (countdown === 0) {
            setError('Время истекло. Начните заново.');
            setTimeout(() => {
                setStep('form');
                setCountdown(300);
            }, 2000);
        }
    }, [step, countdown]);

    const handleSendCode = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        try {
            await authAPI.sendCode(formData.email);
            setStep('code');
            setCountdown(300);
        } catch (err) {
            setError(err.response?.data?.detail || 'Ошибка отправки кода');
        } finally {
            setLoading(false);
        }
    };

    const handleVerifyAndRegister = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        try {
            // Verify code
            await authAPI.verifyCode(formData.email, code);

            // Register
            await authAPI.register({
                email: formData.email,
                hashed_password: formData.password,
                fullname: formData.fullname,
                location: formData.location || null,
                date_birth: formData.date_birth || null,
            });

            // Login
            await authAPI.login(formData.email, formData.password);
            onLogin();
            navigate('/dashboard');
        } catch (err) {
            setError(err.response?.data?.detail || 'Ошибка регистрации');
        } finally {
            setLoading(false);
        }
    };

    const handleVerifyAndLogin = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        try {
            // Verify code
            await authAPI.verifyCode(formData.email, code);

            // Login
            await authAPI.login(formData.email, formData.password);
            onLogin();
            navigate('/dashboard');
        } catch (err) {
            setError(err.response?.data?.detail || 'Ошибка входа');
        } finally {
            setLoading(false);
        }
    };

    const formatTime = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    return (
        <div className="auth-page">
            {/* Animated Background */}
            <div className="auth-background">
                <div className="gradient-orb orb-1"></div>
                <div className="gradient-orb orb-2"></div>
                <div className="gradient-orb orb-3"></div>
                <div className="grid-overlay"></div>
            </div>

            <div className="auth-container">
                <AnimatePresence mode="wait">
                    {mode === 'choice' && (
                        <motion.div
                            key="choice"
                            className="auth-choice"
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.9 }}
                            transition={{ duration: 0.3 }}
                        >
                            <motion.div
                                className="auth-logo"
                                initial={{ y: -20, opacity: 0 }}
                                animate={{ y: 0, opacity: 1 }}
                                transition={{ delay: 0.1 }}
                            >
                                <div className="logo-icon">🤝</div>
                                <h1 className="gradient-text">Волонтёрская Платформа</h1>
                                <p>Профессиональная платформа для организации волонтёрской деятельности</p>
                            </motion.div>

                            <div className="choice-buttons">
                                <motion.button
                                    className="btn btn-primary btn-large"
                                    onClick={() => setMode('register')}
                                    whileHover={{ scale: 1.02 }}
                                    whileTap={{ scale: 0.98 }}
                                    initial={{ x: -20, opacity: 0 }}
                                    animate={{ x: 0, opacity: 1 }}
                                    transition={{ delay: 0.2 }}
                                >
                                    Регистрация <FiArrowRight />
                                </motion.button>

                                <motion.button
                                    className="btn btn-secondary btn-large"
                                    onClick={() => setMode('login')}
                                    whileHover={{ scale: 1.02 }}
                                    whileTap={{ scale: 0.98 }}
                                    initial={{ x: 20, opacity: 0 }}
                                    animate={{ x: 0, opacity: 1 }}
                                    transition={{ delay: 0.3 }}
                                >
                                    Вход <FiArrowRight />
                                </motion.button>
                            </div>

                            <motion.button
                                className="btn-link"
                                onClick={() => navigate('/')}
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                transition={{ delay: 0.4 }}
                            >
                                Вернуться на главную
                            </motion.button>
                        </motion.div>
                    )}

                    {mode === 'register' && step === 'form' && (
                        <RegisterForm
                            formData={formData}
                            setFormData={setFormData}
                            onSubmit={handleSendCode}
                            loading={loading}
                            error={error}
                            onBack={() => setMode('choice')}
                        />
                    )}

                    {mode === 'login' && step === 'form' && (
                        <LoginForm
                            formData={formData}
                            setFormData={setFormData}
                            onSubmit={handleSendCode}
                            loading={loading}
                            error={error}
                            onBack={() => setMode('choice')}
                        />
                    )}

                    {step === 'code' && (
                        <CodeVerification
                            code={code}
                            setCode={setCode}
                            onSubmit={mode === 'register' ? handleVerifyAndRegister : handleVerifyAndLogin}
                            loading={loading}
                            error={error}
                            countdown={countdown}
                            formatTime={formatTime}
                            onBack={() => {
                                setStep('form');
                                setCountdown(300);
                            }}
                        />
                    )}
                </AnimatePresence>
            </div>
        </div>
    );
};

// Register Form Component
const RegisterForm = ({ formData, setFormData, onSubmit, loading, error, onBack }) => (
    <motion.div
        className="auth-form-container glass"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
    >
        <h2 className="form-title gradient-text">Регистрация</h2>
        <p className="form-subtitle">Создайте аккаунт для участия в мероприятиях</p>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={onSubmit} className="auth-form">
            <div className="form-group">
                <label><FiUser /> Полное имя *</label>
                <input
                    type="text"
                    value={formData.fullname}
                    onChange={(e) => setFormData({ ...formData, fullname: e.target.value })}
                    placeholder="Иван Иванов"
                    required
                />
            </div>

            <div className="form-group">
                <label><FiMail /> Email *</label>
                <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    placeholder="your@email.com"
                    required
                />
            </div>

            <div className="form-group">
                <label><FiLock /> Пароль *</label>
                <input
                    type="password"
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    placeholder="Минимум 8 символов"
                    minLength={8}
                    required
                />
            </div>

            <div className="form-row">
                <div className="form-group">
                    <label><FiMapPin /> Город</label>
                    <input
                        type="text"
                        value={formData.location}
                        onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                        placeholder="Москва"
                    />
                </div>

                <div className="form-group">
                    <label><FiCalendar /> Дата рождения</label>
                    <input
                        type="date"
                        value={formData.date_birth}
                        onChange={(e) => setFormData({ ...formData, date_birth: e.target.value })}
                    />
                </div>
            </div>

            <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
                {loading ? 'Отправка...' : 'Продолжить'} <FiArrowRight />
            </button>

            <button type="button" className="btn-link" onClick={onBack}>
                Назад
            </button>
        </form>
    </motion.div>
);

// Login Form Component
const LoginForm = ({ formData, setFormData, onSubmit, loading, error, onBack }) => (
    <motion.div
        className="auth-form-container glass"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
    >
        <h2 className="form-title gradient-text">Вход</h2>
        <p className="form-subtitle">Войдите в свой аккаунт</p>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={onSubmit} className="auth-form">
            <div className="form-group">
                <label><FiMail /> Email</label>
                <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    placeholder="your@email.com"
                    required
                />
            </div>

            <div className="form-group">
                <label><FiLock /> Пароль</label>
                <input
                    type="password"
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    placeholder="Введите пароль"
                    required
                />
            </div>

            <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
                {loading ? 'Отправка...' : 'Продолжить'} <FiArrowRight />
            </button>

            <button type="button" className="btn-link" onClick={onBack}>
                Назад
            </button>
        </form>
    </motion.div>
);

// Code Verification Component
const CodeVerification = ({ code, setCode, onSubmit, loading, error, countdown, formatTime, onBack }) => (
    <motion.div
        className="auth-form-container glass"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.9 }}
    >
        <div className="code-icon">
            <FiCheck />
        </div>
        <h2 className="form-title gradient-text">Проверьте почту</h2>
        <p className="form-subtitle">Мы отправили код подтверждения на вашу почту</p>

        <div className="countdown">
            <span>Код действителен:</span>
            <strong className={countdown < 60 ? 'countdown-warning' : ''}>{formatTime(countdown)}</strong>
        </div>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={onSubmit} className="auth-form">
            <div className="form-group">
                <label>Код подтверждения</label>
                <input
                    type="text"
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                    placeholder="Введите код"
                    className="code-input"
                    required
                    autoFocus
                />
            </div>

            <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
                {loading ? 'Проверка...' : 'Подтвердить'} <FiCheck />
            </button>

            <button type="button" className="btn-link" onClick={onBack}>
                Изменить данные
            </button>
        </form>
    </motion.div>
);

export default AuthPage;
