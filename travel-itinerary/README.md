# AI-Based Travel Itinerary Generator
## Project Summary

Modern travel planning app built with **React frontend**, **FastAPI backend**, **MongoDB database**, and **Google Gemini AI**. Users can create AI-generated itineraries, save trips, and adjust existing plans with AI assistance.

## Tech Stack
- **Frontend:** React 18, Create React App
- **Backend:** FastAPI, Python 3.11
- **Database:** MongoDB 7.0
- **AI:** Google Gemini API
- **Deployment:** Docker & Docker Compose

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Google Gemini API key

### Environment Setup
1. Get Google Gemini API key from "https://aistudio.google.com/apikey"
2. Create `.env` file in project root:
```bash
GEMINI_API_KEY=your_api_key_here
MONGO_URL=mongodb://localhost:27017
DATABASE_NAME=itinerary_db
```

Note: The API key specified in the uploaded .env file will be removed after the interview.

## How to Run Using Docker:

1- Clone and navigate to project

2- cd travel-itinerary

3- Start all services: 

docker-compose up --build

## Access application
Frontend: http://localhost:3000

Backend API: http://localhost:8000

API Docs: http://localhost:8000/docs


## API Routes and Usage

| Method | Endpoint | Description | Body |
|--------|----------|-------------|------|
| `POST` | `/api/itinerary/generate` | Generate new itinerary with AI | `ItineraryInput` |
| `GET` | `/api/itinerary` | Get all saved itineraries | - |
| `GET` | `/api/itinerary/{id}` | Get specific itinerary | - |
| `POST` | `/api/itinerary` | Save itinerary | `Itinerary` |
| `PATCH` | `/api/itinerary/{id}` | AI-powered itinerary adjustment | `ItineraryAdjustment` |
| `DELETE` | `/api/itinerary/{id}` | Delete itinerary | - |


## Architecture Overview

### Frontend (React)
- **Single Page Application** with component-based architecture
- **Trip Creation Form** with validation (destination, dates, interests)
- **Trip Management** - view, delete, expand/collapse details
- **AI Adjustment Feature** - modify existing trips with predefined or custom prompts
- **Responsive Design** with loading states and error handling

### Backend (FastAPI)
- **RESTful API** with automatic OpenAPI documentation
- **Async operations** for optimal performance
- **MongoDB integration** with proper connection lifecycle
- **AI service layer** for Gemini API integration
- **Comprehensive error handling** and logging

### Database (MongoDB)
- **Document-based storage** for flexible itinerary data
- **Auto-generated ObjectIds** for unique trip identification

## Data Schema

### ItineraryInput
```python
{
    "destination": "string",
    "start_date": "date",
    "end_date": "date", 
    "interests": ["string"]
}
```

### Itinerary
```python
{
    "id": "string (optional)",
    "destination": "string",
    "start_date": "date",
    "end_date": "date",
    "interests": ["string"],
    "itinerary": [DayPlan]
}
```

### DayPlan
```python
{
    "day": "integer",
    "activities": ["string"]
}
```

### ItineraryAdjustment
```python
{
    "adjustment_prompt": "string"
}
```

## Gemini AI Integration

### Features
- **Intelligent Trip Generation** - Creates detailed daily itineraries based on user preferences
- **Dynamic Token Management** - Adjusts AI response length based on trip duration - (commented )
- **Trip Adjustment** - Modifies existing itineraries with natural language prompts


### Predefined Adjustment Options
- "Make it more budget-friendly"
- "Add more cultural activities"
- "Focus on food experiences"
- "Add outdoor activities"
- "Make it family-friendly"
- Custom prompts supported

### AI Configuration
- **Model:** `gemini-1.5-flash`
- **Token Limits:** maximum token limits : 8192
- **temperature:** 0.7


## Limitations & Known Issues

### Known Issues
1. **Docker MongoDB Connection** - Occasional connection issues requiring container restart
2. **Environment Variables** - Must restart containers after changing API keys
3. **Frontend Proxy** - Local development may need proxy configuration updates
4. **AI Response Parsing** - Complex itineraries may occasionally cause JSON parsing errors

### Technical Debt
- No caching layer for API responses
- Error handling could be more granular
- Unit test is not implemented
- CI/CD is not implemented
