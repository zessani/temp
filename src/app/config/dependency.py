from typing import Annotated

from fastapi import Depends

from app.db.mongo.resume import ResumeDatabase


def make_database() -> ResumeDatabase:
    return ResumeDatabase()


database: ResumeDatabase = make_database()


def dependency_database():
    return database


def dependency():
    return database


DatabaseDep = Annotated[ResumeDatabase, Depends(dependency_database)]
