
import PropTypes from "prop-types";
import "./FacilityCard.css";

export default function FacilityCard({ facility }) {
  return (
    <article className="facility-card">
      <span className="facility-type">
        {facility.facility_type === "library" ? "Biblioteca" : "Museo"}
      </span>

      <h2>{facility.name}</h2>

      <p>Distrito: {facility.district.name}</p>

      <p>Barrio: {facility.neighborhood.name}</p>
    </article>
  );
}

FacilityCard.propTypes = {
  facility: PropTypes.shape({
    id: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
    facility_type: PropTypes.oneOf(["library", "museum"]).isRequired,
    district: PropTypes.shape({
      name: PropTypes.string.isRequired,
    }).isRequired,
    neighborhood: PropTypes.shape({
      name: PropTypes.string.isRequired,
    }).isRequired
  }).isRequired,
};
