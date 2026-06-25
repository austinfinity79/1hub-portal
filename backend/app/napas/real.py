from datetime import date

from app.napas.client import NapasClient, SettlementRecord, TxnStatusDTO


class RealNapasClient(NapasClient):
    """TODO[NAPAS]: Implement khi co spec Napas that. Chi can thay MockNapasClient bang class nay."""

    def __init__(self, api_url: str, key_path: str):
        self.api_url = api_url
        self.key_path = key_path

    def verify_notice_signature(self, payload: bytes, signature: str) -> bool:
        raise NotImplementedError("Cho spec Napas")

    def get_settlement_report(self, report_date: date) -> list[SettlementRecord]:
        raise NotImplementedError("Cho spec Napas")

    def get_transaction_status(self, full_order_id: str) -> TxnStatusDTO:
        raise NotImplementedError("Cho spec Napas")
