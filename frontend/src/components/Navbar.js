import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FiHome, FiCalendar, FiFileText, FiSettings, FiLogOut, FiShield, FiUser, FiGrid, FiBriefcase } from 'react-icons/fi';
import { authAPI } from '../api/api';
import './Navbar.css';

const Navbar = ({ user, onLogout }) => {
    const navigate = useNavigate();
    const location = useLocation();
    const [isScrolled, setIsScrolled] = React.useState(false);

    React.useEffect(() => {
        const handleScroll = () => {
            setIsScrolled(window.scrollY > 20);
        };
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const handleLogout = async () => {
        try {
            await authAPI.logout();
            onLogout();
            navigate('/login');
        } catch (error) {
            console.error('Logout error:', error);
        }
    };

    const isAdmin = user?.roles?.some(r => r.role_name === 'admin');
    const isOrganizer = user?.roles?.some(r => r.role_name === 'organizer' || r.role_name === 'admin');

    return (
        <motion.nav
            className={`navbar ${isScrolled ? 'scrolled' : ''}`}
            initial={{ y: -100 }}
            animate={{ y: 0 }}
            transition={{ duration: 0.5 }}
        >
            <div className="navbar-container">
                <Link to="/dashboard" className="navbar-logo">
                    <motion.div
                        className="logo-wrapper"
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                    >
                        <FiGrid className="logo-icon" />
                        <span className="logo-text gradient-text">VolonterPlatform</span>
                    </motion.div>
                </Link>

                <div className="navbar-links">
                    <NavLink to="/dashboard" icon={<FiHome />} text="Главная" active={location.pathname === '/dashboard'} />
                    <NavLink to="/events" icon={<FiCalendar />} text="Мероприятия" active={location.pathname === '/events'} />
                    <NavLink to="/my-applications" icon={<FiFileText />} text="Заявки" active={location.pathname === '/my-applications'} />
                    {isOrganizer && <NavLink to="/organizer" icon={<FiBriefcase />} text="Организация" active={location.pathname === '/organizer'} />}
                    {isAdmin && <NavLink to="/admin" icon={<FiShield />} text="Админ" active={location.pathname.startsWith('/admin')} />}
                </div>

                <div className="navbar-user">
                    <div className="user-info">
                        <div className="user-avatar">
                            {user?.fullname?.charAt(0) || <FiUser />}
                        </div>
                        <div className="user-details">
                            <span className="user-name">{user?.fullname || 'Пользователь'}</span>
                            <span className="user-email">{user?.email}</span>
                        </div>
                    </div>

                    <motion.button
                        className="btn-logout"
                        onClick={handleLogout}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        title="Выйти"
                    >
                        <FiLogOut />
                    </motion.button>
                </div>
            </div>
        </motion.nav>
    );
};

const NavLink = ({ to, icon, text, active }) => {
    return (
        <Link to={to} className={`nav-link ${active ? 'active' : ''}`}>
            <motion.div
                className="nav-link-content"
                whileHover={{ y: -2 }}
                whileTap={{ scale: 0.95 }}
            >
                <span className="nav-icon">{icon}</span>
                <span className="nav-text">{text}</span>
            </motion.div>
        </Link>
    );
};

export default Navbar;
