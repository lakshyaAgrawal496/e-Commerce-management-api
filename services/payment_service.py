from sqlalchemy.ext.asyncio import AsyncSession
from models import PaymentResponse
from schemas import Payment
from utils.enums import PaymentMethod, PaymentStatus
from repositories import PaymentRepo
from exceptions import PaymentRefundError
import logging

logger = logging.getLogger("GrocerEase.payment_service")

class PaymentService:
    def __init__(self,db:AsyncSession):
        self.db = db
        self.payment_repo = PaymentRepo(db)

    def orm_to_response(self,result):
        return PaymentResponse(
            payment_id=result.payment_id,
            order_id=result.order_id,
            status=result.status,
            method=result.method,
            final_amount=result.final_amount
        )
    
    async def process_payment(self,order,method:PaymentMethod):
        status = PaymentStatus.PENDING if method == PaymentMethod.COD else PaymentStatus.SUCCESS
        payment = Payment(
            order_id=order.order_id,
            status=status,
            method=method,
            final_amount=order.final_amount
        )
        result = await self.payment_repo.create_payment(payment)
        logger.info(f"Payment processed successfully - payment_id={result.payment_id} order_id={result.order_id} method={method}")
        return self.orm_to_response(result) 

    async def refund_payment(self, payment):
        if payment.status != PaymentStatus.SUCCESS:
            logger.warning(f"Refund failed: payment already refunded - payment_id={payment.payment_id}")
            raise PaymentRefundError()
        payment.status = PaymentStatus.REFUNDED
        logger.info(f"Payment refunded successfully - payment_id={payment.payment_id} order_id={payment.order_id}")

    async def mark_collected(self, payment):
        if payment.status == PaymentStatus.PENDING:
            payment.status = PaymentStatus.SUCCESS

    async def cancel_pending(self, payment):
        payment.status = PaymentStatus.CANCELLED