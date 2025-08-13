import React, { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [sources, setSources] = useState([]);
  const [destinations, setDestinations] = useState([]);
  const [source, setSource] = useState("");
  const [destination, setDestination] = useState("");
  const [trains, setTrains] = useState([]);
  const [sortBy, setSortBy] = useState("");

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

  const sortedTrains = [...trains].sort((a, b) => {
    if (sortBy === "price") return a.price - b.price;
    if (sortBy === "time") return a.start.localeCompare(b.start);
    return 0;
  });

  return (
    <div className="app">
      <h1>Train Search Application</h1>

      <div className="dropdowns">
        <select value={source} onChange={(e) => setSource(e.target.value)}>
          <option value="">Select Source</option>
          {sources.map((st, idx) => (
            <option key={idx} value={st}>
              {st}
            </option>
          ))}
        </select>

        <select value={destination} onChange={(e) => setDestination(e.target.value)}>
          <option value="">Select Destination</option>
          {destinations.map((st, idx) => (
            <option key={idx} value={st}>
              {st}
            </option>
          ))}
        </select>

        <button onClick={searchTrains}>Search</button>
      </div>

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

      {/* IRCTC-style Train list */}
      <div className="train-list">
        {sortedTrains.length > 0 ? (
          sortedTrains.map((train, idx) => (
            <div key={idx} className="train-card-row">
              {/* Row 1: Train name + Price */}
              <div className="train-top">
                <div className="train-left">
                  <h3 className="train-name">
                    {train.trainName || `${train.firstTrain} ➜ ${train.secondTrain}`}
                  </h3>
                </div>
                <div className="train-right price-red">
  ₹{train.price?.toFixed(2)}
</div>
              </div>

              {/* Row 2: Start / Duration+Distance / End */}
              <div className="train-top" style={{ marginTop: "8px" }}>
                <div className="train-left">
                  <div className="station-time">
                    <span className="station">{source}</span>
                    <span className="time">{train.start}</span>
                  </div>
                </div>

                <div className="train-middle" style={{ textAlign: "center" }}>
                  <div className="duration">
                    {train.durationHours
                      ? `${train.durationHours}h ${train.durationMinutes}m`
                      : "—"}
                  </div>
                  <div style={{ fontSize: "0.85em", color: "#888" }}>
                    {train.distance ? `${train.distance} km` : ""}
                  </div>
                </div>

                <div className="train-right">
                  <div className="station-time">
                    <span className="station">{destination}</span>
                    <span className="time">{train.end}</span>
                  </div>
                </div>
              </div>

              {/* Route Display */}
              <div className="train-route">
                {train.type === "direct" && train.route && (
                  <div className="route-line">
                    {train.route.map((stop, stopIdx) => (
                      <div className="route-stop" key={stopIdx}>
                        <div className="dot"></div>
                        <div className="stop-name">{stop}</div>
                      </div>
                    ))}
                  </div>
                )}

                {train.type === "connecting" &&
                  train.route &&
                  Array.isArray(train.route) && (
                    <>
                      <div className="route-line">
                        {train.route[0].map((stop, stopIdx) => (
                          <div className="route-stop" key={`leg1-${stopIdx}`}>
                            <div className="dot"></div>
                            <div className="stop-name">{stop}</div>
                          </div>
                        ))}
                      </div>
                      <div className="route-line">
                        {train.route[1].map((stop, stopIdx) => (
                          <div className="route-stop" key={`leg2-${stopIdx}`}>
                            <div className="dot"></div>
                            <div className="stop-name">{stop}</div>
                          </div>
                        ))}
                      </div>
                    </>
                  )}
              </div>
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
