"""
SafeNest v2.0 — Webhook Management System
Banks can register webhook endpoints to receive real-time transaction analysis callbacks
"""

import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
from contextlib import contextmanager

WEBHOOKS_TABLE = """
CREATE TABLE IF NOT EXISTS bank_webhooks (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    bank_name           TEXT NOT NULL,
    api_key             TEXT NOT NULL UNIQUE,
    webhook_url         TEXT NOT NULL,
    webhook_secret      TEXT NOT NULL,
    is_active           BOOLEAN DEFAULT 1,
    created_at          TEXT NOT NULL,
    last_triggered      TEXT,
    success_count       INTEGER DEFAULT 0,
    failure_count       INTEGER DEFAULT 0,
    events              TEXT DEFAULT 'transaction_analyzed'  -- comma-separated
);

CREATE TABLE IF NOT EXISTS webhook_logs (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    webhook_id          INTEGER NOT NULL,
    transaction_id      TEXT NOT NULL,
    event_type          TEXT NOT NULL,
    payload             TEXT NOT NULL,
    http_status         INTEGER,
    response_time_ms    INTEGER,
    triggered_at        TEXT NOT NULL,
    FOREIGN KEY (webhook_id) REFERENCES bank_webhooks(id)
);
"""

class WebhookManager:
    def __init__(self, db_path: str = "safenest.db"):
        self.db_path = db_path
        self._init_tables()

    @contextmanager
    def _get_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_tables(self):
        """Initialize webhook tables"""
        with self._get_db() as conn:
            cursor = conn.cursor()
            for statement in WEBHOOKS_TABLE.split(';'):
                if statement.strip():
                    try:
                        cursor.execute(statement)
                    except sqlite3.OperationalError:
                        pass  # Table already exists
            conn.commit()

    def register_webhook(self, bank_name: str, api_key: str, webhook_url: str, webhook_secret: str) -> Dict:
        """Register a new webhook endpoint for a bank"""
        with self._get_db() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO bank_webhooks (bank_name, api_key, webhook_url, webhook_secret, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (bank_name, api_key, webhook_url, webhook_secret, datetime.utcnow().isoformat()))
                conn.commit()
                return {
                    "status": "success",
                    "message": f"Webhook registered for {bank_name}",
                    "webhook_id": cursor.lastrowid
                }
            except sqlite3.IntegrityError:
                return {"status": "error", "message": "API key already registered"}

    def get_webhooks_for_api_key(self, api_key: str) -> List[Dict]:
        """Get all webhooks for a given API key"""
        with self._get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, bank_name, webhook_url, webhook_secret, is_active, success_count, failure_count
                FROM bank_webhooks
                WHERE api_key = ? AND is_active = 1
            """, (api_key,))
            return [dict(row) for row in cursor.fetchall()]

    def log_webhook_event(self, webhook_id: int, transaction_id: str, event_type: str, 
                          payload: str, http_status: Optional[int], response_time_ms: int):
        """Log webhook trigger event"""
        with self._get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO webhook_logs (webhook_id, transaction_id, event_type, payload, http_status, response_time_ms, triggered_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (webhook_id, transaction_id, event_type, payload, http_status, response_time_ms, datetime.utcnow().isoformat()))
            
            # Update webhook stats
            if http_status and 200 <= http_status < 300:
                cursor.execute("UPDATE bank_webhooks SET success_count = success_count + 1, last_triggered = ? WHERE id = ?",
                             (datetime.utcnow().isoformat(), webhook_id))
            else:
                cursor.execute("UPDATE bank_webhooks SET failure_count = failure_count + 1, last_triggered = ? WHERE id = ?",
                             (datetime.utcnow().isoformat(), webhook_id))
            conn.commit()

    def get_webhook_stats(self, api_key: str) -> Dict:
        """Get webhook statistics for a bank"""
        with self._get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    SUM(success_count) as total_success,
                    SUM(failure_count) as total_failure,
                    COUNT(*) as total_webhooks
                FROM bank_webhooks
                WHERE api_key = ?
            """, (api_key,))
            row = cursor.fetchone()
            return {
                "total_webhooks": row['total_webhooks'] or 0,
                "total_success": row['total_success'] or 0,
                "total_failure": row['total_failure'] or 0,
                "success_rate": (row['total_success'] / (row['total_success'] + row['total_failure']) * 100) 
                               if (row['total_success'] + row['total_failure']) > 0 else 0
            }

    def list_all_webhooks(self) -> List[Dict]:
        """List all registered webhooks (admin only)"""
        with self._get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, bank_name, webhook_url, is_active, created_at, last_triggered, success_count, failure_count
                FROM bank_webhooks
            """)
            return [dict(row) for row in cursor.fetchall()]

    def deactivate_webhook(self, webhook_id: int) -> Dict:
        """Deactivate a webhook"""
        with self._get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE bank_webhooks SET is_active = 0 WHERE id = ?", (webhook_id,))
            conn.commit()
            if cursor.rowcount > 0:
                return {"status": "success", "message": "Webhook deactivated"}
            return {"status": "error", "message": "Webhook not found"}
