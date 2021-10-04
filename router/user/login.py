from typing import Optional
from fastapi import Request, Header, Depends

import os
from fastapi import Query
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from slowapi import Limiter
from slowapi.util import get_remote_address
from email.mime.text import MIMEText

from models import User, LoginUser, VerifyEmail, AuthorizationStorage
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
            ).to_dict()
        user = await User.get(id=login_user.id)
        if not find_and_get_lambda(
            login_user.trusted_device["devices"],
            check=lambda device: device["ip-address"] == str(request.client.host),
        ):
            random_code = os.urandom(15).hex()
            await VerifyEmail.create(
                code=random_code,
                data={
                    "verify_type": "trust_device",
                    "data": {
                        "email": email,
                        "user-agent": user_agent,
                        "ip-address": str(request.client.host),
                    },
                },
            )
            await self.email_verify(
                email=email, content=f"http://localhost:5500/verify?code={random_code}"
            )
            return ErrorForm(
                error_code=50036,
                errors=[
                    Error(
                        error_code="NOT_TRUST_DEVICE",
                        message="새로운 디바이스에서 로그인했습니다. 이메일을 확인하세요.",
                    )
                ],
            )
        access_key = os.urandom(20).hex()
        await AuthorizationStorage.create(key=access_key, id=user.id)
        return {
            "code": "LOGIN_SUCCESS",
            "data": {"access_key": access_key},
            "message": "로그인 완료.",
        }

    @router.post("/verify")
    @router.get("/verify")
    @rate_limiter.limiter("100/second")
    async def verify_email(
        self,
        code: str = Query(
            None, title="인증 코드", description="이메일 인증을 위해 인증 고유 코드를 제출하세요."
        ),
    ):
        if not await VerifyEmail.exists(code=code):
            return ErrorForm(
                error_code=50035,
                errors=[Error(error_code="INVALID_CODE", message="인증 코드가 올바르지 않습니다.")],
            ).to_dict()
        verify_email = await VerifyEmail.get(code=code)
        data = verify_email.data
        if data["verify_type"] == "trust_device":
            login_user = await LoginUser.get(email=data["data"]["email"])
            devices = login_user.trusted_device["devices"]
            devices.append(
                {
                    "user-agent": data["data"]["user-agent"],
                    "ip-address": data["data"]["ip-address"],
                }
            )
            login_user.trusted_device = devices
            await login_user.save()
            await verify_email.delete()
            return
        elif data["verify_type"] == "register":
            await LoginUser.create(
                email=data["data"]["email"],
                id=data["data"]["id"],
                password=data["data"]["password"],
                trusted_device={
                    "devices": [
                        {
                            "user-agent": data["data"]["user-agent"],
                            "ip-address": data["data"]["ip-address"],
                        }
                    ]
                },
            )
            access_key = os.urandom(20).hex()
            await User.create(
                id=data["data"]["id"],
                name=data["data"]["nick"],
            )
            await AuthorizationStorage.create(key=access_key, id=data["data"]["id"])
            await verify_email.delete()
            return {
                "code": "REGISTER_SUCCESS",
                "data": {"access_key": access_key},
                "message": "가입이 완료되었습니다.",
            }

        return ErrorForm(
            error_code=500,
            errors=[
                Error(
                    error_code="SERVER_ERROR",
                    message=f"알 수 없는 오류가 발생했습니다, {verify_email.code}",
                )
            ],
        ).to_dict()

    @router.post("/register")
    async def register(
        self,
        request: Request,
        user_agent: Header(None),
        user_id: str = Query(
            None, alias="id", title="유저 아이디", description="유저에게 부여할 영어 아이디입니다."
        ),
        nick: str = Query(None, title="유저 닉네임 or 이름", description="유저에게 부여할 닉네임입니다."),
        email: str = Query(
            None,
            title="로그인 이메일",
            description="로그인에 사용할 이메일을 입력하세요.",
            min_length=6,
            regex=r"^[\w\.\+\-]+\@[\w]+\.[a-z]{2,3}$",
        ),
        password: str = Query(
            None, title="로그인 비밀번호", description="로그인에 사용할 비밀번호를 입력하세요.", min_length=8
        ),
    ):
        if await LoginUser.exists(email=email):
            return ErrorForm(
                error_code=50037,
                errors=[
                    Error(error_code="ALREADY_EXIST", message="해당 이메일은 이미 가입되어 있습니다.")
                ],
            )
        elif await LoginUser.exists(id=user_id):
            return ErrorForm(
                error_code=50037,
                errors=[
                    Error(error_code="ALREADY_EXIST", message="해당 아이디는 이미 가입되어 있습니다.")
                ],
            )
        random_code = os.urandom(15).hex()
        await VerifyEmail.create(
            code=random_code,
            data={
                "verify_type": "register",
                "data": {
                    "email": email,
                    "id": user_id,
                    "nick": nick,
                    "password": password,
                    "ip-address": str(request.client.host),
                    "user-agent": user_agent,
                },
            },
        )
        return {"code": "REGISTER_VERIFY", "message": "이메일 인증을 위해 인증을 위한 이메일을 전송했습니다."}

    @router.post("/logout")
    async def logout(
        self,
        _request: Request,
        access_key: str = Query(
            None, title="유저 인증 토큰", description="로그인 시에 발급했던 유저 인증 토큰을 제출하세요."
        ),
    ):
        if not await AuthorizationStorage.exists(key=access_key):
            return ErrorForm(
                error_code=50038,
                errors=[Error(error_code="INVALID_TOKEN", message="잘못된 토큰입니다.")],
            ).to_dict()
        authorization = await AuthorizationStorage.get(key=access_key)
        await authorization.delete()
        return {"code": "LOGOUT_SUCCESS", "message": "로그아웃이 완료되었습니다."}


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
