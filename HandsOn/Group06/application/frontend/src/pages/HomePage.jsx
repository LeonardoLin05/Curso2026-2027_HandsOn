
import { useState } from "react";

import Header from "../components/layout/Header";

import FacilityList from "../components/facilities/FacilityList";

import FacilityMap from "../components/map/FacilityMap";

import FacilityFilters from "../components/filters/FacilityFilters";

import { getFacilities } from "../services/facilityService";

import "./HomePage.css";

export default function HomePage() {
  const [query, setQuery] = useState("");
  const [facilities, setFacilities] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [filters, setFilters] = useState({
    facility_types: [],
    accessibility_status: [],
    accessibility_features: [],
  });

  async function handleSearch(event) {
    event.preventDefault();

    setLoading(true);
    setError(null);

    try {
      const data = await getFacilities({
        query,
        ...filters,
      });
      setFacilities(data);
    } catch (err) {
      setError("No se pudieron obtener las instalaciones: " + err);
    } finally {
      setLoading(false);
    }
  }

  function handleFilterChange(filterName, newValue) {
    setFilters((previousFilters) => ({
      ...previousFilters,
      [filterName]: newValue,
    }));
  }

  return (
    <div className="app-layout">
      <Header />

      <main className="home-page">
        <section className="hero">
          <form className="search-container" onSubmit={handleSearch}>
            <input
              type="text"
              placeholder="Buscar bibliotecas y museos..."
              aria-label="Buscar bibliotecas y museos"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
            />
            <button type="submit" disabled={loading}>
              {loading ? "Buscando..." : "Buscar"}
            </button>
          </form>

          <FacilityFilters
            filters={filters}
            onFilterChange={handleFilterChange}
          />
        </section>

        <section className="results-section">
          {error && <p>{error}</p>}

          {!loading && !error && (
                <>
                  <div className="content-layout">
                    <div className="results-container">
                      <FacilityList facilities={facilities} />
                    </div>

                    <div className="map-container">
                      <FacilityMap facilities={facilities} />
                    </div>
                  </div>
                </>
          )}
        </section>
      </main>
    </div>
  );
}
