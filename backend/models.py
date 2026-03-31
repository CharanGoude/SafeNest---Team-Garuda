from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class Transaction(BaseModel):
    transaction_id: Optional[str] = None
    timestamp: Optional[str] = None
    user_id: str
    account_number: str
    amount: float
    currency: str = "USD"
    transaction_type: str  # TRANSFER, PAYMENT, WITHDRAWAL, DEPOSIT
    merchant_name: Optional[str] = None
    merchant_category: Optional[str] = None
    location_country: str
    location_city: Optional[str] = None
    device_id: Optional[str] = None
    ip_address: Optional[str] = None
    is_new_device: Optional[bool] = False
    previous_transaction_minutes_ago: Optional[int] = None
    user_avg_transaction: Optional[float] = None
    account_age_days: Optional[int] = None


class FraudReport(BaseModel):
    transaction_id: str
    fraud_risk_score: int
    risk_level: str
    fraud_indicators: List[str]
    sentry_analysis: str


class ComplianceReport(BaseModel):
    transaction_id: str
    kyc_status: str
    aml_status: str
    watchlist_status: str
    compliance_status: str
    compliance_notes: str


class AgentLog(BaseModel):
    agent: str
    action: str
    timestamp: str
    details: Dict[str, Any]
