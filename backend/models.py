"""SafeNest v2.0 — Production Data Models"""

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class RiskLevel(str, Enum):
    LOW      = "LOW"
    MEDIUM   = "MEDIUM"
    HIGH     = "HIGH"
    CRITICAL = "CRITICAL"

class ActionTaken(str, Enum):
    APPROVE           = "APPROVE"
    FLAG_FOR_REVIEW   = "FLAG_FOR_REVIEW"
    REQUIRE_OTP       = "REQUIRE_OTP"
    REQUIRE_BIOMETRIC = "REQUIRE_BIOMETRIC"
    FREEZE_ACCOUNT    = "FREEZE_ACCOUNT"
    BLOCK             = "BLOCK"

class ComplianceStatus(str, Enum):
    COMPLIANT     = "COMPLIANT"
    FLAGGED       = "FLAGGED"
    NON_COMPLIANT = "NON_COMPLIANT"

class TransactionType(str, Enum):
    PAYMENT    = "PAYMENT"
    TRANSFER   = "TRANSFER"
    WITHDRAWAL = "WITHDRAWAL"
    DEPOSIT    = "DEPOSIT"


class TransactionRequest(BaseModel):
    transaction_id:    Optional[str]   = None
    account_number:    str
    user_id:           str
    amount:            float           = Field(..., gt=0)
    currency:          str             = "INR"
    transaction_type:  TransactionType = TransactionType.PAYMENT
    merchant_name:     str
    merchant_category: str             = "RETAIL"
    location_country:  str
    location_city:     Optional[str]   = None
    device_id:         str
    ip_address:        str
    is_new_device:     bool            = False
    account_age_days:              int
    user_avg_transaction:          float
    previous_transaction_minutes_ago: Optional[int] = None

    class Config:
        json_schema_extra = {"example": {
            "account_number": "ACC123456789", "user_id": "user_rahul_k",
            "amount": 5000.0, "currency": "INR", "transaction_type": "PAYMENT",
            "merchant_name": "Amazon India", "merchant_category": "RETAIL",
            "location_country": "IN", "location_city": "Mumbai",
            "device_id": "iPhone_14_ABC", "ip_address": "192.168.1.1",
            "is_new_device": False, "account_age_days": 730,
            "user_avg_transaction": 800.0, "previous_transaction_minutes_ago": 120
        }}


class SentryResult(BaseModel):
    risk_score:          int       = Field(..., ge=0, le=100)
    fraud_indicators:    List[str] = []
    behavioural_summary: str       = ""
    processing_ms:       int       = 0

class CoordinatorResult(BaseModel):
    risk_score:             int       = Field(..., ge=0, le=100)
    comparison_indicators:  List[str] = []
    parameter_changes:      List[str] = []
    is_baseline:            bool      = False
    processing_ms:          int       = 0

class AuditorResult(BaseModel):
    compliance_status: ComplianceStatus
    kyc_status:        str
    aml_status:        str
    watchlist_status:  str
    ctr_required:      bool       = False
    sar_required:      bool       = False
    regulatory_flags:  List[str]  = []
    processing_ms:     int        = 0

class ResponseResult(BaseModel):
    action:            ActionTaken
    risk_level:        RiskLevel
    final_risk_score:  int        = Field(..., ge=0, le=100)
    reasoning:         str        = ""
    alert_message:     str        = ""
    secondary_actions: List[str]  = []
    processing_ms:     int        = 0

class AnalysisResponse(BaseModel):
    transaction_id:     str
    timestamp:          str
    processing_time_ms: int
    action:             ActionTaken
    risk_level:         RiskLevel
    final_risk_score:   int
    compliance_status:  ComplianceStatus
    ctr_required:       bool
    sar_required:       bool
    coordinator:        CoordinatorResult
    response:           ResponseResult
    blockchain_hash:    str
