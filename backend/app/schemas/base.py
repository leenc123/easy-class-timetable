"""
通用响应模型
"""
from pydantic import BaseModel
from typing import Optional, Any, Generic, TypeVar, List

T = TypeVar("T")


class ResponseBase(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    message: str = "操作成功"


class PaginatedResponse(BaseModel, Generic[T]):
    success: bool = True
    data: List[T] = []
    total: int = 0
    page: int = 1
    page_size: int = 20
    message: str = "操作成功"