"""
统一异常处理模块

定义业务异常和统一错误响应格式。
"""
from typing import Optional

from fastapi import status
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """
    统一错误响应模型。

    对应 OpenAPI 规范中的错误响应格式。
    """
    code: str
    description: str
    solution: Optional[str] = None
    detail: Optional[dict] = None
    link: Optional[str] = None


class BusinessException(Exception):
    """
    业务异常基类。

    所有业务相关的异常都应该继承此类。
    """

    def __init__(
        self,
        code: str,
        description: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        solution: Optional[str] = None,
        detail: Optional[dict] = None,
        link: Optional[str] = None,
    ):
        self.code = code
        self.description = description
        self.status_code = status_code
        self.solution = solution
        self.detail = detail
        self.link = link
        super().__init__(description)

    def to_response(self) -> JSONResponse:
        """转换为 JSONResponse。"""
        content = {
            "code": self.code,
            "description": self.description,
        }
        if self.solution:
            content["solution"] = self.solution
        if self.detail:
            content["detail"] = self.detail
        if self.link:
            content["link"] = self.link

        return JSONResponse(
            status_code=self.status_code,
            content=content,
        )


def create_error_response(
    status_code: int,
    code: str,
    description: str,
    solution: Optional[str] = None,
    detail: Optional[dict] = None,
    link: Optional[str] = None,
) -> JSONResponse:
    """
    创建统一格式的错误响应。

    参数:
        status_code: HTTP 状态码
        code: 业务错误码
        description: 错误描述
        solution: 错误处理建议
        detail: 错误详细信息
        link: 错误帮助地址

    返回:
        JSONResponse: 格式化的错误响应
    """
    content = {
        "code": code,
        "description": description,
    }
    if solution:
        content["solution"] = solution
    if detail:
        content["detail"] = detail
    if link:
        content["link"] = link

    return JSONResponse(
        status_code=status_code,
        content=content,
    )
