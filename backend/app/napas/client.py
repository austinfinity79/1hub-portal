from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date


@dataclass
class SettlementRecord:
    full_order_id: str
    merchant_id: str
    amount: int
    settled_at: str
    status: str  # ACSC | RJCT


@dataclass
class TxnStatusDTO:
    full_order_id: str
    status: str
    amount: int
    merchant_id: str
    timestamp: str


class NapasClient(ABC):
    @abstractmethod
    def verify_notice_signature(self, payload: bytes, signature: str) -> bool: ...

    @abstractmethod
    def get_settlement_report(self, report_date: date) -> list[SettlementRecord]: ...

    @abstractmethod
    def get_transaction_status(self, full_order_id: str) -> TxnStatusDTO: ...
