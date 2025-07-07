from app.config.env_vars import EnvironmentVars
from app.db.mongo import Database
from app.model.schema.together import DOCUMENTS


class ResumeDatabase(Database):
    def __init__(self):
        super().__init__(
            uri=f"mongodb://{EnvironmentVars.DB_USERNAME}:{EnvironmentVars.DB_PASSWORD}@{EnvironmentVars.DB_HOST}:{EnvironmentVars.DB_PORT}/",
            database_name=EnvironmentVars.DB_DATABASE,
            doc_models=DOCUMENTS,
        )
