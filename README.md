Train Search Web Application

A full-stack web application to search trains between stations, powered by FastAPI, MongoDB, and React.js.

Problem Statement:
The task is to develop a train search application that allows users to select source and
destination stations from the available options and view a list of trains that operate
on that route. The application should enable users to sort the list of trains based on
prices and timings for the entered route.



Requirements:

The train search application should meet the following requirements:

	• Allow users to select source and destination stations from a dropdown menu
	• Display a clear and concise list of available trains, including information on
	train name, departure and arrival times, and ticket prices for the entered route.
	• Allow users to sort the list of trains based on price
	• Price should be determined based on distance of the journey (Rs 1.25/km).
	• Be scalable and able to handle a large number of stations and train routes
	• Be user-friendly and easy to navigate
	• For ease of testing, develop a test data generation script, that generates 1000
	trains and thier routes in your application db.


Tech Stack:

Backend:

		•	Python 3.10+
		•	FastAPI
		•	Uvicorn
		•	Pymongo

Middleware:

	  •	CORS
  
Frontend:

	•	React.js
	•	Axios (API calls)

Database:

	•	MongoDB (via MongoDB Compass)

Folder structure

	rapid/
	│
	├── backend/
	│   ├── main.py         # FastAPI app entry point
	│   ├── dataset.py      # Script to insert sample data
	│   └── requirements.txt
	│
	├── rapid/              #Frontend
	│   ├── src/
	│   │   ├── App.js
	│   │   ├── App.css
	│   │   └── ...
	│   └── package.json
	│
	└── README.md


Installation & Setup

1. Clone the repo

        git clone https://github.com/Sanjay16C/rapid.git
        cd rapid


2. Backend Setup

        cd backend

        python3 -m venv venv
        source venv/bin/activate  # Mac/Linux
        #OR
        venv\Scripts\activate     # Windows
        
        pip install -r requirements.txt

3. Make sure your mongo url looks like this or according to yours:
   
        MONGO_URI=mongodb://localhost:27017
        DB_NAME=train_db1

5. Run dataset insertion script:

       python dataset.py

6. Run FastAPI server:

       uvicorn main:app --reload


7. Frontend Setup

        cd ../frontend
        npm install
        npm start



📡 API Endpoints

Below are the available API endpoints and their expected request/response formats.



1️⃣ Get All Stations

Endpoint:

GET /stations

Description:
Returns the list of all stations present in the database.

Example Response:

	{
	  "stations": [
	    "Delhi",
	    "Mumbai",
	    "Chennai",
	    "Kolkata"
	  ]
	}




2️⃣ Get All Sources

Endpoint:

GET /sources

Description:
Returns all stations that can be the starting station of a train.

Example Response:

	{
	  "sources": [
	    "Delhi",
	    "Mumbai",
	    "Bangalore",
	    "Hyderabad"
	  ]
	}




3️⃣ Get All Destinations for a Given Source

Endpoint:

GET /destinations

Query Parameters:
	•	source (required) — Name of the source station.

Example Request:

GET /destinations?source=Delhi

Example Response:

	{
	  "destinations": [
	    "Mumbai",
	    "Jaipur",
	    "Lucknow"
	  ]
	}



4️⃣ Search Trains Between Two Stations

Endpoint:

GET /trains

Query Parameters:
	•	source (required) — Name of the starting station
	•	destination (required) — Name of the ending station

Description:
Searches for direct and connecting trains between two stations.

Example Request (Direct train available):

GET /trains?source=Delhi&destination=Mumbai

Example Response (Direct Train):

	{
	  "trains": [
	    {
	      "type": "direct",
	      "trainName": "Golden Express",
	      "start": "05:00",
	      "end": "14:30",
	      "distance": 1400,
	      "price": 1750.0,
	      "route": ["Delhi", "Jaipur", "Ahmedabad", "Mumbai"]
	    }
	  ]
	}


Example Response (Connecting Train):

	{
	  "trains": [
	    {
	      "type": "connecting",
	      "firstTrain": "Silver Shatabdi",
	      "secondTrain": "Crimson Express",
	      "hub": "Ahmedabad",
	      "start": "06:30",
	      "hub_arrival": "13:00",
	      "hub_departure": "14:00",
	      "end": "22:15",
	      "distance": 1450,
	      "price": 1812.5,
	      "route": [
	        ["Delhi", "Jaipur", "Ahmedabad"],
	        ["Ahmedabad", "Surat", "Mumbai"]
	      ]
	    }
	  ]
	}







