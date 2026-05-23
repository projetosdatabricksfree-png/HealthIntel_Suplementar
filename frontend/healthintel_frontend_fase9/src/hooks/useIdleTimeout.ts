import { useCallback, useEffect, useRef, useState } from 'react';

interface UseIdleTimeoutOptions {
  idleMs: number;
  warningMs: number;
  enabled: boolean;
  onIdle: () => void;
}

interface UseIdleTimeoutResult {
  isWarning: boolean;
  secondsLeft: number;
  resetActivity: () => void;
}

const ACTIVITY_STORAGE_KEY = 'healthintel.portal.last_activity';
const THROTTLE_MS = 2_000;
const ACTIVITY_EVENTS = ['mousemove', 'mousedown', 'keydown', 'touchstart', 'scroll'] as const;

export function useIdleTimeout({ idleMs, warningMs, enabled, onIdle }: UseIdleTimeoutOptions): UseIdleTimeoutResult {
  const [isWarning, setIsWarning] = useState(false);
  const [secondsLeft, setSecondsLeft] = useState(Math.ceil(warningMs / 1000));

  const warningTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const logoutTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const countdownIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const lastWriteRef = useRef<number>(0);
  const onIdleRef = useRef(onIdle);

  useEffect(() => {
    onIdleRef.current = onIdle;
  }, [onIdle]);

  const clearAllTimers = useCallback(() => {
    if (warningTimerRef.current) {
      clearTimeout(warningTimerRef.current);
      warningTimerRef.current = null;
    }
    if (logoutTimerRef.current) {
      clearTimeout(logoutTimerRef.current);
      logoutTimerRef.current = null;
    }
    if (countdownIntervalRef.current) {
      clearInterval(countdownIntervalRef.current);
      countdownIntervalRef.current = null;
    }
  }, []);

  const scheduleFromTimestamp = useCallback(
    (lastActivityAt: number) => {
      clearAllTimers();
      setIsWarning(false);
      setSecondsLeft(Math.ceil(warningMs / 1000));

      const now = Date.now();
      const elapsed = now - lastActivityAt;
      const warningDelay = Math.max(idleMs - warningMs - elapsed, 0);
      const logoutDelay = Math.max(idleMs - elapsed, 0);

      if (logoutDelay === 0) {
        onIdleRef.current();
        return;
      }

      warningTimerRef.current = setTimeout(() => {
        setIsWarning(true);
        const remainingMs = Math.max(idleMs - (Date.now() - lastActivityAt), 0);
        setSecondsLeft(Math.ceil(remainingMs / 1000));
        countdownIntervalRef.current = setInterval(() => {
          const left = Math.max(idleMs - (Date.now() - lastActivityAt), 0);
          setSecondsLeft(Math.ceil(left / 1000));
        }, 1_000);
      }, warningDelay);

      logoutTimerRef.current = setTimeout(() => {
        onIdleRef.current();
      }, logoutDelay);
    },
    [idleMs, warningMs, clearAllTimers],
  );

  const recordActivity = useCallback(
    (broadcast: boolean) => {
      const now = Date.now();
      if (broadcast && now - lastWriteRef.current >= THROTTLE_MS) {
        lastWriteRef.current = now;
        try {
          window.localStorage.setItem(ACTIVITY_STORAGE_KEY, String(now));
        } catch {
          // localStorage indisponível (modo privado, quota); seguir só com timer local
        }
      }
      scheduleFromTimestamp(now);
    },
    [scheduleFromTimestamp],
  );

  const resetActivity = useCallback(() => {
    lastWriteRef.current = 0;
    recordActivity(true);
  }, [recordActivity]);

  useEffect(() => {
    if (!enabled) {
      clearAllTimers();
      setIsWarning(false);
      return undefined;
    }

    let storedTs = 0;
    try {
      const raw = window.localStorage.getItem(ACTIVITY_STORAGE_KEY);
      storedTs = raw ? Number(raw) : 0;
    } catch {
      storedTs = 0;
    }

    const initialTs = storedTs && Number.isFinite(storedTs) && Date.now() - storedTs < idleMs ? storedTs : Date.now();
    if (initialTs === Date.now()) {
      try {
        window.localStorage.setItem(ACTIVITY_STORAGE_KEY, String(initialTs));
      } catch {
        // ignore
      }
    }
    scheduleFromTimestamp(initialTs);

    const onActivity = () => recordActivity(true);

    for (const ev of ACTIVITY_EVENTS) {
      window.addEventListener(ev, onActivity, { passive: true });
    }

    const onVisibility = () => {
      if (document.visibilityState === 'visible') {
        try {
          const raw = window.localStorage.getItem(ACTIVITY_STORAGE_KEY);
          const ts = raw ? Number(raw) : 0;
          if (ts && Number.isFinite(ts)) {
            scheduleFromTimestamp(ts);
            return;
          }
        } catch {
          // ignore
        }
        recordActivity(true);
      }
    };
    document.addEventListener('visibilitychange', onVisibility);

    const onStorage = (event: StorageEvent) => {
      if (event.key !== ACTIVITY_STORAGE_KEY || !event.newValue) return;
      const ts = Number(event.newValue);
      if (!Number.isFinite(ts)) return;
      scheduleFromTimestamp(ts);
    };
    window.addEventListener('storage', onStorage);

    return () => {
      clearAllTimers();
      for (const ev of ACTIVITY_EVENTS) {
        window.removeEventListener(ev, onActivity);
      }
      document.removeEventListener('visibilitychange', onVisibility);
      window.removeEventListener('storage', onStorage);
    };
  }, [enabled, idleMs, clearAllTimers, recordActivity, scheduleFromTimestamp]);

  return { isWarning, secondsLeft, resetActivity };
}
