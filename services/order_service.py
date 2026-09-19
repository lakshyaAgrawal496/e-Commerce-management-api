from sqlalchemy.ext.asyncio import AsyncSession
from models import OrderResponse, OrderItemResponse
from schemas import OrderItem, Order, ReturnOrder
from repositories import OrderRepo,CartRepo,InventoryRepo
from services import CheckoutService, PaymentService
from exceptions import OrderNotFoundError,OrderCannotBeCancelledError,OrderCannotBeReturnedError,ReturnAlreadyRequestedError,InventoryNotFoundError,InsufficientStockError,CartItemNotFoundError,PaymentFailedError,AlreadyCancelledOrderError
from utils.enums import PaymentMethod, OrderStatus
import logging

logger = logging.getLogger("GrocerEase.order_service")
 
class OrderService:
    def __init__(self,db:AsyncSession):
        self.db = db
        self.order_repo = OrderRepo(db)
        self.cart_repo = CartRepo(db)
        self.inventory_repo = InventoryRepo(db)
        self.checkout_service = CheckoutService(db)
        self.payment_service = PaymentService(db)

    def orm_to_response(self,order):
        return OrderResponse(
                user_id=order.user_id,
                ordered_at=order.ordered_at,
                order_id=order.order_id,
                payment_id=order.payment.payment_id,
                order_status=order.status,
                total_amount=order.total_amount,
                discounted_amount=order.discount_amount,
                final_amount=order.final_amount,
                items=[OrderItemResponse(
                    product_id=item.product_id,
                    product_name=item.product.product_name,
                    unit_price=item.product.unit_price,
                    quantity=item.quantity
                )for item in order.items
            ]
        )
    
    async def get_order(self, order_id:int, user_id:int):
        order = await self.order_repo.get_order(order_id,user_id)
        if order is None:
            logger.warning(f"Order not found: order_id={order_id}")
            raise OrderNotFoundError()

        logger.info(f"Order with ID: {order_id} fetched successfully")
        return self.orm_to_response(order)
    
    async def get_order_history(self, user_id:int):
        orders = await self.order_repo.get_order_history(user_id)
        if not orders:
            logger.warning(f"Order history not exist for userID: {user_id}")
            raise OrderNotFoundError()

        logger.info(f"Order history fetched successsfully for userID: {user_id}")
        return [self.orm_to_response(order) for order in orders]
    
    async def get_all_orders(self):
        orders = await self.order_repo.get_all_orders()
        if not orders:
            logger.warning("Customer hasn't ordered anything yet")
            raise OrderNotFoundError()

        logger.info("Orders fetched successfully")
        return [self.orm_to_response(order) for order in orders]

    async def place_order(self,user_id:int,method:PaymentMethod):
        async with self.db.begin():
            checkout_data = await self.checkout_service.checkout(user_id)

            total_amount = checkout_data.total_amount
            discount_amount = checkout_data.discounted_amount
            final_amount = checkout_data.final_amount

            order_data = Order(
                user_id=user_id,
                status=OrderStatus.PLACED,
                total_amount=total_amount,
                discount_amount=discount_amount,
                final_amount=final_amount
            )

            order = await self.order_repo.create_order(order_data)

            try:
                await self.payment_service.process_payment(order,method)
            except PaymentFailedError:
                logger.warning(f"Payment failed - order_id={order.order_id}")
                raise 

            for item in checkout_data.items:
                order_item = OrderItem(
                    order_id=order.order_id,
                    product_id=item.product_id,
                    quantity=item.quantity
                )
                await self.order_repo.add_order_item(order_item)
            logger.info(f"Order items added successfully - order_id={order.order_id}")

            for item in checkout_data.items:
                inventory = await self.inventory_repo.get_inventory(item.product_id)
                if inventory is None:
                    logger.warning(f"Inventory not found - product_id={item.product_id}")
                    raise InventoryNotFoundError()
                if inventory.quantity < item.quantity:
                    logger.warning(f"Insufficient inventory - product_id={item.product_id} requested={item.quantity} available={inventory.quantity}")
                    raise InsufficientStockError()

                inventory.quantity -= item.quantity
                logger.info(f"Inventory decremented successfully - product_id={item.product_id} quantity={item.quantity}")

                cart = await self.cart_repo.get_cart_item(item.product_id,item.cart_id)
                await self.cart_repo.remove_from_cart(cart)
            logger.info(f"Cart cleared successfully after order placement - order_id={order.order_id}")

            order = await self.order_repo.get_order(order.order_id, user_id)
            logger.info(f"Order placed successfully - order_id={order.order_id} user_id={user_id}")

            return self.orm_to_response(order)
    
    async def cancel_order(self, order_id: int, user_id: int):
        async with self.db.begin():
            order = await self.order_repo.get_order(order_id,user_id)
            if order is None:
                logger.warning(f"Order not found for ID: {order_id}")
                raise OrderNotFoundError()
            if order.status == OrderStatus.CANCELLED:
                logger.warning(f"Order cancellation failed: already cancelled - order_id={order_id}")
                raise AlreadyCancelledOrderError()
            if order.status != OrderStatus.PLACED:
                logger.warning(f"Order cancellation failed: invalid status - order_id={order_id} status={order.status}")
                raise OrderCannotBeCancelledError()

            for item in order.items:
                inventory = await self.inventory_repo.get_inventory(item.product_id)
                if inventory is None:
                    logger.warning(f"Inventory not found - product_id={item.product_id}")
                    raise InventoryNotFoundError()

                inventory.quantity += item.quantity
            logger.info(f"Inventory incremented successfully - product_id={item.product_id}")

            if order.payment.method != PaymentMethod.COD:
                await self.payment_service.refund_payment(order.payment)
            logger.info("Refund has been initated")

            order.status = OrderStatus.CANCELLED
            logger.info("Order status has been updated to Cancelled")
            return self.orm_to_response(order)

    async def return_order(self,order_id: int,user_id: int,reason: str):
        async with self.db.begin():
            order = await self.order_repo.get_order(order_id,user_id)
            if order is None:
                logger.warning(f"Order not found: order_id={order_id}")
                raise OrderNotFoundError()
            if order.status != OrderStatus.DELIVERED:
                logger.warning(f"Order return failed: order not delivered - order_id={order_id} status={order.status}")
                raise OrderCannotBeReturnedError()

            existing_return = await self.order_repo.get_return_order(order_id)
            if existing_return:
                logger.warning(f"Order return failed: return already requested - order_id={order_id}")
                raise ReturnAlreadyRequestedError()

            return_order = ReturnOrder(order_id=order.order_id,reason=reason,status=OrderStatus.RETURNED)
            await self.order_repo.create_return_order(return_order)
            logger.info(f"Payment refunded successfully - order_id={order_id} payment_id={order.payment.payment_id}")

            for item in order.items:
                inventory = await self.inventory_repo.get_inventory(item.product_id)
                if inventory is None:
                    logger.warning(f"Inventory not found - product_id={item.product_id}")
                    raise InventoryNotFoundError()
                
                inventory.quantity += item.quantity

            logger.info(f"Inventory restored for returned order item - product_id={item.product_id} quantity={item.quantity}")
            await self.payment_service.refund_payment(order.payment)
            logger.info(f"Payment refunded for returned order - order_id={order_id} payment_id={order.payment.payment_id}")

            logger.info(f"Order return requested successfully - order_id={order_id}")
            return self.orm_to_response(order)

    async def update_order_status(self,order_id:int,user_id:int,status:OrderStatus):
        async with self.db.begin():
            order = await self.order_repo.get_order(order_id,user_id)
            if order is None:
                logger.warning(f"Order not found: order_id={order_id}")
                raise OrderNotFoundError()
            updated_order = await self.order_repo.update_order_status(order,status)
            logger.info(f"Order status updated - order_id={order_id} to new_status={status}")
            return self.orm_to_response(updated_order)