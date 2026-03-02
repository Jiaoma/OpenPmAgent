"""Common Pydantic schemas."""
from pydantic import BaseModel, Field
from typing import Generic, TypeVar, List, Optional

DataT = TypeVar('DataT')


class APIResponse(BaseModel, Generic[DataT]):
    """Standard API response wrapper."""

    code: int = Field(200, description="HTTP status code")
    message: str = Field("success", description="Response message")
    data: Optional[DataT] = Field(None, description="Response data")


class PaginatedResponse(BaseModel, Generic[DataT]):
    """Paginated API response."""

    code: int = Field(200, description="HTTP status code")
    message: str = Field("success", description="Response message")
    data: DataT = Field(..., description="Paginated data")


class PaginatedData(BaseModel, Generic[DataT]):
    """Paginated data wrapper."""

    items: List[DataT] = Field(default_factory=list, description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(1, description="Current page number")
    page_size: int = Field(20, description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")


class ErrorResponse(BaseModel):
    """Error response schema."""

    code: int = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    errors: Optional[List[dict]] = Field(None, description="Detailed errors")
