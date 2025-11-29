import { Outlet } from 'react-router-dom';
import { useState } from 'react';
import { Menu, X, Home, Upload, Network, Map, MessageSquare, Settings, LogOut } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';
import { ThemeToggle } from './ThemeToggle';
import { useAuth } from '@/contexts/AuthContext';

export default function Layout() {
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const location = useLocation();
    const { user, signOut } = useAuth();

    const menuItemsTop = [
        { icon: Home, label: 'Dashboard', path: '/' },
        { icon: Network, label: 'Grafos', path: '/grafos' },
        { icon: Map, label: 'Mapa', path: '/mapa' },
        { icon: MessageSquare, label: 'Mensagens', path: '/mensagens' },
    ];

    const menuItemsBottom = [
        { icon: Upload, label: 'Importar', path: '/upload' },
        { icon: Settings, label: 'Configurações', path: '/configuracoes' },
    ];

    return (
        <div className="flex h-screen bg-background">
            {/* Sidebar */}
            <aside className={`${sidebarOpen ? 'w-64' : 'w-0'} transition-all duration-300 bg-card border-r border-border overflow-hidden flex flex-col`}>
                <div className="h-16 px-4 border-b border-border flex items-center justify-between">
                    <h1 className="text-xl font-bold text-primary">Sistema Forense</h1>
                    <div className="flex items-center gap-2">
                        <ThemeToggle />
                        <button onClick={() => setSidebarOpen(false)} className="p-1 hover:bg-accent rounded text-muted-foreground">
                            <X className="h-5 w-5" />
                        </button>
                    </div>
                </div>

                {/* User Info */}
                {user && (
                    <div className="p-4 border-b border-border flex items-center gap-3">
                        {user.foto ? (
                            <img src={user.foto} alt={user.nome} className="h-10 w-10 rounded-full object-cover" />
                        ) : (
                            <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                                <span className="text-primary font-semibold">{user.nome[0]}</span>
                            </div>
                        )}
                        <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium truncate">Olá, {user.nome.split(' ')[0]}</p>
                        </div>
                    </div>
                )}

                <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
                    {menuItemsTop.map((item) => {
                        const Icon = item.icon;
                        const isActive = location.pathname === item.path;
                        return (
                            <Link
                                key={item.path}
                                to={item.path}
                                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${isActive
                                    ? 'bg-primary text-primary-foreground'
                                    : 'hover:bg-accent text-foreground'
                                    }`}
                            >
                                <Icon className="h-5 w-5" />
                                <span>{item.label}</span>
                            </Link>
                        );
                    })}
                </nav>

                {/* Bottom Items */}
                <div className="p-4 border-t border-border space-y-2">
                    {menuItemsBottom.map((item) => {
                        const Icon = item.icon;
                        const isActive = location.pathname === item.path;
                        return (
                            <Link
                                key={item.path}
                                to={item.path}
                                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${isActive
                                    ? 'bg-primary text-primary-foreground'
                                    : 'hover:bg-accent text-foreground'
                                    }`}
                            >
                                <Icon className="h-5 w-5" />
                                <span>{item.label}</span>
                            </Link>
                        );
                    })}

                    <button
                        onClick={signOut}
                        className="flex items-center gap-3 px-4 py-3 rounded-lg w-full hover:bg-white/10 text-white transition-colors"
                    >
                        <LogOut className="h-5 w-5" />
                        <span>Sair</span>
                    </button>
                </div>
            </aside>

            {/* Main Content */}
            <div className="flex-1 flex flex-col overflow-hidden">
                {/* Header */}
                <header className="h-16 border-b border-border bg-card flex items-center px-6 gap-4">
                    {!sidebarOpen && (
                        <button
                            onClick={() => setSidebarOpen(true)}
                            className="p-2 hover:bg-accent rounded-lg transition-colors"
                        >
                            <Menu className="h-5 w-5" />
                        </button>
                    )}
                    <div id="header-portal-root" className="flex-1 flex items-center justify-between gap-4" />
                </header>

                {/* Page Content */}
                <main className="flex-1 overflow-auto">
                    <Outlet />
                </main>
            </div>
        </div>
    );
}
