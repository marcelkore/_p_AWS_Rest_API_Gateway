import json
import logging
import os
import uuid
from datetime import datetime

import boto3

import dynamo  # helper function

logger = logging.getLogger()
logger.setLevel(logging.INFO)
dynamodb = boto3.client("dynamodb")
# dynamodb = boto3.resource(
# 'dynamodb', region_name=str(os.environ['REGION_NAME']))
table_name = str(os.environ["DYNAMODB_TABLE"])


def create(event, context):
    """Create a new post and store it in DynamoDB.

    Args:
        event (events): data that is passed to the function
        context (context_.Context): provides contextual information to the function

    Returns:
        events.APIGatewayResponse: A response to the user
    """
    logger.info(f"Incoming request is: {event}")

    # Set the default error response
    response = {
        "statusCode": 500,
        "body": "An error occurred while creating post.",
    }

    # extract the post from the body
    post_str = event["body"]

    # convert to json and store in a post variable
    post = json.loads(post_str)

    # generate a unique timestamp for the post
    current_timestamp = datetime.now().isoformat()
    post["createdAt"] = current_timestamp

    # generate a unique id for the post
    post["id"] = str(uuid.uuid4())

    # insert the post into the database
    # to_item below converts the post to a dictionary that can be stored in dynamodb
    res = dynamodb.put_item(TableName=table_name, Item=dynamo.to_item(post))

    # If creation is successful
    if res["ResponseMetadata"]["HTTPStatusCode"] == 200:
        response = {
            "statusCode": 201,
        }

    return response


def get(event, context):
    """Query DynamoDB for the post with the given id.
    ID is passed as a path parameter (events)

    Args:
        event (events): data that is passed to the function
        context (context_.Context): provides contextual information to the function

    Returns:
        events.APIGatewayResponse: A response to the user
    """

    print(":::::==>>>", event["pathParameters"])
    logger.info(f"Incoming request is: {event}")
    # Set the default error response
    response = {
        "statusCode": 500,
        "body": "An error occurred while getting post.",
    }
    print(":::::==>>>", event)

    # extract the post id from the path parameters
    post_id = event["pathParameters"]["postId"]

    # Query the post from the database
    post_query = dynamodb.get_item(
        TableName=table_name, Key={"id": {"S": post_id}}
    )

    # If the post is found
    if "Item" in post_query:
        post = post_query["Item"]
        logger.info(f"Post is: {post}")
        response = {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(dynamo.to_dict(post)),
        }

    return response


def all(event, context):
    """Retrieve all posts from DynamoDB.
    ID is passed as a path parameter (events)

    Args:
        event (events): Not used but still required by the function
        context (context_.Context): provides contextual information to the function

    Returns:
        events.APIGatewayResponse: A response to the user
    """
    # Set the default error response
    response = {
        "statusCode": 500,
        "body": "An error occurred while getting all posts.",
    }

    # Query the posts from the database
    scan_result = dynamodb.scan(TableName=table_name)["Items"]

    posts = []

    for item in scan_result:
        posts.append(dynamo.to_dict(item))

    response = {"statusCode": 200, "body": json.dumps(posts)}

    return response


def update(event, context):
    """Update a post in DynamoDB with the given id.
    ID is passed as a path parameter (events)

    Args:
        event (events): Not used but still required by the function
        context (context_.Context): provides contextual information to the function

    Returns:
        events.APIGatewayResponse: A response to the user
    """
    logger.info(f"Incoming request is: {event}")

    # retrieve the post id from the path parameters
    post_id = event["pathParameters"]["postId"]

    # Set the default error response
    response = {
        "statusCode": 500,
        "body": f"An error occurred while updating post {post_id}",
    }

    # extract the event body from the request
    post_str = event["body"]

    # convert to json and store in a post variable
    post = json.loads(post_str)

    # function to update the post in dynamodb
    res = dynamodb.update_item(
        TableName=table_name,
        Key={"id": {"S": post_id}},
        UpdateExpression="set content=:c, author=:a, updatedAt=:u",
        ExpressionAttributeValues={
            ":c": dynamo.to_item(post["content"]),
            ":a": dynamo.to_item(post["author"]),
            ":u": dynamo.to_item(datetime.now().isoformat()),
        },
        ReturnValues="UPDATED_NEW",
    )

    # If update  is successful for post
    # return appropriate response
    if res["ResponseMetadata"]["HTTPStatusCode"] == 200:
        response = {
            "statusCode": 200,
        }

    return response


def delete(event, context):
    """Delete a post from DynamoDB with the given id.
    ID is passed as a path parameter (events)

    Args:
        event (events): Not used but still required by the function
        context (context_.Context): provides contextual information to the function

    Returns:
        events.APIGatewayResponse: A response to the user
    """
    logger.info(f"Incoming request is: {event}")

    # retrieve the post id from the path parameters
    post_id = event["pathParameters"]["postId"]

    # Set the default error response
    response = {
        "statusCode": 500,
        "body": f"An error occurred while deleting post {post_id}",
    }

    # function to delete the post from dynamodb
    res = dynamodb.delete_item(
        TableName=table_name, Key={"id": {"S": post_id}}
    )

    # If deletion is successful for post
    if res["ResponseMetadata"]["HTTPStatusCode"] == 200:
        response = {
            "statusCode": 204,
        }
    return response
