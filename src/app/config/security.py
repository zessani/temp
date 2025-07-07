from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.config.env_vars import EnvironmentVars

security = HTTPBasic()


def api_authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    if (
        credentials.username != EnvironmentVars.API_USERNAME
        or credentials.password != EnvironmentVars.API_PASSWORD
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
