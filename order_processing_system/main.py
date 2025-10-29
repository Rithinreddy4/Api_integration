import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from logger_config import logger

load_dotenv()

SERVICE_BUS_CONNECTION_STR = os.getenv("SERVICE_BUS_CONNECTION_STR")
TOPIC_NAME = os.getenv("TOPIC_NAME")

if not SERVICE_BUS_CONNECTION_STR or not TOPIC_NAME:
    raise RuntimeError("SERVICE_BUS_CONNECTION_STR and TOPIC_NAME must be set in .env")

app = FastAPI(title="Azure Service Bus Order API")

class Order(BaseModel):
    orderId: str
    customerName: str
    product: str
    quantity: int
    price: float

@app.get("/")
def health_check():
    logger.info("Health check endpoint hit.")
    return {"status": "running", "message": "Azure Service Bus Order API is healthy "}

@app.post("/place-order")
async def place_order(order: Order):
    if order.quantity <= 0:
        raise HTTPException(status_code=400, detail="quantity must be > 0")

    payload = order.model_dump()
    msg_body = json.dumps(payload)

    try:
        with ServiceBusClient.from_connection_string(SERVICE_BUS_CONNECTION_STR) as client:
            sender = client.get_topic_sender(topic_name=TOPIC_NAME)
            with sender:
                message = ServiceBusMessage(msg_body)
                message.application_properties = {"event": "order.created", "orderId": order.orderId}
                sender.send_messages(message)

        logger.info(
            f" New Order Published | ID={order.orderId} | Customer={order.customerName} | "
            f"Product={order.product} | Qty={order.quantity} | Price={order.price:.2f} | Total={order.quantity * order.price:.2f}"
        )
        return {"status": "success", "message": "Order published successfully"}

    except Exception as e:
        logger.exception(f" Error publishing message: {e}")
        raise HTTPException(status_code=500, detail=f"Error publishing message: {str(e)}")
