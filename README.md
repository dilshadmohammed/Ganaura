# Ganaura

Ganaura is a web application that transforms regular images and videos into anime style art using GAN (Generative Adversarial Network) technology.

![Ganaura LandingPage](https://github.com/munawir40/Ganaura/blob/main/Landin%20Page.jpeg)

## Project Overview

Ganaura leverages generative adverserial network to convert ordinary photos and videos into anime-style content. The application features:

- Image-to-anime conversion
- Video-to-anime transformation

## Tech Stack

The project is built using a three-tier architecture:

- **Frontend**: React with Vite for a fast, responsive user interface
- **Backend**: Django REST framework for user management and business logic
- **GAN Microservice**: FastAPI service that handles the actual image/video processing
- **Deep Learning**: TensorFlow for the GAN model implementation

## Project Structure

```
ganaura/
├── frontend/           # React Vite frontend application
├── backend/            # Django backend application
└── gan_microservice/   # FastAPI microservice for GAN processing
    ├── main.py         # FastAPI application entry point
    └── utils.py        # Utility functions for GAN processing
```

## Installation Guide

### Prerequisites

- Python 3.10+
- Node.js 22+
- npm or yarn
- TensorFlow 2.x
- CUDA-compatible GPU (recommended for faster processing)

### Step 1: Clone the Repository

```bash
git clone https://github.com/dilshadmohammed/Ganaura.git
cd Ganaura
```

### Step 2: Set Up the Backend (Django)

```bash
cd backend

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Start the Django server
python manage.py runserver
```

The backend will be available at http://localhost:8000/

### Step 3: Set Up the Frontend (React/Vite)

```bash
cd ../frontend

# Install dependencies
npm install
# or if you use yarn
yarn install

# Start the development server
npm run dev
# or
yarn dev
```

The frontend will be available at http://localhost:5173/

### Step 4: Set Up the GAN Microservice (FastAPI)

```bash
cd ../gan_microservice

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

```

The GAN microservice will be available at http://localhost:9000/
