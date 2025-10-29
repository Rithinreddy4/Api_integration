import os
import json
from dotenv import load_dotenv
from azure.servicebus import ServiceBusClient
from logger_config import logger

load_dotenv()

SERVICE_BUS_CONNECTION_STR = os.getenv("SERVICE_BUS_CONNECTION_STR")
TOPIC_NAME = os.getenv("TOPIC_NAME")
SUBSCRIPTION_NAME = os.getenv("SUBSCRIPTION_NAME", "order_subscription")

if not all([SERVICE_BUS_CONNECTION_STR, TOPIC_NAME, SUBSCRIPTION_NAME]):
    raise RuntimeError("Set SERVICE_BUS_CONNECTION_STR, TOPIC_NAME, SUBSCRIPTION_NAME in .env")

def receive_orders(max_messages=10, max_wait_time=5):
    logger.info(f" Listening to topic '{TOPIC_NAME}' / subscription '{SUBSCRIPTION_NAME}'")
    with ServiceBusClient.from_connection_string(SERVICE_BUS_CONNECTION_STR) as client:
        receiver = client.get_subscription_receiver(
            topic_name=TOPIC_NAME, subscription_name=SUBSCRIPTION_NAME
        )
        with receiver:
            received = receiver.receive_messages(max_message_count=max_messages, max_wait_time=max_wait_time)
            if not received:
                logger.info("No new messages found.")
                return

            for msg in received:
                try:
                    order = json.loads(str(msg))
                    logger.info(
                        f" Received Order | ID={order.get('orderId')} | Customer={order.get('customerName')} | "
                        f"Product={order.get('product')} | Qty={order.get('quantity')} | Price={order.get('price'):.2f} | "
                        f"Total={order.get('quantity') * order.get('price'):.2f}"
                    )
                    receiver.complete_message(msg)
                    logger.info(f" Processed Order | ID={order.get('orderId')}")
                except Exception as ex:
                    logger.exception(f" Error processing message: {ex}")
                    receiver.abandon_message(msg)

if __name__ == "__main__":
    try:
        receive_orders()
    except KeyboardInterrupt:
        logger.info(" Consumer stopped manually.")
