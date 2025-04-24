import threading
import time

class TokenRefresher:
    def __init__(self, refresh_fn, interval_sec=250):
        self.refresh_fn = refresh_fn
        self.interval_sec = interval_sec
        self.token = None
        self.token_time = 0
        self._lock = threading.Lock()
        self._start_refresher()

    def _start_refresher(self):
        threading.Thread(target=self._auto_refresh, daemon=True).start()

    def _auto_refresh(self):
        while True:
            try:
                token = self.refresh_fn()
                with self._lock:
                    self.token = token
                    self.token_time = time.time()
            except Exception:
                pass
            time.sleep(self.interval_sec)

    def get_token(self):
        with self._lock:
            return self.token

    def get_token_age(self):
        with self._lock:
            return time.time() - self.token_time if self.token_time else None
