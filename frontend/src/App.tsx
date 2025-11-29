import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from '@/contexts/ThemeContext';
import { ToastProvider } from '@/contexts/ToastContext';
import { AuthProvider, useAuth } from '@/contexts/AuthContext';
import Layout from '@/components/Layout';
import Dashboard from '@/pages/Dashboard';
import Upload from '@/pages/Upload';
import GraphView from '@/pages/GraphView';
import MapView from '@/pages/MapView';
import Messages from '@/pages/Messages';
import Settings from '@/pages/Settings';
import Login from '@/pages/Login';
import Register from '@/pages/Register';
import AdminUsers from '@/pages/AdminUsers';

// Componente para proteger rotas privadas
const ProtectedRoute = ({ children }: { children: JSX.Element }) => {
    const { signed, loading } = useAuth();

    if (loading) {
        return <div className="h-screen flex items-center justify-center">Carregando...</div>;
    }

    if (!signed) {
        return <Navigate to="/login" replace />;
    }

    return children;
};

// Componente para proteger rotas de admin
const AdminRoute = ({ children }: { children: JSX.Element }) => {
    const { user, loading } = useAuth();

    if (loading) {
        return <div>Carregando...</div>;
    }

    if (user?.role !== 'admin') {
        return <Navigate to="/" replace />;
    }

    return children;
};

function AppRoutes() {
    return (
        <Routes>
            {/* Rotas Públicas */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            {/* Rotas Privadas (com Layout) */}
            <Route path="/" element={
                <ProtectedRoute>
                    <Layout />
                </ProtectedRoute>
            }>
                <Route index element={<Dashboard />} />
                <Route path="upload" element={<Upload />} />
                <Route path="grafos" element={<GraphView />} />
                <Route path="mapa" element={<MapView />} />
                <Route path="mensagens" element={<Messages />} />
                <Route path="configuracoes" element={<Settings />} />

                {/* Rota de Admin */}
                <Route path="usuarios" element={
                    <AdminRoute>
                        <AdminUsers />
                    </AdminRoute>
                } />
            </Route>
        </Routes>
    );
}

function App() {
    return (
        <Router>
            <AuthProvider>
                <ThemeProvider>
                    <ToastProvider>
                        <AppRoutes />
                    </ToastProvider>
                </ThemeProvider>
            </AuthProvider>
        </Router>
    );
}

export default App;
