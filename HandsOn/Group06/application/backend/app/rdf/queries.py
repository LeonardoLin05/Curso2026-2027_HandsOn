
import unicodedata

from rdflib import Graph, URIRef
from rdflib.namespace import RDF, RDFS, OWL

from app.rdf.namespaces import MC, SCHEMA
from app.schemas import (
    Accessibility,
    Address,
    Area,
    Contact,
    FacilityDetail,
    FacilitySummary,
    Location,
    LinkedData,
    FacilityFilters,
    NearbyFacility,
    NearbySearch
)

from app.services.geo import _calculate_distance

# --------------------------------------------------
# Fragmento común: información de las instalaciones
# --------------------------------------------------

FACILITY_COMMON_PATTERN = """
    VALUES ?facilityClass {
        mc:Library
        mc:Museum
    }

    ?facility rdf:type ?facilityClass .

    ?facility schema:name ?name .
    ?facility schema:latitude ?latitude .
    ?facility schema:longitude ?longitude .

    ?facility mc:hasAddress ?address .

    ?address mc:locatedInDistrict ?district .
    ?district schema:name ?district_name .

    ?address mc:locatedInNeighborhood ?neighborhood .
    ?neighborhood schema:name ?neighborhood_name .

    ?facility mc:hasAccessibility ?accessibility .

    ?accessibility mc:accessible ?accessible .
    ?accessibility mc:partiallyAccessible ?partially_accessible .
    ?accessibility mc:noInfoAccessibility ?no_info_accessibility .
    ?accessibility mc:signLanguage ?sign_language .
    ?accessibility mc:tactilePaving ?tactile_paving .
    ?accessibility mc:magneticInductionLoop ?magnetic_induction_loop .
"""


# --------------------------------------------------
# Consulta 1: listado de instalaciones
# --------------------------------------------------

FACILITIES_QUERY = """
    SELECT DISTINCT
        ?facility
        ?facilityClass
        ?name
        ?latitude
        ?longitude
        ?district
        ?district_name
        ?neighborhood
        ?neighborhood_name
        ?partially_accessible
        ?no_info_accessibility
        ?sign_language
        ?tactile_paving
        ?magnetic_induction_loop

    WHERE {
""" + FACILITY_COMMON_PATTERN + """
    }
"""


# --------------------------------------------------
# Consulta 2: detalle de una instalación
# --------------------------------------------------

FACILITY_DETAIL_QUERY = """
    SELECT
        ?facility
        ?facilityClass
        ?name
        ?latitude
        ?longitude
        ?address
        ?street
        ?postal_code
        ?district
        ?district_name
        ?neighborhood
        ?neighborhood_name
        ?opening_hours
        ?transport
        ?telephone
        ?email
        ?publisher_url
        ?same_as
        ?accessible
        ?partially_accessible
        ?no_info_accessibility
        ?sign_language
        ?tactile_paving
        ?magnetic_induction_loop

    WHERE {
""" + FACILITY_COMMON_PATTERN + """

        FILTER(?facility = ?facility_uri)

        ?address mc:streetAddress ?street .
        ?address mc:postalCode ?postal_code .

        ?facility schema:openingHours ?opening_hours .
        ?facility mc:transport ?transport .
        ?facility schema:telephone ?telephone .
        ?facility mc:email ?email .
        ?facility schema:url ?publisher_url .

        OPTIONAL {
            ?facility owl:sameAs ?same_as .
        }
    }
"""


# --------------------------------------------------
# Funciones auxiliares
# --------------------------------------------------

NAMESPACES = {
    "rdf": RDF,
    "rdfs": RDFS,
    "owl": OWL,
    "mc": MC,
    "schema": SCHEMA,
}


def _get_value(row: dict, key: str):
    """Obtiene el valor Python de una variable SPARQL."""

    value = row.get(key)

    if value is None:
        return None

    return value.toPython()


def _get_area(row: dict, uri_key: str, name_key: str) -> Area | None:
    """Construye un área administrativa si existe su URI."""

    uri = row.get(uri_key)

    return Area(
        uri=str(uri),
        name=_get_value(row, name_key),
    )


def _get_location(row: dict) -> Location | None:
    """Construye las coordenadas si ambas están disponibles."""

    latitude = _get_value(row, "latitude")
    longitude = _get_value(row, "longitude")

    return Location(
        latitude=float(latitude),
        longitude=float(longitude),
    )


def _get_facility_type(value) -> str:
    """Convierte la clase RDF en el tipo utilizado por la API."""

    if str(value) == str(MC.Library):
        return "library"

    return "museum"


def _row_to_dict(row) -> dict:
    """Convierte las variables de una fila SPARQL en un diccionario."""

    return {
        str(variable): value
        for variable, value in row.asdict().items()
    }


def _normalize_text(value: str) -> str:
    """Quita los acentos y mayúsculas a un texto"""
    value = unicodedata.normalize("NFD", value)
    value = "".join(
        character
        for character in value
        if unicodedata.category(character) != "Mn"
    )

    return value.casefold().strip()


def _matches_filters(
    row: dict, 
    filters: FacilityFilters
) -> bool:
    """Comprueba si una instalación cumple los filtros seleccionados."""

    # Filtro por nombre
    if filters.query:
        name = str(_get_value(row, "name"))

        if _normalize_text(filters.query) not in _normalize_text(name):
            return False

    # Filtro por tipo
    facility_type = _get_facility_type(row["facilityClass"])

    if filters.facility_types:
        if facility_type not in filters.facility_types:
            return False

    # Filtro por distrito
    if filters.district:
        if str(row["district"]) != filters.district:
            return False

    # Filtro por barrio
    if filters.neighborhood:
        if str(row["neighborhood"]) != filters.neighborhood:
            return False

    # Filtro por estado de accesibilidad
    if filters.accessibility_status:
        status_values = {
            "accessible": _get_value(row, "accessible"),
            "partial": _get_value(row, "partially_accessible"),
        }

        if not any(
            status_values[status]
            for status in filters.accessibility_status
        ):
            return False

    # Filtro por características de accesibilidad
    if filters.accessibility_features:
        feature_values = {
            "sign_language": _get_value(row, "sign_language"),
            "tactile_paving": _get_value(row, "tactile_paving"),
            "magnetic_induction_loop": _get_value(
                row,
                "magnetic_induction_loop",
            ),
        }

        if not all(
            feature_values[feature]
            for feature in filters.accessibility_features
        ):
            return False

    return True


def _within_distance(
    facility: FacilitySummary, 
    nearby: NearbySearch
) -> tuple[bool, float]:
    """Comprueba si una instalación está en las distancias especificadas"""

    distance = _calculate_distance(
        nearby.latitude,
        nearby.longitude,
        facility.location.latitude,
        facility.location.longitude,
    )

    # Comprobar si está dentro del radio.
    return distance <= nearby.radius, distance

# --------------------------------------------------
# Función para obtener el listado
# --------------------------------------------------

def get_facilities(
    graph: Graph, 
    filters: FacilityFilters | None = None, 
    nearby: NearbySearch | None = None
) -> list[FacilitySummary] | list[NearbyFacility]:
    """Obtiene los datos básicos de bibliotecas y museos."""

    results = graph.query(
        FACILITIES_QUERY,
        initNs=NAMESPACES,
    )

    facilities = []

    for result in results:
        row = _row_to_dict(result)

        # Aplicar filtros solamente si se ha proporcionado.
        if filters is not None and not _matches_filters(row, filters):
            continue

        facility = FacilitySummary(
            id=str(row["facility"]),
            name=str(_get_value(row, "name")),
            facility_type=_get_facility_type(row["facilityClass"]),
            location=_get_location(row),
            district=_get_area(row, "district", "district_name"),
            neighborhood=_get_area(
                row,
                "neighborhood",
                "neighborhood_name",
            ),
        )

        # Aplicar filtro distancia solamente si se ha proporcionado
        if nearby is not None:
            is_within_distance, distance = _within_distance(facility, nearby)

            if not is_within_distance:
                continue

            facilities.append(
                NearbyFacility(
                    facility=facility,
                    distance_km=round(distance, 3)
                )
            )
        else:
            facilities.append(facility)

    # Ordenar por distancia cuando se solicita cercanía.
    if nearby is not None:
        facilities.sort(key=lambda item: item.distance_km)

    return facilities


# --------------------------------------------------
# Función para obtener el detalle
# --------------------------------------------------

def get_facility_by_id(
    graph: Graph,
    facility_id: str
) -> FacilityDetail | None:
    """Obtiene toda la información de una instalación concreta."""

    results = graph.query(
        FACILITY_DETAIL_QUERY,
        initNs=NAMESPACES,
        initBindings={
            "facility_uri": URIRef(facility_id),
        },
    )

    result = next(iter(results), None)

    if result is None:
        return None

    row = _row_to_dict(result)

    address = Address(
        uri=str(row["address"]),
        street=_get_value(row, "street"),
        postal_code=_get_value(row, "postal_code"),
        district=_get_area(row, "district", "district_name"),
        neighborhood=_get_area(
            row,
            "neighborhood",
            "neighborhood_name",
        ),
    )

    accessibility = Accessibility(
        accessible=_get_value(row, "accessible"),
        partially_accessible=_get_value(
            row,
            "partially_accessible",
        ),
        no_info_accessibility=_get_value(
            row,
            "no_info_accessibility",
        ),
        sign_language=_get_value(row, "sign_language"),
        tactile_paving=_get_value(row, "tactile_paving"),
        magnetic_induction_loop=_get_value(
            row,
            "magnetic_induction_loop",
        ),
    )

    return FacilityDetail(
        id=str(row["facility"]),
        name=str(_get_value(row, "name")),
        facility_type=_get_facility_type(row["facilityClass"]),
        location=_get_location(row),
        district=_get_area(row, "district", "district_name"),
        neighborhood=_get_area(
            row,
            "neighborhood",
            "neighborhood_name",
        ),
        address=address,
        accessibility=accessibility,
        opening_hours=_get_value(row, "opening_hours"),
        transport=_get_value(row, "transport"),
        contact=Contact(
            telephone=_get_value(row, "telephone"),
            email=_get_value(row, "email"),
        ),
        publisher_url=str(row["publisher_url"]),
        linked_data=LinkedData(
            wikidata_uri=(
                str(row["same_as"])
                if row.get("same_as") is not None
                else None
            )
        ),
    )