import { useEffect, useRef } from 'react';
import { useAuth } from './useAuth';
import { toast } from 'sonner';

/**
 * Custom hook to log out the user automatically after a period of inactivity.
 * @param {number} timeoutMs - Timeout in milliseconds (default: 30 minutes)
 */
export function useIdleTimeout(timeoutMs = 30 * 60 * 1000) {
  const { logout, isAuthenticated } = useAuth();
  const timeoutRef = useRef(null);

  useEffect(() => {
    if (!isAuthenticated) return;

    const handleActivity = () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      timeoutRef.current = setTimeout(() => {
        toast.info('Sesión cerrada automáticamente por inactividad.');
        logout();
      }, timeoutMs);
    };

    // Attach activity event listeners
    const events = ['mousemove', 'keydown', 'scroll', 'click', 'touchstart'];
    events.forEach((event) => window.addEventListener(event, handleActivity));

    // Initialize timer
    handleActivity();

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      events.forEach((event) => window.removeEventListener(event, handleActivity));
    };
  }, [isAuthenticated, logout, timeoutMs]);
}
