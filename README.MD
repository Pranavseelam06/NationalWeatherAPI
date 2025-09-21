# DisasterSafety API

A FastAPI-based API that checks if a location is inside an active National Weather Service (NWS) alert zone and returns the nearest safe cities.

---

## Setup

### 1. Clone project
git clone https://github.com/your-username/DisasterSafetyAPI.git
cd DisasterSafetyAPI
### 2. Create a vitural entironment
python3 -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
### 3. Install Dependencies
pip install -r requirements.txt
### 4. Run the API
uvicorn app:app --reload
### 5. Check your location
GET /checkSafety?lat={latitude}&lon={longitude}
## Example
http://127.0.0.1:8000/checkSafety?lat=40.4259&lon=-86.9081

### Note
Built a FastAPI-based safety-check API. Used AI tools for scaffolding and debugging, and customized the logic for my use case.
