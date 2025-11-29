import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '@/services/api';
import { jwtDecode } from "jwt-decode";

interface User {
    id: number;
    nome: string;
    email: string;
    role: 'admin' | 'user';
    status: 'pending' | 'active' | 'blocked';
    foto?: string;
}

interface AuthContextData {
    signed: boolean;
    user: User | null;
    loading: boolean;
    signIn: (token: string, user: User) => void;
    signOut: () => void;
}

const AuthContext = createContext<AuthContextData>({} as AuthContextData);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);

    function signIn(token: string, user: User) {
        localStorage.setItem('@App:user', JSON.stringify(user));
        localStorage.setItem('@App:token', token);

        api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        setUser(user);
    }

    function signOut() {
        localStorage.removeItem('@App:user');
        localStorage.removeItem('@App:token');
        api.defaults.headers.common['Authorization'] = '';
        setUser(null);
    }

    useEffect(() => {
        const storagedUser = localStorage.getItem('@App:user');
        const storagedToken = localStorage.getItem('@App:token');

        if (storagedToken && storagedUser) {
            // Verificar validade do token (opcional, mas recomendado)
            try {
                const decoded: any = jwtDecode(storagedToken);
                if (decoded.exp * 1000 < Date.now()) {
                    signOut();
                } else {
                    api.defaults.headers.common['Authorization'] = `Bearer ${storagedToken}`;
                    setUser(JSON.parse(storagedUser));
                }
            } catch (err) {
                signOut();
            }
        }
        setLoading(false);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    return (
        <AuthContext.Provider value={{ signed: !!user, user, loading, signIn, signOut }}>
            {children}
        </AuthContext.Provider>
    );
};

export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}
