"""
    All the API routes for the title records.
"""
import math
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security.api_key import APIKey
from sqlalchemy.sql import select, insert, update, delete

from models.title import TitleRecord
from schemas.title import (
    CreateTitleSchema,
    ListTitlePagesSchema,
    ListTitlesSchema,
    TitleOutSchema,
    UpdateTitleSchema
)
from schemas.enums import Platform, TitleType
from database.session import db
from routes.auth import get_api_key


router = APIRouter(
    prefix="/api/v1",
    tags=["titles"],
)


@router.get("/titles", response_model=ListTitlePagesSchema)
async def get_all_titles(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=25, ge=1),
    title: Optional[str] = Query(default=None),
    type: Optional[TitleType] = Query(default=None),
    release_yr: Optional[int] = Query(default=None),
    platform: Optional[Platform] = Query(default=None),
    genres: Optional[List[str]] = Query(default=None),
    director: Optional[str] = Query(default=None),
    country: Optional[str] = Query(default=None),
):
    """Route for getting all titles.

    Parameters
    ----------
    skip : int, optional (default=0)
        The number of records to skip before starting the list.
    
    limit : int, optional (default=25)
        The number of records to return at a time.
    """
    try:
        filter_by = ()
        # Filter by title if provided:
        if title:
            filter_by += (TitleRecord.title.ilike(f"%{title}%"), )
        # Filter by type if provided:
        if type:
            filter_by += (TitleRecord.type == type, )
        # Filter by release year if provided:
        if  release_yr and 2100 > release_yr > 1900:
            filter_by += (TitleRecord.release_yr == release_yr, )
        # Filter by platform if provided:
        if platform:
            filter_by += (
                TitleRecord.platform == platform, 
            )
        # Filter by genres if provided:
        if genres:
            genres_list = [ g.title() for g in genres ]
            filter_by += (TitleRecord.genres.contains(genres_list), )
        # Filter by director if provided:
        if director:
            filter_by += (TitleRecord.director.ilike(f"%{director}%"), )
        # Filter by country if provided:
        if country:
            filter_by += (TitleRecord.country.ilike(f"%{country}%"), )

        # Determine the query that needs to be run:
        if filter_by:
            qry = select(TitleRecord).filter(*filter_by)
            count_qry = select(TitleRecord.pk).filter(*filter_by)
        else:
            qry = select(TitleRecord)
            count_qry = select(TitleRecord.pk)

        # Query for counting number of results returned:
        skip = ((page - 1) * limit)
        count_titles = await db.fetch_all(query=count_qry)
        record_count = len(count_titles)
        titles = await db.fetch_all(query=qry.offset(skip).limit(limit))
        total = int(record_count)
        total_pgs = math.ceil(total / limit)
        # Return the response:
        return {
            "total": total,
            "titles": titles,
            "total_pages": total_pgs,
            "page": page,
            "has_next": page < total_pgs,
            "has_prev": page > 1
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while trying to get all titles. | {e} "
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
        total_records_count = await db.execute(
            select(TitleRecord).count()
        )
        total = all_titles_response["total"]
        titles = all_titles_response["titles"]
        total_pgs = math.ceil(int(total_records_count) / limit)
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
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
    try:
        query = select(TitleRecord).where(TitleRecord.pk == int(pk))
        title = await db.fetch_one(query=query)
        if title is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Title record not found for primary key: {pk}"
                )
            )
        return title

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "ERROR: Failed to get title by primary key. "
                f"(pk={pk})"
            )
        )


@router.post("/titles", status_code=201, response_model=TitleOutSchema)
async def create_title_record(new_title: CreateTitleSchema,
                              api_key: APIKey = Depends(get_api_key)):
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
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ERROR: Failed to create title record. {e} "
        )


@router.patch("/titles/{pk}", status_code=200, response_model=TitleOutSchema)
async def update_title_record(pk: int,
                              record_update: UpdateTitleSchema,
                              api_key: APIKey = Depends(get_api_key)):
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
        query = update(TitleRecord).where(TitleRecord.pk == int(pk)).values(
            **record_update.dict(exclude_unset=True)
        )
        await db.execute(query=query)
        updated_record = await get_title(pk=int(pk))
        return updated_record

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                f"ERROR: Failed to update record with primary key: {pk}. {e} "
            )
        )


@router.delete("/titles/{pk}", status_code=204)
async def delete_title_record(pk: int,
                              api_key: APIKey = Depends(get_api_key)):
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
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                f"ERROR: Failed to delete record with primary key: {pk}."
            )
        )
