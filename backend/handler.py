import boto3
import json
import logging
import time

logger = logging.getLogger("handler_logger")
logger.setLevel(logging.DEBUG)

dynamodb = boto3.resource("dynamodb")

def default_message(event, context):
    """
    Send back error when unrecognized WebSocket action is received.
    """
    logger.info("Unrecognized WebSocket action received.")
    return _get_response(400, "Unrecognized WebSocket action.")

def ping(event, context):
    """
    Sanity check endpoint that echoes back 'PONG' to the sender.
    """
    logger.info("Ping requested.")
    return _get_response(200, "PONG!")

def _get_response(status_code, body):
    if not isinstance(body, str):
        body = json.dumps(body)
    return {"statusCode": status_code, "body": body}

def _get_body(event):
    try:
        return json.loads(event.get("body", ""))
    except:
        logger.debug("event body could not be JSON decoded.")
        return {}

def _send_to_connection(connection_id, data, event):
    gatewayapi = boto3.client("apigatewaymanagementapi",
            endpoint_url = "https://" + event["requestContext"]["domainName"] +
                    "/" + event["requestContext"]["stage"])
    return gatewayapi.post_to_connection(ConnectionId=connection_id,
            Data=json.dumps(data).encode('utf-8'))

def connection_manager(event, context):
    """
    Handles connecting and disconnecting for the Websocket.
    """
    connectionID = event["requestContext"].get("connectionId")

    if event["requestContext"]["eventType"] == "CONNECT":
        logger.info("Connect requested")

        # Add connectionID to the database
        table = dynamodb.Table("gov-chat_Connections")
        table.put_item(Item={"ConnectionID": connectionID})
        return _get_response(200, "Connect successful.")

    elif event["requestContext"]["eventType"] == "DISCONNECT":
        logger.info("Disconnect requested")

        # Remove the connectionID from the database
        table = dynamodb.Table("gov-chat_Connections")
        table.delete_item(Key={"ConnectionID": connectionID})
        return _get_response(200, "Disconnect successful.")

    else:
        logger.error("Connection manager received unrecognized eventType '{}'")
        return _get_response(500, "Unrecognized eventType.")

def send_message(event, context):
    """
    When a message is sent on the socket, forward it to all connections.
    """
    logger.info("Message sent on WebSocket.")

    # Ensure all required fields were provided
    body = _get_body(event)
    for attribute in ["username", "content", "room"]:
        if attribute not in body:
            logger.debug("Failed: '{}' not in message dict."\
                    .format(attribute))
            return _get_response(400, "'{}' not in message dict"\
                    .format(attribute))

    # Get the next message index
    table = dynamodb.Table("gov-chat_Messages")
    response = table.query(KeyConditionExpression="Room = :room",
            ExpressionAttributeValues={":room": body['room']},
            Limit=1, ScanIndexForward=False)
    logger.info(response)
    items = response.get("Items", [])
    index = items[0]["Index"] + 1 if len(items) > 0 else 0

    # Add the new message to the database
    timestamp = int(time.time())
    username = body["username"]
    content = body["content"]
    room = body["room"]
    table.put_item(Item={"Room": room, "Index": index,
            "Timestamp": timestamp, "Username": username,
            "Content": content})

    # Get all current connections
    table = dynamodb.Table("gov-chat_Connections")
    response = table.scan(ProjectionExpression="ConnectionID")
    items = response.get("Items", [])
    connections = [x["ConnectionID"] for x in items if "ConnectionID" in x]

    # Send the message data to all connections
    message = {"username": username, "content": content}
    logger.debug("Broadcasting message: {}".format(message))
    data = {"messages": [message]}
    for connectionID in connections:
        _send_to_connection(connectionID, data, event)

    return _get_response(200, "Message sent to all connections.")

def get_recent_messages(event, context):
    """
    Return the 10 most recent chat messages.
    """
    logger.info("Retrieving most recent messages.")
    connectionID = event["requestContext"].get("connectionId")

    # Ensure all required fields were provided
    body = _get_body(event)
    for attribute in ["room"]:
        if attribute not in body:
            logger.debug("Failed: '{}' not in message dict."\
                    .format(attribute))
            return _get_response(400, "'{}' not in message dict"\
                    .format(attribute))

    # Get the 10 most recent chat messages
    table = dynamodb.Table("gov-chat_Messages")
    response = table.query(KeyConditionExpression="Room = :room",
            ExpressionAttributeValues={":room": body['room']},
            Limit=10, ScanIndexForward=False)
    items = response.get("Items", [])

    # Extract the relevant data and order chronologically
    messages = [{"username": x["Username"], "content": x["Content"]}
            for x in items]
    messages.reverse()

    # Send them to the client who asked for it
    data = {"messages": messages}
    _send_to_connection(connectionID, data, event)

    return _get_response(200, "Sent recent messages.")
