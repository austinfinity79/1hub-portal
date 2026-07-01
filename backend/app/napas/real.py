"""NAPAS APG real client — sandbox/production.

Kết nối NAPAS APG qua HTTPS, sign payload bằng RSA private key (PEM).
Endpoints: {NAPAS_BASE_URL}/apg/{function}

# TODO[NAPAS-A2]: senderId / receiverId chưa có — cần điền header.
# TODO[NAPAS-A3]: OAuth2 getToken — chưa có client_id/secret/URL.
# TODO[NAPAS-B1]: Canonical JSON serialize rule + mẫu verify.
# TODO[NAPAS-B2]: senderDateTime vs creationDateTime field name.
"""

import logging
from datetime import date

import httpx

from app.config import settings
from app.core.crypto_napas import sign_payload, verify_napas_signature
from app.napas.client import NapasClient, SettlementRecord, TxnStatusDTO

logger = logging.getLogger(__name__)


class RealNapasClient(NapasClient):
    """NAPAS APG client — sandbox (apg-stg) hoặc production."""

    def __init__(self) -> None:
        self.base_url = settings.NAPAS_BASE_URL
        # TODO[NAPAS-A3]: OAuth2 token sẽ được lấy từ token endpoint
        self._access_token: str | None = None

    def _headers(self) -> dict[str, str]:
        """Build common headers cho mọi request NAPAS."""
        headers: dict[str, str] = {
            "Content-Type": "application/json",
        }
        # TODO[NAPAS-A2]: Thêm senderId, receiverId khi NAPAS cấp
        if settings.NAPAS_SENDER_ID:
            headers["senderId"] = settings.NAPAS_SENDER_ID
        if settings.NAPAS_RECEIVER_ID:
            headers["receiverId"] = settings.NAPAS_RECEIVER_ID
        # TODO[NAPAS-A3]: Thêm Authorization: Bearer {token} khi có OAuth2
        if self._access_token:
            headers["Authorization"] = f"Bearer {self._access_token}"
        return headers

    def _sign_and_post(self, url: str, payload: bytes) -> httpx.Response:
        """Sign payload + gửi POST request tới NAPAS.

        # TODO[NAPAS-B1]: Canonical JSON serialization chưa xác nhận.
        """
        signature = sign_payload(payload)
        headers = self._headers()
        headers["signature"] = signature

        resp = httpx.post(
            url,
            content=payload,
            headers=headers,
            timeout=30.0,
        )
        resp.raise_for_status()
        return resp

    def verify_notice_signature(self, payload: bytes, signature: str) -> bool:
        """Verify chữ ký RSA trên notification từ NAPAS."""
        return verify_napas_signature(payload, signature)

    def get_settlement_report(self, report_date: date) -> list[SettlementRecord]:
        """Gọi NAPAS reconciliation API lấy báo cáo đối soát.

        Endpoint: POST {base}/apg/reconciliation
        # TODO[NAPAS-B2]: Format request body chờ spec chi tiết.
        """
        import json
        url = settings.napas_reconciliation_url
        body = json.dumps({
            "reportDate": report_date.isoformat(),
            # TODO[NAPAS-A2]: senderId
            # TODO[NAPAS-B2]: thêm fields theo spec
        }).encode()

        resp = self._sign_and_post(url, body)
        data = resp.json()

        records: list[SettlementRecord] = []
        for item in data.get("records", []):
            records.append(SettlementRecord(
                full_order_id=item["orderId"],
                merchant_id=item["merchantId"],
                amount=int(item["amount"]),
                settled_at=item.get("settledAt", ""),
                status=item.get("status", "ACSC"),
            ))
        return records

    def get_transaction_status(self, full_order_id: str) -> TxnStatusDTO:
        """Tra cứu trạng thái giao dịch qua NAPAS investigation API.

        Endpoint: POST {base}/apg/investigation
        # TODO[NAPAS-B2]: Format request body chờ spec chi tiết.
        """
        import json
        url = settings.napas_investigation_url
        body = json.dumps({
            "orderId": full_order_id,
            # TODO[NAPAS-A2]: senderId
        }).encode()

        resp = self._sign_and_post(url, body)
        data = resp.json()

        return TxnStatusDTO(
            full_order_id=data["orderId"],
            status=data["status"],
            amount=int(data["amount"]),
            merchant_id=data.get("merchantId", ""),
            timestamp=data.get("timestamp", ""),
        )
