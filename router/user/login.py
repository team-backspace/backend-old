from typing import Optional
from fastapi import Request, Header

from fastapi import Query
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from slowapi import Limiter
from slowapi.util import get_remote_address
from email.mime.text import MIMEText

from models import User, LoginUser
from form import Error, ErrorForm
from utils import Email, find_and_get_lambda

router = InferringRouter()
rate_limiter = Limiter(key_func=get_remote_address)


@cbv(router)
class Login:
    @router.post("/login")
    @rate_limiter.limiter("100/second")
    async def login(
        self,
        request: Request,
        user_agent: Header("user-agent"),
        email: str = Query(
            None,
            title="이메일",
            description="로그인에 사용하는 이메일을 입력하세요.",
            min_length=6,
            regex=r"^[\w\.\+\-]+\@[\w]+\.[a-z]{2,3}$",
        ),
        password: str = Query(
            None,
            title="비밀번호",
            description="로그인에 사용하는 비밀번호를 입력하세요.",
            min_length=8,
        ),
        captcha_key: Optional[str] = Query(
            None, title="캡차 인증 키", description="캡차 인증이 필요할 경우, 캡차 키를 입력하세요."
        ),
        _application_source: Optional[dict] = Query(
            None,
            alias="application_source",
            title="특정 애플리케이션 허가 데이터",
            description="특정 애플리케이션을 통해 로그인 하는 경우, 애플리케이션에 필요한 데이터를 입력하세요.",
            deprecated=True,
        ),
    ):
        if not await LoginUser.exists(email=email):
            return ErrorForm(
                error_code=50035,
                errors=[Error(error_code="INVALID_EMAIL", message="유효하지 않은 이메일 입니다.")],
            ).to_dict()
        login_user = await LoginUser.get(email=email)
        if not login_user.password == password:
            return ErrorForm(
                error_code=50035,
                errors=[Error(error_code="INVALID_PASSWORD", message="비밀번호가 다릅니다.")],
            )
        user = await User.get(id=login_user.id)
        if not find_and_get_lambda(
            login_user.trusted_device["devices"],
            check=lambda device: device["ip-address"] == str(request.client.host),
        ):
            ...

    @staticmethod
    async def email_verify(email: str, content: str) -> None:
        config = router.config["email"]
        connection = Email(host=config["host"], port=config["port"], tls=True)
        await connection.login(email=config["sender"], password=config["password"])
        html_source = open("source/verify_email.html").read()
        html = html_source.replace("{{verify_url}}", content)
        attachment = MIMEText(html, "html")
        await connection.send(
            email=email, subject="Spacebook 이메일 인증", attachments=[attachment]
        )
        await connection.close()
