from abc import ABC, abstractmethod
from typing import Optional, Type

import motor.motor_asyncio as ma
from beanie import Document, init_beanie


class Database:
    def __init__(self, uri: str, database_name: str, doc_models: list[Type[Document]]):
        self._uri = uri
        self._database_name = database_name
        self._doc_models = doc_models
        self._client: Optional[ma.AsyncIOMotorClient] = None
        self._db: Optional[ma.AsyncIOMotorDatabase] = None
        self._fs: Optional[ma.AsyncIOMotorGridFSBucket] = None

    @property
    def uri(self):
        return self._uri

    @property
    def database_name(self):
        return self._database_name

    @property
    def client(self):
        return self._client

    @property
    def db(self):
        return self._db

    @property
    def fs(self):
        return self._fs

    @property
    def doc_models(self):
        return self._doc_models

    async def start(self):
        self._client = ma.AsyncIOMotorClient(self._uri, tz_aware=True)
        self._db = self._client[self._database_name]
        self._fs = ma.AsyncIOMotorGridFSBucket(self._db)
        await init_beanie(database=self._db, document_models=self._doc_models)

    async def end(self):
        pass
