import { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';

interface HeaderPortalProps {
    children: React.ReactNode;
}

export const HeaderPortal = ({ children }: HeaderPortalProps) => {
    const [mounted, setMounted] = useState(false);
    const [container, setContainer] = useState<HTMLElement | null>(null);

    useEffect(() => {
        setMounted(true);
        const el = document.getElementById('header-portal-root');
        if (el) {
            setContainer(el);
        }
        return () => setMounted(false);
    }, []);

    if (!mounted || !container) return null;

    return createPortal(children, container);
};
