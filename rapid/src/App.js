import React, { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [sources, setSources] = useState([]);
  const [destinations, setDestinations] = useState([]);
  const [source, setSource] = useState("");
  const [destination, setDestination] = useState("");
  const [trains, setTrains] = useState([]);
  const [sortBy, setSortBy] = useState("");

  // Fetch source stations from backend
  useEffect(() => {
    const fetchSources = async () => {
      try {
        const res = await fetch("http://localhost:8000/sources");
        const data = await res.json();
        setSources(data.sources || []);
      } catch (error) {
        console.error("Error fetching sources:", error);
      }
    };
    fetchSources();
  }, []);

  // Fetch destination stations when source changes
  useEffect(() => {
    const fetchDestinations = async () => {
      if (!source) {
        setDestinations([]);
        return;
      }
      try {
        const res = await fetch(`http://localhost:8000/destinations?source=${source}`);
        const data = await res.json();
        setDestinations(data.destinations || []);
      } catch (error) {
        console.error("Error fetching destinations:", error);
      }
    };
    fetchDestinations();
  }, [source]);

  // Search trains from backend
  const searchTrains = async () => {
    if (!source || !destination) {
      alert("Please select both source and destination");
      return;
    }

    try {
      const res = await fetch(
        `http://localhost:8000/trains?source=${source}&destination=${destination}`
      );
      const data = await res.json();
      setTrains(data.trains || []);
    } catch (error) {
      console.error("Error fetching trains:", error);
    }
  };

  // Handle sorting
  const sortedTrains = [...trains].sort((a, b) => {
    if (sortBy === "price") return a.price - b.price;
    if (sortBy === "time") return a.start.localeCompare(b.start);
    return 0;
  });

  return (
    <div className="app">
      <h1>Train Search Application</h1>

      {/* Dropdowns */}
      <div className="dropdowns">
        <select value={source} onChange={(e) => setSource(e.target.value)}>
          <option value="">Select Source</option>
          {sources.map((st, idx) => (
            <option key={idx} value={st}>
              {st}
            </option>
          ))}
        </select>

        <select
          value={destination}
          onChange={(e) => setDestination(e.target.value)}
        >
          <option value="">Select Destination</option>
          {destinations.map((st, idx) => (
            <option key={idx} value={st}>
              {st}
            </option>
          ))}
        </select>

        <button onClick={searchTrains}>Search</button>
      </div>

      {/* Sorting */}
      {trains.length > 0 && (
        <div className="sort">
          <label>Sort by: </label>
          <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
            <option value="">Default</option>
            <option value="price">Price</option>
            <option value="time">Departure Time</option>
          </select>
        </div>
      )}

      {/* Train list */}
      <div className="train-list">
        {sortedTrains.length > 0 ? (
          sortedTrains.map((train, idx) => (
            <div key={idx} className="train-card">
              <h3>{train.trainName}</h3>
              <p>
                <strong>Departure:</strong> {train.start}
              </p>
              <p>
                <strong>Arrival:</strong> {train.end}
              </p>
              <p>
                <strong>Distance:</strong> {train.distance} km
              </p>
              <p>
                <strong>Price:</strong> ₹{train.price.toFixed(2)}
              </p>
            </div>
          ))
        ) : (
          <p>No trains found for this route.</p>
        )}
      </div>
    </div>
  );
}

export default App;
