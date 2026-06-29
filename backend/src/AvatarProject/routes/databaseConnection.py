# ================== Sample connection to MongoDB database =======================
from fastapi import APIRouter
import os
from pymongo import AsyncMongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

router = APIRouter()
load_dotenv()
MONGO_DB_URL = os.environ["MONGO_DB_URL"]

# Connect to the cluster
client = AsyncMongoClient(MONGO_DB_URL, server_api = ServerApi(version="1", strict=True, deprecation_errors=True))

@router.get("/testEndpoint")
async def getAllUsers() -> list:
    """ Sample endpoint connecting to a MongoDB database

    Returns:
        list : returns a list of users currently placed in the db
    """

    try:
        users = []
        # Access database
        db = client.get_database("AvatarProject")

        # Access a collection
        user_collection = db.get_collection("User")

        async for user in user_collection.find():
            users.append(user["name"])

        return users
    except Exception as e:
        print(f"error when loading data : {e}")
    finally:
        client.close()