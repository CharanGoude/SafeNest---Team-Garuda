"""SafeNest v2.0 — SQLite Database Layer"""

import sqlite3, json, os
from datetime import datetime
from typing import List, Optional, Dict, Any
from contextlib import contextmanager

DB_PATH = os.getenv("DATABASE_URL", "safenest.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS transactions (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id      TEXT UNIQUE NOT NULL,
    timestamp           TEXT NOT NULL,
    account_number      TEXT NOT NULL,
    user_id             TEXT NOT NULL,
    amount              REAL NOT NULL,
    currency            TEXT DEFAULT 'INR',
    transaction_type    TEXT DEFAULT 'PAYMENT',
    merchant_name       TEXT NOT NULL,
    merchant_category   TEXT DEFAULT 'RETAIL',
    location_country    TEXT NOT NULL,
    location_city       TEXT,
    device_id           TEXT NOT NULL,
    ip_address          TEXT NOT NULL,
    is_new_device       INTEGER DEFAULT 0,
    action              TEXT NOT NULL,
    risk_level          TEXT NOT NULL,
    final_risk_score    INTEGER NOT NULL,
    compliance_status   TEXT NOT NULL,
    ctr_required        INTEGER DEFAULT 0,
    sar_required        INTEGER DEFAULT 0,
    blockchain_hash     TEXT NOT NULL,
    fraud_indicators    TEXT DEFAULT '[]',
    regulatory_flags    TEXT DEFAULT '[]',
    processing_time_ms  INTEGER DEFAULT 0,
    sentry_score        INTEGER DEFAULT 0,
    auditor_status      TEXT DEFAULT 'COMPLIANT',
    created_at          TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS blockchain_ledger (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    block_id        TEXT UNIQUE NOT NULL,
    transaction_id  TEXT NOT NULL,
    action          TEXT NOT NULL,
    risk_score      INTEGER NOT NULL,
    block_hash      TEXT NOT NULL,
    prev_hash       TEXT DEFAULT '0000000000000000',
    timestamp       TEXT NOT NULL,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS api_keys (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    bank_name   TEXT NOT NULL,
    api_key     TEXT UNIQUE NOT NULL,
    is_active   INTEGER DEFAULT 1,
    created_at  TEXT DEFAULT CURRENT_TIMESTAMP,
    last_used   TEXT
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id  TEXT NOT NULL,
    agent           TEXT NOT NULL,
    action          TEXT NOT NULL,
    result          TEXT NOT NULL,
    duration_ms     INTEGER DEFAULT 0,
    timestamp       TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS baseline_transactions (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id             TEXT NOT NULL,
    account_number      TEXT NOT NULL,
    amount              REAL NOT NULL,
    location_country    TEXT NOT NULL,
    location_city       TEXT,
    merchant_name       TEXT NOT NULL,
    merchant_category   TEXT DEFAULT 'RETAIL',
    device_id           TEXT NOT NULL,
    ip_address          TEXT NOT NULL,
    timestamp           REAL NOT NULL,
    created_at          TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, account_number)
);

CREATE INDEX IF NOT EXISTS idx_tx_account   ON transactions(account_number);
CREATE INDEX IF NOT EXISTS idx_tx_timestamp ON transactions(timestamp);
CREATE INDEX IF NOT EXISTS idx_tx_action    ON transactions(action);
CREATE INDEX IF NOT EXISTS idx_bc_txid      ON blockchain_ledger(transaction_id);
CREATE INDEX IF NOT EXISTS idx_baseline_user ON baseline_transactions(user_id, account_number);
"""

SEED = """
INSERT OR IGNORE INTO api_keys (bank_name, api_key, is_active)
VALUES
    ('Demo Bank',         'sk-safenest-demo-key-2026', 1),
    ('Test Integration',  'sk-safenest-test-key-2026', 1);
"""

class Database:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with self._conn() as conn:
            conn.executescript(SCHEMA)
            conn.executescript(SEED)
            conn.commit()

    @contextmanager
    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        try:
            yield conn
        finally:
            conn.close()

    def save_transaction(self, d: Dict[str, Any]) -> bool:
        sql = """INSERT OR REPLACE INTO transactions (
            transaction_id,timestamp,account_number,user_id,amount,currency,
            transaction_type,merchant_name,merchant_category,location_country,
            location_city,device_id,ip_address,is_new_device,action,risk_level,
            final_risk_score,compliance_status,ctr_required,sar_required,
            blockchain_hash,fraud_indicators,regulatory_flags,processing_time_ms,
            sentry_score,auditor_status
        ) VALUES (
            :transaction_id,:timestamp,:account_number,:user_id,:amount,:currency,
            :transaction_type,:merchant_name,:merchant_category,:location_country,
            :location_city,:device_id,:ip_address,:is_new_device,:action,:risk_level,
            :final_risk_score,:compliance_status,:ctr_required,:sar_required,
            :blockchain_hash,:fraud_indicators,:regulatory_flags,:processing_time_ms,
            :sentry_score,:auditor_status
        )"""
        try:
            with self._conn() as conn:
                conn.execute(sql, d); conn.commit()
            return True
        except Exception as e:
            print(f"[DB] save_transaction error: {e}"); return False

    def get_transactions(self, limit=50, offset=0, action=None, risk_level=None):
        conds, params = [], []
        if action:     conds.append("action=?");     params.append(action)
        if risk_level: conds.append("risk_level=?"); params.append(risk_level)
        where = f"WHERE {' AND '.join(conds)}" if conds else ""
        sql = f"SELECT * FROM transactions {where} ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        with self._conn() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]

    def get_transaction_by_id(self, tx_id: str):
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM transactions WHERE transaction_id=?", (tx_id,)).fetchone()
        return dict(row) if row else None

    def get_stats(self):
        with self._conn() as conn:
            total = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
            if total == 0:
                return {"total":0,"approved":0,"blocked":0,"frozen":0,"flagged":0,
                        "otp":0,"avg_risk":0.0,"fraud_rate":0.0,"critical_count":0,
                        "warning_count":0,"ctr_count":0,"sar_count":0}
            def q(sql): return conn.execute(sql).fetchone()[0]
            return {
                "total":         total,
                "approved":      q("SELECT COUNT(*) FROM transactions WHERE action='APPROVE'"),
                "blocked":       q("SELECT COUNT(*) FROM transactions WHERE action='BLOCK'"),
                "frozen":        q("SELECT COUNT(*) FROM transactions WHERE action='FREEZE_ACCOUNT'"),
                "flagged":       q("SELECT COUNT(*) FROM transactions WHERE action='FLAG_FOR_REVIEW'"),
                "otp":           q("SELECT COUNT(*) FROM transactions WHERE action IN ('REQUIRE_OTP','REQUIRE_BIOMETRIC')"),
                "avg_risk":      round(q("SELECT AVG(final_risk_score) FROM transactions") or 0, 1),
                "fraud_rate":    round((total - q("SELECT COUNT(*) FROM transactions WHERE action='APPROVE'")) / total * 100, 1),
                "critical_count":q("SELECT COUNT(*) FROM transactions WHERE risk_level='CRITICAL'"),
                "warning_count": q("SELECT COUNT(*) FROM transactions WHERE risk_level IN ('HIGH','MEDIUM')"),
                "ctr_count":     q("SELECT COUNT(*) FROM transactions WHERE ctr_required=1"),
                "sar_count":     q("SELECT COUNT(*) FROM transactions WHERE sar_required=1"),
            }

    def save_block(self, d: Dict[str, Any]) -> bool:
        sql = """INSERT OR IGNORE INTO blockchain_ledger
            (block_id,transaction_id,action,risk_score,block_hash,prev_hash,timestamp)
            VALUES (:block_id,:transaction_id,:action,:risk_score,:block_hash,:prev_hash,:timestamp)"""
        try:
            with self._conn() as conn:
                conn.execute(sql, d); conn.commit()
            return True
        except Exception as e:
            print(f"[DB] save_block error: {e}"); return False

    def get_blockchain(self, limit=100):
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM blockchain_ledger ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        return [dict(r) for r in rows]

    def get_last_block_hash(self):
        with self._conn() as conn:
            row = conn.execute(
                "SELECT block_hash FROM blockchain_ledger ORDER BY id DESC LIMIT 1"
            ).fetchone()
        return row[0] if row else "0"*64

    def validate_api_key(self, key: str):
        with self._conn() as conn:
            row = conn.execute(
                "SELECT bank_name FROM api_keys WHERE api_key=? AND is_active=1", (key,)
            ).fetchone()
            if row:
                conn.execute(
                    "UPDATE api_keys SET last_used=? WHERE api_key=?",
                    (datetime.utcnow().isoformat(), key)
                )
                conn.commit()
        return row[0] if row else None

    def save_audit_log(self, tx_id, agent, action, result, duration_ms):
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO audit_logs (transaction_id,agent,action,result,duration_ms,timestamp) VALUES (?,?,?,?,?,?)",
                (tx_id, agent, action, result, duration_ms, datetime.utcnow().isoformat())
            )
            conn.commit()

    def get_audit_logs(self, tx_id):
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM audit_logs WHERE transaction_id=? ORDER BY timestamp", (tx_id,)
            ).fetchall()
        return [dict(r) for r in rows]

    def save_baseline_transaction(self, data: Dict[str, Any]) -> bool:
        """Save or update baseline transaction for a user/account."""
        sql = """INSERT OR REPLACE INTO baseline_transactions
            (user_id, account_number, amount, location_country, location_city,
             merchant_name, merchant_category, device_id, ip_address, timestamp)
            VALUES (:user_id, :account_number, :amount, :location_country, :location_city,
                    :merchant_name, :merchant_category, :device_id, :ip_address, :timestamp)"""
        try:
            with self._conn() as conn:
                conn.execute(sql, data)
                conn.commit()
            return True
        except Exception as e:
            print(f"[DB] save_baseline_transaction error: {e}")
            return False

    def get_baseline_transaction(self, user_id: str, account_number: str) -> Optional[Dict]:
        """Retrieve baseline transaction for a user/account."""
        sql = "SELECT * FROM baseline_transactions WHERE user_id=? AND account_number=?"
        try:
            with self._conn() as conn:
                row = conn.execute(sql, (user_id, account_number)).fetchone()
            return dict(row) if row else None
        except Exception as e:
            print(f"[DB] get_baseline_transaction error: {e}")
            return None

db = Database()
