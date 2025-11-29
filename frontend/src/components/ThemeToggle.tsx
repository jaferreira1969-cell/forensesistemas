import { Moon, Sun, Sparkles } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';

export function ThemeToggle() {
    const { theme, toggleTheme } = useTheme();

    return (
        <button
            onClick={toggleTheme}
            className="p-2 rounded-lg bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
            aria-label="Toggle theme"
            title={`Tema atual: ${theme}. Clique para alterar.`}
        >
            {theme === 'light' && <Moon className="w-5 h-5 text-gray-700" />}
            {theme === 'dark' && <Sparkles className="w-5 h-5 text-yellow-400" />}
            {theme === 'midnight' && <Sun className="w-5 h-5 text-orange-400" />}
        </button>
    );
}
