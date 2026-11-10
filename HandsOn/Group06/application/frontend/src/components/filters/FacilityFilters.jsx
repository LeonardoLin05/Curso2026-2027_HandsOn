
import PropTypes from "prop-types";

import { useState } from "react";

import "./FacilityFilters.css";

export default function FacilityFilters({ filters, onFilterChange }) {

  const [isOpen, setIsOpen] = useState(false);

  function handleFeatureChange(event) {
    const { value, checked } = event.target;

    const currentFeatures = filters.accessibility_features;

    const updatedFeatures = checked
      ? [...currentFeatures, value]
      : currentFeatures.filter((feature) => feature !== value);

    onFilterChange("accessibility_features", updatedFeatures);
  }

  function handleStatusChange(event) {
    const value = event.target.value;

    onFilterChange(
      "accessibility_status",
      value ? value.split(",") : []
    );

    if (!value) {
      onFilterChange("accessibility_features", []);
    }
  }

  return (
    <section className="facility-filters">
      <button
        type="button"
        className="filters-toggle"
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
      >
        <span>Filtros</span>
        <span>{isOpen ? "▲" : "▼"}</span>
      </button>

      {isOpen && (
        <div className="filters-content">
          {/* Tipo de instalación */}
          <div className="filter-group">
            <label htmlFor="facility-type">
              Tipo de instalación
            </label>

            <select
              id="facility-type"
              value={filters.facility_types[0] ?? ""}
              onChange={(event) =>
                onFilterChange(
                  "facility_types",
                  event.target.value ? [event.target.value] : []
                )
              }
            >
              <option value="">Todas</option>
              <option value="library">Bibliotecas</option>
              <option value="museum">Museos</option>
            </select>
          </div>

          {/* Estado de accesibilidad */}
          <div className="filter-group">
            <label htmlFor="accessibility-status">
              Estado de accesibilidad
            </label>

            <select
              id="accessibility-status"
              value={filters.accessibility_status.join(",")}
              onChange={handleStatusChange}
            >
              <option value="">Cualquier estado</option>
              <option value="accessible">Accesible</option>
              <option value="partial">Parcialmente accesible</option>
              <option value="accessible,partial"> Accesible y parcialmente accesible</option>
            </select>
          </div>

          {/* Características de accesibilidad */}
          {filters.accessibility_status.length > 0 && (
            <div className="filter-group">
              <p>Características de accesibilidad</p>

              <label>
                <input
                  type="checkbox"
                  value="sign_language"
                  checked={filters.accessibility_features.includes("sign_language")}
                  onChange={handleFeatureChange}
                />
                Señalización en lengua de signos
              </label>

              <label>
                <input
                  type="checkbox"
                  value="tactile_paving"
                  checked={filters.accessibility_features.includes("tactile_paving")}
                  onChange={handleFeatureChange}
                />
                Pavimento podotáctil
              </label>

              <label>
                <input
                  type="checkbox"
                  value="magnetic_induction_loop"
                  checked={filters.accessibility_features.includes(
                    "magnetic_induction_loop"
                  )}
                  onChange={handleFeatureChange}
                />
                Bucle de inducción magnética
              </label>
            </div>
          )}
        </div>
      )}
    </section>
  );
}

FacilityFilters.propTypes = {
  filters: PropTypes.shape({
    facility_types: PropTypes.arrayOf(
      PropTypes.oneOf(["library", "museum"])
    ).isRequired,
    accessibility_status: PropTypes.arrayOf(
      PropTypes.oneOf(["accessible", "partial"])
    ).isRequired,
    accessibility_features: PropTypes.arrayOf(
      PropTypes.oneOf([
        "sign_language",
        "tactile_paving",
        "magnetic_induction_loop",
      ])
    ).isRequired,
  }).isRequired,
  onFilterChange: PropTypes.func.isRequired,
};
