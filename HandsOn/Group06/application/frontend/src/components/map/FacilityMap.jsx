import PropTypes from "prop-types";

import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  useMap,
} from "react-leaflet";

import L from "leaflet";

import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";

import "./FacilityMap.css";

// Configuración del icono de los marcadores.
const defaultIcon = L.icon({
  iconUrl: markerIcon,
  iconRetinaUrl: markerIcon2x,
  shadowUrl: markerShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
});

// Coordenadas del centro de Madrid.
const MADRID_CENTER = [40.4168, -3.7038];

function MapBounds({ facilities }) {
  const map = useMap();

  const bounds = facilities.map((facility) => [
    facility.location.latitude,
    facility.location.longitude,
  ]);

  if (bounds.length > 0) {
    map.fitBounds(bounds, {
      padding: [30, 30],
      maxZoom: 15,
    });
  }

  return null;
}

export default function FacilityMap({ facilities }) {
  // Nos quedamos únicamente con instalaciones
  // que tienen coordenadas válidas.
  const locatedFacilities = facilities.filter((facility) => {
    const latitude = facility.location?.latitude;
    const longitude = facility.location?.longitude;

    return (
      Number.isFinite(latitude) &&
      Number.isFinite(longitude) &&
      latitude >= -90 &&
      latitude <= 90 &&
      longitude >= -180 &&
      longitude <= 180
    );
  });

  return (
    <MapContainer
      center={MADRID_CENTER}
      zoom={12}
      scrollWheelZoom={true}
      className="facility-map"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      <MapBounds facilities={locatedFacilities} />

      {locatedFacilities.map((facility) => (
        <Marker
          key={facility.id}
          position={[
            facility.location.latitude,
            facility.location.longitude,
          ]}
          icon={defaultIcon}
        >
          <Popup>
            <strong>{facility.name}</strong>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}

MapBounds.propTypes = {
  facilities: PropTypes.arrayOf(
    PropTypes.shape({
      location: PropTypes.shape({
        latitude: PropTypes.number.isRequired,
        longitude: PropTypes.number.isRequired,
      }).isRequired,
    })
  ).isRequired,
};

FacilityMap.propTypes = {
  facilities: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      name: PropTypes.string.isRequired,
      location: PropTypes.shape({
        latitude: PropTypes.number,
        longitude: PropTypes.number,
      }),
    })
  ).isRequired,
};