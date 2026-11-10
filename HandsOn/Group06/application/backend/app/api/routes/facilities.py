from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Request

from rdflib import Graph

from app.rdf.queries import (
    get_facilities,
    get_facility_by_id,
)

from app.schemas import (
    FacilitySummary,
    FacilityDetail,
    FacilityFilters,
    NearbySearch, 
    NearbyFacility
)


router = APIRouter(
    prefix="/facilities",
    tags=["Facilities"],
)


@router.get("", response_model=list[FacilitySummary] | list[NearbyFacility])
def list_facilities(
    request: Request, 
    filters: Annotated[FacilityFilters, Query()],
    latitude: float | None = Query(default=None, ge=-90, le=90),
    longitude: float | None = Query(default=None, ge=-180, le=180),
    radius: float = Query(default=1.0)
):
    """Devuelve todas las bibliotecas y museos (sin detalles)"""

    graph: Graph = request.app.state.rdf_graph

    # Comprobar los parámetros de búsqueda por cercanía.
    nearby = None

    if latitude is not None or longitude is not None:

        if latitude is None or longitude is None:
            raise HTTPException(
                status_code=400,
                detail="Debes proporcionar latitud y longitud conjuntamente.",
            )

        nearby = NearbySearch(
            latitude=latitude,
            longitude=longitude,
            radius=radius,
        )

    return get_facilities(graph, filters, nearby)


@router.get("/{facility_id:path}", response_model=FacilityDetail)
def facility_detail(
    facility_id: str,
    request: Request,
):
    """Devuelve los detalles de una instalación."""

    graph: Graph = request.app.state.rdf_graph

    facility = get_facility_by_id(
        graph,
        facility_id,
    )

    if facility is None:
        raise HTTPException(
            status_code=404,
            detail="Facility not found",
        )

    return facility
