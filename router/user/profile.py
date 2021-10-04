from typing import Optional
from fastapi import Request, Header, Depends

from fastapi import Query
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from slowapi import Limiter
from slowapi.util import get_remote_address

from models import User
from utils import user_authorization

router = InferringRouter()
rate_limiter = Limiter(key_func=get_remote_address)


@cbv(router)
class Profile:
    @router.post("/me/edit")
    async def edit_profile(
        self,
        request: Request,
        authorization: User = Depends(user_authorization),
        nick: Optional[str] = Query(
            None,
            title="변경할 유저 닉네임을 입력하세요.",
            description="변경할 유저 닉네임을 입력합니다. 중복이 가능합니다.",
        ),
        bio: Optional[str] = Query(
            None,
            title="변경할 유저 소개를 입력하세요.",
            description="변경할 유저 소개를 입력합니다.유저 소개는 프로필에 표시됩니다.",
        ),
        profile_url: Optional[str] = Query(
            None,
            title="변경할 유저 프로필 url를 입력하세요.",
            description="변경할 유저 프로필 url를 입력합니다. url만 입력이 가능합니다.",
        ),
        banner_url: Optional[str] = Query(
            None,
            title="변경할 유저 배너 url를 입력하세요.",
            description="변경할 유저 배너 url를 입력합니다. url만 입력이 가능합니다.",
        ),
    ):
        ...
