from pydantic import BaseModel


class MetricsOut(BaseModel):
    gmv_settled: int  # total VND of SETTLED/NOTIFIED/RECONCILED txns (ACSC confirmed)
    gmv_pending: int  # total VND of AUTHORIZED txns (ACSP only, not yet settled)
    fee_receivable: int  # total PHAI_THU fees
    fee_received: int  # total DA_NHAN fees
    queue_pending: int  # count of notify_queue where batched_at IS NULL
    dispute_count: int  # count of LECH reconciliations

    model_config = {"from_attributes": True}
