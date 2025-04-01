# Ganaura

Ganaura is a web application that transforms regular images and videos into anime style art using GAN (Generative Adversarial Network) technology.

![Ganaura LandingPage](assets/landing_page.jpeg)

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
- **Video Processing**: FFmpeg
- **Image Processing**: OpenCV
- **Cloud Storage**: Digital ocean spaces

## Project Structure

```
ganaura/
├── frontend/               # React Vite frontend application
├── backend/                # Django backend application
    └── generation_service/ # Django app for gan related route
    └── user/               # Django app for user auth
├── gan_microservice/       # FastAPI microservice for GAN processing
└── gan_model/              # Gan model training files
    └── dataset/            # Dataset for gan training
        └── style
        └── real_photo        
    └── inputs/             # Sample inputs for inference
        └── imgs
        └── videos        
```

## Installation Guide

### Prerequisites

- Python 3.10+
- Node.js 22+
- npm
- TensorFlow 2.x
- CUDA-compatible GPU (recommended for faster processing)
- FFmpeg

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
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py makemigrations
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

# Start the development server
npm run dev

```

The frontend will be available at http://localhost:5173/

### Step 4: Set Up the GAN Microservice (FastAPI)

```bash
cd ../gan_microservice

# Create a virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the development server
python main.py

```

The GAN microservice will be available at http://localhost:9000/

## For GAN training
```bash
cd gan_model

# Install dependencies
pip install -r requirements.txt

# Download the dataset
# (Make sure to place it according to the project structure)
# https://drive.google.com/drive/folders/19J-3UqEoSwqAyCcOQB9ZtDnRCLyTO9bC?usp=drive_link

# Start training
python Ganaura_train.py
```


## Sample Input vs Output

### Image 1
<table>
  <tr>
    <td><b>Input</b></td>
    <td><b>Output</b></td>
  </tr>
  <tr>
    <td><img src="assets/imgs/sample_inputs/img1.jpeg" width="300"></td>
    <td><img src="assets/imgs/sample_outputs/img1.jpeg" width="300"></td>
  </tr>
</table>

### Image 2
<table>
  <tr>
    <td><b>Input</b></td>
    <td><b>Output</b></td>
  </tr>
  <tr>
    <td><img src="assets/imgs/sample_inputs/img2.jpeg" width="300"></td>
    <td><img src="assets/imgs/sample_outputs/img2.jpeg" width="300"></td>
  </tr>
</table>

### Image 3
<table>
  <tr>
    <td><b>Input</b></td>
    <td><b>Output</b></td>
  </tr>
  <tr>
    <td><img src="assets/imgs/sample_inputs/img3.jpeg" width="300"></td>
    <td><img src="assets/imgs/sample_outputs/img3.jpeg" width="300"></td>
  </tr>
</table>

### Image 4
<table>
  <tr>
    <td><b>Input</b></td>
    <td><b>Output</b></td>
  </tr>
  <tr>
    <td><img src="assets/imgs/sample_inputs/img4.jpeg" width="300"></td>
    <td><img src="assets/imgs/sample_outputs/img4.jpeg" width="300"></td>
  </tr>
</table>
