import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';

// Pages
import PublicPage from './pages/PublicPage';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import EventsPage from './pages/EventsPage';
import EventDetailsPage from './pages/EventDetailsPage';
import MyApplicationsPage from './pages/MyApplicationsPage';
import OrganizerPage from './pages/OrganizerPage';
import AdminPage from './pages/AdminPage';

// Components
import Navbar from './components/Navbar';

import './App.css';

import { NotificationProvider } from './contexts/NotificationContext';
import { ConfirmationProvider } from './contexts/ConfirmationContext';

function App() {
    const [isAuthenticated, setIsAuthenticated] = React.useState(false);
    const [user, setUser] = React.useState(null);

    React.useEffect(() => {
        // Проверка авторизации при загрузке
        checkAuth();
    }, []);

    const checkAuth = async () => {
        try {
            const response = await fetch('http://localhost:8060/v1/auth/login/me', {
                method: 'POST',
                credentials: 'include',
            });
            if (response.ok) {
                const data = await response.json();
                setUser(data);
                setIsAuthenticated(true);
            }
        } catch (error) {
            setIsAuthenticated(false);
        }
    };

    const handleLogout = () => {
        setIsAuthenticated(false);
        setUser(null);
    };

    return (
        <NotificationProvider>
            <ConfirmationProvider>
                <Router>
                    <div className="App">
                        {isAuthenticated && <Navbar user={user} onLogout={handleLogout} />}

                        <AnimatePresence mode="wait">
                            <Routes>
                                {/* Публичная страница */}
                                <Route path="/" element={<PublicPage />} />

                                {/* Страница логина */}
                                <Route
                                    path="/login"
                                    element={
                                        isAuthenticated ?
                                            <Navigate to="/dashboard" /> :
                                            <LoginPage onLogin={() => checkAuth()} />
                                    }
                                />

                                {/* Защищённые маршруты */}
                                <Route
                                    path="/dashboard"
                                    element={
                                        isAuthenticated ?
                                            <DashboardPage user={user} /> :
                                            <Navigate to="/login" />
                                    }
                                />

                                <Route
                                    path="/events"
                                    element={
                                        isAuthenticated ?
                                            <EventsPage /> :
                                            <Navigate to="/login" />
                                    }
                                />

                                <Route
                                    path="/events/:id"
                                    element={
                                        isAuthenticated ?
                                            <EventDetailsPage /> :
                                            <Navigate to="/login" />
                                    }
                                />

                                <Route
                                    path="/my-applications"
                                    element={
                                        isAuthenticated ?
                                            <MyApplicationsPage /> :
                                            <Navigate to="/login" />
                                    }
                                />

                                <Route
                                    path="/admin"
                                    element={
                                        isAuthenticated && user?.roles?.some(r => r.role_name === 'admin') ?
                                            <AdminPage /> :
                                            <Navigate to="/dashboard" />
                                    }
                                />

                                <Route
                                    path="/organizer"
                                    element={
                                        isAuthenticated && user?.roles?.some(r => r.role_name === 'organizer' || r.role_name === 'admin') ?
                                            <OrganizerPage /> :
                                            <Navigate to="/dashboard" />
                                    }
                                />
                            </Routes>
                        </AnimatePresence>
                    </div>
                </Router>
            </ConfirmationProvider>
        </NotificationProvider>
    );
}

export default App;
