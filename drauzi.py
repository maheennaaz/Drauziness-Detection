import json
import os
import sys
import threading
import time
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import messagebox, ttk

import cv2
import mediapipe as mp
import numpy as np
from pygame import mixer
from scipy.spatial import distance

# Import UI components with error handling
try:
    from data_export import (DataExporter, DrowsinessEvent, SessionData,
                             SessionReport)
    from ui_components import (AlertHistoryWidget, AnimatedProgressBar,
                               GradientButton, ModernFrame, StatusIndicator)
except ImportError as e:
    print(f"UI components import error: {e}")
    print("Please ensure ui_components.py and data_export.py are in the same directory")
    sys.exit(1)

class EnhancedDrowsinessDetector:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()  # Hide main window initially
        self.show_splash_screen()  # Show splash screen
        self.setup_window_properties()
        self.setup_detection()
        self.setup_data_tracking()
        self.setup_ui()

    def show_splash_screen(self):
        """Display a splash screen with fade-in effect and loading animation"""
        self.splash = tk.Toplevel()
        self.splash.title("Loading...")
        self.splash.configure(bg='#ffffff')
        self.splash.overrideredirect(True)  # Remove window decorations
        self.splash.attributes('-topmost', True)  # Keep on top

        # Center splash screen
        screen_width = self.splash.winfo_screenwidth()
        screen_height = self.splash.winfo_screenheight()
        splash_width = 400
        splash_height = 250
        x = (screen_width - splash_width) // 2
        y = (screen_height - splash_height) // 2
        self.splash.geometry(f"{splash_width}x{splash_height}+{x}+{y}")

        # Splash screen content
        splash_frame = ModernFrame(self.splash, gradient_colors=['#ffffff', '#f0f0f0'])
        splash_frame.pack(fill='both', expand=True)

        tk.Label(
            splash_frame,
            text="🧠 AI Drowsiness Detection",
            font=('Segoe UI', 18, 'bold'),
            fg='#25D366',  # WhatsApp green
            bg='#ffffff'
        ).pack(pady=30)

        tk.Label(
            splash_frame,
            text="Initializing System...",
            font=('Segoe UI', 12),
            fg='#333333',
            bg='#ffffff'
        ).pack(pady=10)

        # Loading animation (progress bar)
        loading_bar = AnimatedProgressBar(
            splash_frame,
            label="Loading",
            color='#25D366'
        )
        loading_bar.pack(fill='x', padx=20, pady=20)

        # Animate progress bar
        def animate_loading():
            for i in range(0, 100, 5):
                loading_bar.set_value(i)
                self.splash.update()
                time.sleep(0.15)

        # Fade-in effect
        def fade_in():
            alpha = 0.0
            self.splash.attributes('-alpha', alpha)
            while alpha < 1.0:
                alpha += 0.1
                self.splash.attributes('-alpha', alpha)
                self.splash.update()
                time.sleep(0.05)

        # Run animations and close splash
        threading.Thread(target=lambda: [fade_in(), animate_loading(), self.close_splash()], daemon=True).start()

    def close_splash(self):
        """Close splash screen and show main window"""
        self.splash.destroy()
        self.root.deiconify()  # Show main window

    def setup_window_properties(self):
        """Configure window properties for responsiveness"""
        self.root.title("AI Drowsiness Detection System")
        self.root.configure(bg='#ffffff')  # White background for WhatsApp/Instagram theme

        # Make window responsive
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Set initial size based on screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Use 90% of screen size or fixed max size
        window_width = min(int(screen_width * 0.9), 1400)
        window_height = min(int(screen_height * 0.9), 900)

        self.root.geometry(f"{window_width}x{window_height}")
        self.root.minsize(800, 600)  # Minimum size to ensure usability

    def setup_ui(self):
        """Initialize the modern white-themed UI with responsive design"""
        # Create main container with white background
        self.main_frame = ModernFrame(self.root, gradient_colors=['#ffffff', '#f0f0f0'])  # Light gradient
        self.main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Configure grid layout for main frame
        self.main_frame.grid_rowconfigure(0, weight=0)  # Header
        self.main_frame.grid_rowconfigure(1, weight=0)  # Control panel
        self.main_frame.grid_rowconfigure(2, weight=1)  # Content area
        self.main_frame.grid_columnconfigure(0, weight=3)  # Video/left panel
        self.main_frame.grid_columnconfigure(1, weight=1)  # Dashboard/right panel

        self.create_header()
        self.create_control_panel()
        self.create_content_area()
        self.create_settings_panel()

    def create_header(self):
        """Create the modern header section with white theme"""
        header_frame = tk.Frame(self.main_frame, bg='#f0f0f0', height=80)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", pady=(0, 10))
        header_frame.pack_propagate(False)

        # Title with modern typography
        title_label = tk.Label(
            header_frame,
            text="🧠 AI Drowsiness Detection System",
            font=('Segoe UI', 20, 'bold'),
            fg='#25D366',  # WhatsApp green
            bg='#f0f0f0'
        )
        title_label.pack(side='left', padx=20, pady=20)

        # Status indicators
        self.status_frame = tk.Frame(header_frame, bg='#f0f0f0')
        self.status_frame.pack(side='right', padx=20)

        self.camera_status = StatusIndicator(self.status_frame, "Camera", "offline")
        self.camera_status.pack(side='left', padx=10)

        self.detection_status = StatusIndicator(self.status_frame, "Detection", "offline")
        self.detection_status.pack(side='left', padx=10)

    def create_control_panel(self):
        """Create the control panel with modern buttons, excluding settings"""
        control_frame = ModernFrame(self.main_frame, gradient_colors=['#f0f0f0', '#e0e0e0'])
        control_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(0, 10))

        button_frame = tk.Frame(control_frame, bg='#f0f0f0')
        button_frame.pack(pady=10)

        self.start_btn = GradientButton(
            button_frame,
            text="🚀 Start Detection",
            command=self.start_detection,
            gradient_colors=['#25D366', '#128C7E']  # WhatsApp green gradient
        )
        self.start_btn.pack(side='left', padx=10)

        self.stop_btn = GradientButton(
            button_frame,
            text="⏹️ Stop Detection",
            command=self.stop_detection,
            gradient_colors=['#FF0000', '#CC0000']  # Red gradient
        )
        self.stop_btn.pack(side='left', padx=10)

        self.export_btn = GradientButton(
            button_frame,
            text="📁 Export Data",
            command=self.export_data,
            gradient_colors=['#00CED1', '#008B8B']  # Cyan gradient
        )
        self.export_btn.pack(side='left', padx=10)

    def create_content_area(self):
        """Create the main content area with video and dashboard"""
        # Video section
        video_frame = ModernFrame(self.main_frame, gradient_colors=['#f0f0f0', '#e0e0e0'])
        video_frame.grid(row=2, column=0, sticky="nsew", padx=(0, 10))
        video_frame.grid_rowconfigure(0, weight=1)  # Video display
        video_frame.grid_rowconfigure(1, weight=0)  # Metrics
        video_frame.grid_columnconfigure(0, weight=1)

        # Video display
        self.video_label = tk.Label(
            video_frame,
            text="📹 Video Feed Will Appear Here",
            font=('Segoe UI', 14),
            fg='#333333',  # Dark text for contrast
            bg='#ffffff'
        )
        self.video_label.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Real-time metrics below video
        metrics_frame = tk.Frame(video_frame, bg='#ffffff')
        metrics_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 10))

        self.ear_progress = AnimatedProgressBar(
            metrics_frame,
            label="Eye Aspect Ratio",
            color='#25D366'  # WhatsApp green
        )
        self.ear_progress.pack(fill='x', pady=5)

        self.mar_progress = AnimatedProgressBar(
            metrics_frame,
            label="Mouth Aspect Ratio",
            color='#FF9900'  # Orange for yawn detection
        )
        self.mar_progress.pack(fill='x', pady=5)

        self.alertness_progress = AnimatedProgressBar(
            metrics_frame,
            label="Alertness Level",
            color='#00CED1'  # Cyan
        )
        self.alertness_progress.pack(fill='x', pady=5)

        # Dashboard section
        dashboard_frame = ModernFrame(
            self.main_frame,
            gradient_colors=['#f0f0f0', '#e0e0e0']
        )
        dashboard_frame.grid(row=2, column=1, sticky="nsew")
        dashboard_frame.grid_rowconfigure(0, weight=0)  # Title
        dashboard_frame.grid_rowconfigure(1, weight=0)  # Session info
        dashboard_frame.grid_rowconfigure(2, weight=1)  # Alert history
        dashboard_frame.grid_columnconfigure(0, weight=1)

        # Dashboard title
        title = tk.Label(
            dashboard_frame,
            text="📊 Real-Time Analytics",
            font=('Segoe UI', 14, 'bold'),
            fg='#25D366',
            bg='#f0f0f0'
        )
        title.grid(row=0, column=0, sticky="nsew", pady=10)

        # Session info
        self.session_frame = tk.Frame(dashboard_frame, bg='#ffffff')
        self.session_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

        self.session_time_label = tk.Label(
            self.session_frame,
            text="Session Duration: 00:00:00",
            font=('Segoe UI', 10),
            fg='#333333',
            bg='#ffffff'
        )
        self.session_time_label.pack(anchor='w')

        self.drowsy_events_label = tk.Label(
            self.session_frame,
            text="Drowsiness Events: 0",
            font=('Segoe UI', 10),
            fg='#333333',
            bg='#ffffff'
        )
        self.drowsy_events_label.pack(anchor='w')

        self.alert_frequency_label = tk.Label(
            self.session_frame,
            text="Alert Frequency: 0/min",
            font=('Segoe UI', 10),
            fg='#333333',
            bg='#ffffff'
        )
        self.alert_frequency_label.pack(anchor='w')

        self.export_path_label = tk.Label(
            self.session_frame,
            text="Export Path: exports/",
            font=('Segoe UI', 10),
            fg='#333333',
            bg='#ffffff'
        )
        self.export_path_label.pack(anchor='w')

        # Alert history
        self.alert_history = AlertHistoryWidget(dashboard_frame)
        self.alert_history.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

    def create_settings_panel(self):
        """Create the settings panel with white theme"""
        self.settings_panel = ModernFrame(
            self.root,
            gradient_colors=['#f0f0f0', '#e0e0e0']
        )
        self.settings_panel.place(relx=1.0, rely=0.1, anchor='ne', x=-20, y=0)
        self.settings_panel.pack_forget()

        settings_title = tk.Label(
            self.settings_panel,
            text="⚙️ Detection Settings",
            font=('Segoe UI', 12, 'bold'),
            fg='#25D366',
            bg='#f0f0f0'
        )
        settings_title.pack(pady=10)

        # EAR Threshold
        tk.Label(
            self.settings_panel,
            text="EAR Threshold:",
            font=('Segoe UI', 9),
            fg='#333333',
            bg='#f0f0f0'
        ).pack(anchor='w', padx=10)

        self.ear_threshold_var = tk.DoubleVar(value=0.28)
        ear_scale = tk.Scale(
            self.settings_panel,
            from_=0.1,
            to=0.5,
            resolution=0.01,
            orient='horizontal',
            variable=self.ear_threshold_var,
            bg='#e0e0e0',
            fg='#333333',
            highlightthickness=0,
            length=200
        )
        ear_scale.pack(fill='x', padx=10, pady=5)

        # Blink Duration Threshold
        tk.Label(
            self.settings_panel,
            text="Blink Duration (seconds):",
            font=('Segoe UI', 9),
            fg='#333333',
            bg='#f0f0f0'
        ).pack(anchor='w', padx=10, pady=(10,0))

        self.blink_duration_var = tk.DoubleVar(value=0.4)
        blink_scale = tk.Scale(
            self.settings_panel,
            from_=0.1,
            to=2.0,
            resolution=0.1,
            orient='horizontal',
            variable=self.blink_duration_var,
            bg='#e0e0e0',
            fg='#333333',
            highlightthickness=0,
            length=200
        )
        blink_scale.pack(fill='x', padx=10, pady=5)

        # MAR Threshold for Yawn Detection
        tk.Label(
            self.settings_panel,
            text="MAR Threshold (Yawn):",
            font=('Segoe UI', 9),
            fg='#333333',
            bg='#f0f0f0'
        ).pack(anchor='w', padx=10, pady=(10,0))

        self.mar_threshold_var = tk.DoubleVar(value=0.6)
        mar_scale = tk.Scale(
            self.settings_panel,
            from_=0.2,
            to=1.0,
            resolution=0.01,
            orient='horizontal',
            variable=self.mar_threshold_var,
            bg='#e0e0e0',
            fg='#333333',
            highlightthickness=0,
            length=200
        )
        mar_scale.pack(fill='x', padx=10, pady=5)

        # Yawn Duration Threshold
        tk.Label(
            self.settings_panel,
            text="Yawn Duration (seconds):",
            font=('Segoe UI', 9),
            fg='#333333',
            bg='#f0f0f0'
        ).pack(anchor='w', padx=10, pady=(10,0))

        self.yawn_duration_var = tk.DoubleVar(value=0.6)
        yawn_scale = tk.Scale(
            self.settings_panel,
            from_=0.1,
            to=2.0,
            resolution=0.1,
            orient='horizontal',
            variable=self.yawn_duration_var,
            bg='#e0e0e0',
            fg='#333333',
            highlightthickness=0,
            length=200
        )
        yawn_scale.pack(fill='x', padx=10, pady=5)

        # Scarf Detection Sensitivity
        tk.Label(
            self.settings_panel,
            text="Scarf Detection Sensitivity:",
            font=('Segoe UI', 9),
            fg='#333333',
            bg='#f0f0f0'
        ).pack(anchor='w', padx=10, pady=(10,0))

        self.scarf_sensitivity_var = tk.DoubleVar(value=0.6)
        scarf_scale = tk.Scale(
            self.settings_panel,
            from_=0.1,
            to=1.0,
            resolution=0.1,
            orient='horizontal',
            variable=self.scarf_sensitivity_var,
            bg='#e0e0e0',
            fg='#333333',
            highlightthickness=0,
            length=200
        )
        scarf_scale.pack(fill='x', padx=10, pady=5)

        # Apply button
        apply_btn = GradientButton(
            self.settings_panel,
            text="Apply Settings",
            command=self.apply_settings,
            gradient_colors=['#25D366', '#128C7E']
        )
        apply_btn.pack(pady=10, padx=10, fill='x')

        self.settings_visible = False

    def setup_detection(self):
        """Initialize detection components with moderate sensitivity"""
        try:
            mixer.init()
        except pygame.error as e:
            print(f"Audio initialization failed: {e}")
            print("Continuing without audio alerts...")
            self.audio_disabled = True
        else:
            self.audio_disabled = False

        # Use music.wav from the same directory as this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.audio_file = os.path.join(script_dir, "music.wav")

        if not os.path.exists(self.audio_file):
            try:
                import pygame
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                sound = pygame.mixer.Sound(buffer=np.sin(2 * np.pi * np.arange(22050) * 440 / 22050).astype(np.float32))
                sound.save(self.audio_file)
            except Exception as e:
                print(f"Could not create alert sound file: {e}")

        # Detection parameters (moderate sensitivity)
        self.EAR_THRESHOLD = 0.28  # Slightly higher for moderate eye closure detection
        self.BLINK_DURATION_THRESHOLD = 0.4  # Moderate duration for blinks
        self.MAR_THRESHOLD = 0.6  # Slightly higher for yawn detection
        self.YAWN_DURATION_THRESHOLD = 0.6  # Moderate duration for yawns
        self.SCARF_SENSITIVITY = 0.6  # Moderate delay for scarf detection

        # Initialize MediaPipe Face Mesh and Face Detection
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        self.mp_face_detection = mp.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(min_detection_confidence=0.5)

        self.LEFT_EYE_INDICES = [362, 385, 387, 263, 373, 380]
        self.RIGHT_EYE_INDICES = [33, 160, 158, 133, 153, 144]
        self.MOUTH_INDICES = [61, 291, 0, 17]  # Top, bottom, left, right lip points

        self.detection_active = False
        self.cap = None
        self.is_alert_playing = False
        self.blink_start_time = None
        self.yawn_start_time = None
        self.scarf_alert_time = None
        self.last_alert_type = None  # Track the last alert type to prevent re-triggering

    def setup_data_tracking(self):
        """Initialize data tracking for analytics"""
        self.session_start_time = None
        self.drowsiness_events = []
        self.alert_history_data = []
        self.current_ear = 0.0
        self.current_mar = 0.0
        self.alertness_level = 100.0
        self.data_collector = DataExporter()

    def eye_aspect_ratio(self, eye_landmarks):
        """Calculate eye aspect ratio from landmarks"""
        A = distance.euclidean(eye_landmarks[1], eye_landmarks[5])
        B = distance.euclidean(eye_landmarks[2], eye_landmarks[4])
        C = distance.euclidean(eye_landmarks[0], eye_landmarks[3])
        return (A + B) / (2.0 * C)

    def mouth_aspect_ratio(self, mouth_landmarks):
        """Calculate mouth aspect ratio for yawn detection"""
        A = distance.euclidean(mouth_landmarks[0], mouth_landmarks[1])  # Vertical distance (top to bottom)
        B = distance.euclidean(mouth_landmarks[2], mouth_landmarks[3])  # Horizontal distance (left to right)
        return A / B if B != 0 else 0.0

    def detect_scarf(self, frame, results):
        """Detect if a scarf is covering the face"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_results = self.face_detection.process(rgb_frame)
        if not face_results.detections:
            if self.scarf_alert_time is None:
                self.scarf_alert_time = time.time()
            scarf_duration = time.time() - self.scarf_alert_time
            if scarf_duration > self.SCARF_SENSITIVITY:
                return True, "Scarf Covering Face - ALERT!"
        else:
            self.scarf_alert_time = None
            return False, ""
        return False, ""

    def start_detection(self):
        """Start the drowsiness detection"""
        if self.detection_active:
            return

        try:
            print("Attempting to open camera (index 0)...")
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                print("ERROR: Could not open camera. Trying alternative camera index...")
                # Try other camera indices
                for i in range(1, 5):
                    print(f"Trying camera index {i}...")
                    self.cap = cv2.VideoCapture(i)
                    if self.cap.isOpened():
                        print(f"Camera found at index {i}")
                        break
                else:
                    messagebox.showerror("Error", "Could not open camera. Please check if your webcam is connected and not in use by another application.")
                    print("No camera found on any index")
                    return

            print("Camera opened successfully")

            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

            if os.path.exists(self.audio_file):
                try:
                    mixer.music.load(self.audio_file)
                    print(f"Audio file loaded successfully: {self.audio_file}")
                except Exception as e:
                    print(f"Audio loading warning: {e}")
            else:
                print(f"Audio file not found: {self.audio_file}")

            self.detection_active = True
            self.session_start_time = datetime.now()
            self.drowsiness_events = []
            self.alert_history_data = []

            self.camera_status.set_status("online")
            self.detection_status.set_status("online")

            self.detection_thread = threading.Thread(target=self.detection_loop, daemon=True)
            self.detection_thread.start()
            self.ui_update_thread = threading.Thread(target=self.update_ui_loop, daemon=True)
            self.ui_update_thread.start()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to start detection: {str(e)}")

    def stop_detection(self):
        """Stop the drowsiness detection"""
        self.detection_active = False

        if self.cap:
            self.cap.release()

        if self.is_alert_playing:
            try:
                mixer.music.stop()
                self.is_alert_playing = False
                self.last_alert_type = None
            except Exception as e:
                print(f"Audio stop error: {e}")

        self.camera_status.set_status("offline")
        self.detection_status.set_status("offline")

        self.video_label.configure(
            text="📹 Video Feed Stopped",
            image=""
        )

    def detection_loop(self):
        """Main detection loop running in separate thread"""
        while self.detection_active and self.cap:
            ret, frame = self.cap.read()
            if not ret:
                break

            # Convert to RGB for processing
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb_frame.flags.writeable = False

            # Process frame for face mesh
            results = self.face_mesh.process(rgb_frame)

            # Default values
            ear = 0.0
            mar = 0.0
            alert_text = "AWAKE"
            current_alert_type = None

            # Stop any playing alert sound by default
            if self.is_alert_playing:
                try:
                    mixer.music.stop()
                    self.is_alert_playing = False
                except Exception as e:
                    print(f"Audio stop error: {e}")

            # Check for scarf covering face
            scarf_detected, scarf_alert = self.detect_scarf(frame, results)

            if results.multi_face_landmarks and not scarf_detected:
                for face_landmarks in results.multi_face_landmarks:
                    h, w = frame.shape[:2]

                    # Extract eye coordinates
                    left_eye = np.array([
                        [int(face_landmarks.landmark[idx].x * w),
                         int(face_landmarks.landmark[idx].y * h)]
                        for idx in self.LEFT_EYE_INDICES
                    ])

                    right_eye = np.array([
                        [int(face_landmarks.landmark[idx].x * w),
                         int(face_landmarks.landmark[idx].y * h)]
                        for idx in self.RIGHT_EYE_INDICES
                    ])

                    # Extract mouth coordinates
                    mouth = np.array([
                        [int(face_landmarks.landmark[idx].x * w),
                         int(face_landmarks.landmark[idx].y * h)]
                        for idx in self.MOUTH_INDICES
                    ])

                    # Calculate EAR and MAR
                    left_ear = self.eye_aspect_ratio(left_eye)
                    right_ear = self.eye_aspect_ratio(right_eye)
                    ear = (left_ear + right_ear) / 2.0
                    mar = self.mouth_aspect_ratio(mouth)

                    # Draw eye contours (green if open, red if closed)
                    eye_color = (0, 255, 0) if ear >= self.EAR_THRESHOLD else (0, 0, 255)  # Green for open, red for closed
                    cv2.polylines(frame, [left_eye], True, eye_color, 2)
                    cv2.polylines(frame, [right_eye], True, eye_color, 2)

                    # Drowsiness detection (eyes)
                    if ear < self.EAR_THRESHOLD:
                        if self.blink_start_time is None:
                            self.blink_start_time = time.time()

                        blink_duration = time.time() - self.blink_start_time
                        if blink_duration > self.BLINK_DURATION_THRESHOLD:
                            alert_text = "DROWSY - ALERT! (Eyes)"
                            current_alert_type = "eye_drowsiness_detected"

                            current_time = datetime.now()
                            self.drowsiness_events.append(DrowsinessEvent(
                                timestamp=current_time,
                                ear_value=ear,
                                event_type="eye_drowsiness_detected",
                                duration_seconds=blink_duration
                            ))
                            self.alert_history_data.append({
                                'time': current_time.strftime("%H:%M:%S"),
                                'type': 'Eye Drowsiness Detected',
                                'ear': ear
                            })

                            if not self.is_alert_playing and os.path.exists(self.audio_file) and self.last_alert_type != current_alert_type:
                                try:
                                    mixer.music.play(-1)
                                    self.is_alert_playing = True
                                    self.last_alert_type = current_alert_type
                                except Exception as e:
                                    print(f"Audio error: {e}")
                    else:
                        self.blink_start_time = None

                    # Yawn detection (mouth)
                    if mar > self.MAR_THRESHOLD:
                        if self.yawn_start_time is None:
                            self.yawn_start_time = time.time()

                        yawn_duration = time.time() - self.yawn_start_time
                        if yawn_duration > self.YAWN_DURATION_THRESHOLD:
                            alert_text = "YAWN DETECTED - ALERT!"
                            current_alert_type = "yawn_detected"

                            current_time = datetime.now()
                            self.drowsiness_events.append(DrowsinessEvent(
                                timestamp=current_time,
                                ear_value=mar,
                                event_type="yawn_detected",
                                duration_seconds=yawn_duration
                            ))
                            self.alert_history_data.append({
                                'time': current_time.strftime("%H:%M:%S"),
                                'type': 'Yawn Detected',
                                'ear': mar
                            })

                            if not self.is_alert_playing and os.path.exists(self.audio_file) and self.last_alert_type != current_alert_type:
                                try:
                                    mixer.music.play(-1)
                                    self.is_alert_playing = True
                                    self.last_alert_type = current_alert_type
                                except Exception as e:
                                    print(f"Audio error: {e}")
                    else:
                        self.yawn_start_time = None

            elif scarf_detected:
                alert_text = scarf_alert
                current_alert_type = "scarf_detected"
                current_time = datetime.now()
                self.drowsiness_events.append(DrowsinessEvent(
                    timestamp=current_time,
                    ear_value=0.0,
                    event_type="scarf_detected",
                    duration_seconds=0.0
                ))
                self.alert_history_data.append({
                    'time': current_time.strftime("%H:%M:%S"),
                    'type': 'Scarf Detected',
                    'ear': 0.0
                })

                if not self.is_alert_playing and os.path.exists(self.audio_file) and self.last_alert_type != current_alert_type:
                    try:
                        mixer.music.play(-1)
                        self.is_alert_playing = True
                        self.last_alert_type = current_alert_type
                    except Exception as e:
                        print(f"Audio error: {e}")

            # Reset alert type and stop sound if no drowsiness conditions are met
            if ear >= self.EAR_THRESHOLD and mar <= self.MAR_THRESHOLD and not scarf_detected:
                self.last_alert_type = None
                if self.is_alert_playing:
                    try:
                        mixer.music.stop()
                        self.is_alert_playing = False
                    except Exception as e:
                        print(f"Audio stop error: {e}")

            # Stop sound if no face is detected (outside scarf detection)
            if not results.multi_face_landmarks and not scarf_detected:
                self.last_alert_type = None
                if self.is_alert_playing:
                    try:
                        mixer.music.stop()
                        self.is_alert_playing = False
                    except Exception as e:
                        print(f"Audio stop error: {e}")

            self.current_ear = ear
            self.current_mar = mar
            self.alertness_level = max(0, min(100, (ear / 0.3) * 100 if not scarf_detected else 0))

            # Display original frame with eye contours
            frame = cv2.resize(frame, (640, 480))
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = tk.PhotoImage(master=self.root, data=cv2.imencode('.ppm', frame_rgb)[1].tobytes())

            self.root.after(0, lambda: self.update_video_display(img, alert_text))

            time.sleep(0.03)

    def update_video_display(self, frame_pil, alert_text):
        """Update the video display in the UI with alert text"""
        if hasattr(self, 'video_label'):
            self.video_label.configure(image=frame_pil, text=alert_text, compound='top')
            self.video_label.image = frame_pil

    def update_ui_loop(self):
        """Update UI elements periodically"""
        while self.detection_active:
            self.root.after(0, self.update_dashboard)
            time.sleep(1)

    def update_dashboard(self):
        """Update the dashboard with current statistics"""
        if not self.session_start_time:
            return

        duration = datetime.now() - self.session_start_time
        duration_str = str(duration).split('.')[0]
        self.session_time_label.configure(text=f"Session Duration: {duration_str}")
        self.drowsy_events_label.configure(text=f"Drowsiness Events: {len(self.drowsiness_events)}")
        minutes = max(1, duration.total_seconds() / 60)
        frequency = len(self.drowsiness_events) / minutes
        self.alert_frequency_label.configure(text=f"Alert Frequency: {frequency:.1f}/min")
        self.ear_progress.set_value(self.current_ear * 100)
        self.mar_progress.set_value(self.current_mar * 100)
        self.alertness_progress.set_value(self.alertness_level)
        self.alert_history.update_history(self.alert_history_data[-10:])

    def apply_settings(self):
        """Apply the new settings"""
        self.EAR_THRESHOLD = self.ear_threshold_var.get()
        self.BLINK_DURATION_THRESHOLD = self.blink_duration_var.get()
        self.MAR_THRESHOLD = self.mar_threshold_var.get()
        self.YAWN_DURATION_THRESHOLD = self.yawn_duration_var.get()
        self.SCARF_SENSITIVITY = self.scarf_sensitivity_var.get()

        messagebox.showinfo("Settings", "Settings applied successfully!")

    def export_data(self):
        """Export session data and show result"""
        if not self.session_start_time:
            messagebox.showwarning("Export", "No active session to export!")
            return

        session_data = SessionData(
            session_id=self.data_collector.generate_session_id(),
            start_time=self.session_start_time,
            end_time=datetime.now(),
            duration_seconds=(datetime.now() - self.session_start_time).total_seconds(),
            total_drowsiness_events=len(self.drowsiness_events),
            alert_frequency_per_minute=len(self.drowsiness_events) / max((datetime.now() - self.session_start_time).total_seconds() / 60, 1),
            average_ear=sum(event.ear_value for event in self.drowsiness_events if event.event_type == "eye_drowsiness_detected") / max(len(self.drowsiness_events), 1),
            min_ear=min((event.ear_value for event in self.drowsiness_events if event.event_type == "eye_drowsiness_detected"), default=0.0),
            max_ear=max((event.ear_value for event in self.drowsiness_events if event.event_type == "eye_drowsiness_detected"), default=0.0),
            average_alertness=self.alertness_level,
            settings_used={
                "EAR_THRESHOLD": self.EAR_THRESHOLD,
                "BLINK_DURATION_THRESHOLD": self.BLINK_DURATION_THRESHOLD,
                "MAR_THRESHOLD": self.MAR_THRESHOLD,
                "YAWN_DURATION_THRESHOLD": self.YAWN_DURATION_THRESHOLD,
                "SCARF_SENSITIVITY": self.SCARF_SENSITIVITY
            }
        )

        success, message = self.data_collector.export_to_csv(session_data, self.drowsiness_events)
        if success:
            messagebox.showinfo("Export", message)
        else:
            messagebox.showerror("Export", message)

    def on_closing(self):
        """Handle application closing"""
        self.stop_detection()
        if hasattr(self, 'face_mesh'):
            self.face_mesh.close()
        if hasattr(self, 'face_detection'):
            self.face_detection.close()
        mixer.quit()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = EnhancedDrowsinessDetector(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
