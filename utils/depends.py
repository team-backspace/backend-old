from fastapi import Request, HTTPException
from models import AuthorizationStorage, User


async def user_authorization(request: Request):
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
        )
    if not await AuthorizationStorage.exists(key=token):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
        )
    authorization_data = await AuthorizationStorage.get(key=token)
    user = await User.get(id=authorization_data.id)
    return user
