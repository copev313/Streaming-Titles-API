"""
    All the API routes for the title records.
"""
import math

from fastapi import APIRouter, HTTPException
from sqlalchemy.sql import select, insert, update, delete

from models.title import TitleRecord
from schemas.title import (
    CreateTitleSchema,
    ListTitlePagesSchema,
    ListTitlesSchema,
    TitleOutSchema,
    UpdateTitleSchema
)
from database.session import db


router = APIRouter(
    prefix="/api/v1",
    tags=["titles"],
)


@router.get("/titles", response_model=ListTitlesSchema)
async def get_all_titles(skip: int = 0, limit: int = 25):
    """Route for getting all titles.

    Parameters
    ----------
    skip : int, optional (default=0)
        The number of records to skip before starting the list.
    
    limit : int, optional (default=25)
        The number of records to return at a time.
    """
    try:
        query = select(TitleRecord).offset(skip).limit(limit)
        titles = await db.fetch_all(query=query)
        return {
            "total": len(titles),
            "titles": titles
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="An error occurred while trying to get all titles."
        )


@router.get("/title-pages", response_model=ListTitlePagesSchema)
async def get_titles_paginated(page: int = 1, limit: int = 25):
    """Route for getting titles by page. Extends on the `get_all_titles`
    route.

    Parameters
    ----------
    page : int, optional (default=1)
        The page number to return.

    limit : int, optional (default=25)
        The number of records to return at a time.
    """
    try:
        skip = (page - 1) * limit
        all_titles_response = await get_all_titles(skip=skip, limit=limit)
        total = all_titles_response["total"]
        titles = all_titles_response["titles"]
        total_pgs = math.ceil(total / limit)
        has_next = page < total_pgs
        has_prev = page > 1
        return {
            "total": total,
            "titles": titles,
            "total_pages": total_pgs,
            "page": page,
            "has_next": has_next,
            "has_prev": has_prev
        }

    except Exception:
        raise HTTPException(
            status_code=500,
            detail=(
                "ERROR: Failed to get titles by page. "
                f"(page={page}, limit={limit})"
            )
        )


@router.get("/titles/{pk}", response_model=TitleOutSchema)
async def get_title(pk: int):
    """Route for getting a single title by primary key.

    Parameters
    ----------
    pk : int
        The primary key of the title record.
    """
    query = select(TitleRecord).where(TitleRecord.pk == int(pk))
    title = await db.fetch_one(query=query)
    if title is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Title record not found for primary key: {pk}"
            )
        )
    return title


@router.post("/titles", status_code=201, response_model=TitleOutSchema)
async def create_title_record(new_title: CreateTitleSchema):
    """Endpoint for creating a new title record.

    Parameters
    ----------
    new_title : CreateTitleSchema
        The title record to create.
    """
    try:
        query = insert(TitleRecord).values(**new_title.dict())
        pk = await db.execute(query=query)
        return {
            "pk": pk,
            **new_title.dict()
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"ERROR: Failed to create title record. {e} "
        )


@router.patch("/titles/{pk}", status_code=200, response_model=TitleOutSchema)
async def update_title_record(pk: int, record_update: UpdateTitleSchema):
    """Endpoint for updating a title record. Only the fields that are provided
    will be updated.

    Parameters
    ----------
    pk: int
        The primary key of the title record to update.

    record_update: UpdateTitleSchema
        The updated title record data.
    """
    try:
        query = update(TitleRecord).where(TitleRecord.pk == int(pk))\
                    .values(**record_update.dict(exclude_unset=True))
        await db.execute(query=query)
        updated_record = await get_title(pk=int(pk))
        return updated_record

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=(
                f"ERROR: Failed to update record with primary key: {pk}. {e} "
            )
        )


@router.delete("/titles/{pk}", status_code=204)
async def delete_title_record(pk: int):
    """Endpoint for deleting a title record.

    Parameters
    ----------
    pk: int
        The primary key of the title record to delete.
    """
    try:
        query = delete(TitleRecord).where(TitleRecord.pk == int(pk))
        await db.execute(query=query)

    except Exception:
        raise HTTPException(
            status_code=500,
            detail=(
                f"ERROR: Failed to delete record with primary key: {pk}."
            )
        )
