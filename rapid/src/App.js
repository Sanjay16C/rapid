import React, { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [stations, setStations] = useState([]);
  const [source, setSource] = useState("");
  const [destination, setDestination] = useState("");
  const [trains, setTrains] = useState([]);
  const [sortBy, setSortBy] = useState("");

  // Mock: Fetch stations from backend
  useEffect(() => {
    // Replace with: fetch("/api/stations").then(...)
    setStations([
      "Chennai",
      "Vellore",
      "Bangalore",
      "Mysuru",
      "Mangalore",
      "Shimoga",
    ]);
  }, []);

  // Handle search
  const searchTrains = () => {
    if (!source || !destination) {
      alert("Please select both source and destination");
      return;
    }

    // Mock API data
    // Replace with real fetch(`/api/trains?source=${source}&destination=${destination}`)
    const mockData = [
      {
        trainName: "Train A",
        start: "15:30",
        end: "21:45",
        distance: 420,
        price: 420 * 1.25,
      },
      {
        trainName: "Train B",
        start: "09:00",
        end: "17:30",
        distance: 430,
        price: 430 * 1.25,
      },
    ];

    setTrains(mockData);
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
          {stations.map((st, idx) => (
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
          {stations.map((st, idx) => (
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