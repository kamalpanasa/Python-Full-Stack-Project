# TypeMaster

TypeMaster is a full-stack web application that helps users practice and improve their typing skills by measuring speed (WPM), accuracy, and mistakes in real-time. The app provides random passages of different difficulty levels for typing tests, tracks each attempt, and generates detailed results. Users can create accounts, compete on a global leaderboard, and monitor their performance history to see progress over time.

## Features

- User authentication and profiles  
- Random text generation with difficulty levels  
- Real-time timer and WPM/accuracy calculation  
- Leaderboard showcasing top performers  
- Progress tracking and analytics for each user  
- Modern UI powered by Streamlit frontend  
- REST API powered by FastAPI backend  

---

## Project Structure
```
TypeMaster/
|
|---src/                # core application logic
|   |---logic.py        # Buisiness logic and task
operations
|   |---db.py           # Database operations
|
|---api/                # Backend API
|   |---main.py         # FastAPI endpoints
|
|---frontend/           # Frontend application
|   |---app.py          # Streamlit web interface
|
|---requirements.txt    # Python Dependencies
|
|---README.md           # Project documentation
|
|---.env                # Python variables
```
## Quick Start

### Prerequisites

- Python 3.8 or higher
- A Supabase account
- Git(Push, Cloning)

## 1. Clone or Download the Project
### Option 1: Clone with Git
git clone <https://github.com/kamalpanasa/Python-Full-Stack-Project.git>

### Option 2: Download and extract the ZIP file

## 2. Install Dependencies
### Install all required Python packages
pip install -r requirements.txt

## 3. Set Up Supabase Database

1.Create a Supabase Project:

2.Create the Tasks Table:

- Go to the SQL Editor in your Supabase dashboard
- Run this SQL command:

``` sql
create table users (
    id uuid primary key default gen_random_uuid(),
    username varchar(50) unique not null,
    email varchar(100) unique not null,
    full_name varchar(100),
    created_at timestamp default now()
);

```

3. **Get Your Credentials:

## 4. Configure Environment Variables

1. Create a `.env` file in the project root

2. Add your Supabase credentials to `.env` :
SUPABASE_URL = "https://gekitershzcibxxceuus.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imdla2l0ZXJzaHpjaWJ4eGNldXVzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg2ODY4NzUsImV4cCI6MjA3NDI2Mjg3NX0.EYdx1rKEy5Kt0rhPc0ZXY-1q07ZTJsOEPgTZ3ktmxvY"

## 5. Run the application

### Streamlit Frontend
streamlit run frontend/app.py

The app will open in your browser at `http://localhost:5000`

### FastAPI Backend

cd api
python main.py

The API will be available at `http://localhost:8000`

### How to Use

- **Frontend** : React.js + Tailwind CSS (interactive UI)

- **Backend** : Fast API (Python REST API framework)

- **Database** : Supabase (PostgreSQL with Auth & Storage)

- **Language** : Python 3.8+

## Key Components

1. **`src/db.py`**: Database operations
    - Handles all CRUD operations with Supabase

2. **`src/logic.py`**: Business logic
    - Task validation and processing


## Troubleshooting

## Common Issues

1. **"Module not found" errors**
    - Make sure you've installed all dependencies: `pip install requirements.txt`
    - Check that you're running commands from the correct directory

## Future Enhancements

Ideas for extending this project:


## Support 

If you encounter any issues or have questions:
- Contact : 1234567890
- Mail : panasakamal92@gmail.com

