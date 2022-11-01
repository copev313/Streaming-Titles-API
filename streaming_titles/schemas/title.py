from typing import List, Optional, Union

from pydantic import BaseModel

from schemas.enums import TitleType, Platform


class GeneralResponseSchema(BaseModel):
    """A schema for general responses. """
    status: str
    detail: str


class CreateTitleSchema(BaseModel):
    """Schema for creating a title record. """
    show_id: str
    title: str
    type: TitleType
    director: Optional[str] = None
    cast: Union[List[str], List[None]] = []
    country: Optional[str] = None
    date_added: Optional[str] = None
    release_year: Optional[str] = None
    rating: Optional[str] = None
    duration: Optional[str] = None
    genres: Union[List[str], List[None]] = []
    description: Optional[str] = None
    platform: Platform


class UpdateTitleSchema(BaseModel):
    """Schema for updating a title record. 
    
    NOTE: This schema is designed to be used in PATCH requests. Best when used
    alongside the `model.dict(...)` method, with arguments `exclude_unset=True`
    or `exclude_none=True`.
    """
    # pass
    show_id: Optional[str] = None
    title: Optional[str] = None
    type: Optional[TitleType] = None
    director: Optional[str] = None
    cast: Optional[Union[List[str], List[None]]] = None
    country: Optional[str] = None
    date_added: Optional[str] = None
    release_year: Optional[str] = None
    rating: Optional[str] = None
    duration: Optional[str] = None
    genres: Optional[Union[List[str], List[None]]] = None
    description: Optional[str] = None
    platform: Optional[Platform] = None


class DeletedTitleSchema(GeneralResponseSchema):
    """Schema for deleting a title record. """
    pk: int


class TitleOutSchema(CreateTitleSchema):
    """Schema for title record output. """
    pk: int


class ListTitlesSchema(BaseModel):
    """Schema for listing title records. """
    total: int
    titles: list[TitleOutSchema]


class ListTitlePagesSchema(ListTitlesSchema):
    """Schema for listing title records by pages. """
    page: int
    total_pages: int
    has_prev: bool
    has_next: bool
