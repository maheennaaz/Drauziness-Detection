# Project Summary
The Enhanced AI Drowsiness Detection System is a modern application designed to monitor driver alertness through video analysis. Utilizing OpenCV for video processing, MediaPipe for facial landmark detection, and pygame for audio alerts, this project aims to prevent drowsiness-related accidents by providing real-time feedback and alerts to users. The application features a visually appealing user interface that enhances user experience while maintaining core functionalities.

# Project Module Description
- **enhanced_drowsiness_detector.py**: Main application that integrates video processing, drowsiness detection logic, and user interface.
- **ui_components.py**: Custom UI elements designed to provide an attractive and responsive user interface.
- **create_sample_audio.py**: Script to generate a sample audio file for alerts.
- **requirements.txt**: Lists all necessary dependencies for the project.
- **README.md**: Documentation providing setup instructions and feature descriptions.

# Directory Tree
```
.
├── README.md                 # Comprehensive documentation
├── create_sample_audio.py    # Script to create sample audio file
├── enhanced_drowsiness_detector.py  # Main application code
├── music.wav                 # Sample audio alert file
├── requirements.txt          # Required Python packages
└── ui_components.py          # Custom UI components
```

# File Description Inventory
- **README.md**: Provides an overview, installation instructions, and usage guidelines for the application.
- **create_sample_audio.py**: Generates a simple beep sound saved as a WAV file for use as an alert.
- **enhanced_drowsiness_detector.py**: Contains the main logic for detecting drowsiness and managing the user interface.
- **music.wav**: Audio file used for alert notifications during drowsiness detection.
- **requirements.txt**: Specifies required libraries including OpenCV, MediaPipe, NumPy, pygame, and SciPy.

# Technology Stack
- **Python**: Programming language used for development.
- **OpenCV**: Library for computer vision tasks.
- **MediaPipe**: Framework for building multimodal applied machine learning pipelines.
- **pygame**: Library for writing video games, used here for audio playback.
- **NumPy**: Library for numerical computations.
- **SciPy**: Library for scientific and technical computing.
- **tkinter**: Built-in library for creating GUI applications in Python.

# Usage
1. Install dependencies:
   ```bash
   python -m venv venv
venv\Scripts\activate

   pip install -r req.txt
   ```
2. Create the sample audio file (if not already created):
   ```bash
   python create_sample_audio.py
   ```
3. Run the application:
   ```bash
   &"C:\Users\moham\Downloads\drauzy-main\.venv\Scripts\python.exe" "c:\Users\moham\Downloads\drauzy-main\drauzy-main\drauzi.py"
   ```
