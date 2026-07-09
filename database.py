import os
from motor.motor_asyncio import AsyncIOMotorClient # MongoDB async driver instead of pymongo
from dotenv import load_dotenv

load_dotenv()

class Database:
  mongo_uri = os.getenv("MONGO_URI")

  client = None
  discord_bot_db = None
  modlogs_collection = None
  modlogschannel_collection = None
  dark_history_collection = None

  @classmethod
  async def initDB(cls) -> bool:
    try:
      cls.client = AsyncIOMotorClient(cls.mongo_uri)
      await cls.client.admin.command("ping")
      print("Successfully connected to MongoDB!")

      cls.discord_bot_db = cls.client["discord_bot_db"]
      cls.modlogs_collection = cls.discord_bot_db["modlogs"]
      cls.modlogschannel_collection = cls.discord_bot_db["modlogschannel"]
      cls.dark_history_collection = cls.discord_bot_db["dark_history"]

      return True

    except Exception as err:
      print(f"Error connect to MongoDB: {err}")
      return False