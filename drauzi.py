import json
import os
import sys
import threading
import time
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import messagebox, ttk

print("STARTUP: imports beginning...", flush=True)

print("  importing cv2...", flush=True)
import cv2
print("  cv2 imported", flush=True)

print("  importing mediapipe...", flush=True)
try:
    import mediapipe as mp
    print("  mediapipe imported", flush=True)
except Exception as e:
    print(f"  ERROR importing mediapipe: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("  importing numpy...", flush=True)
import numpy as np
print("  numpy imported", flush=True)

print("  importing pygame...", flush=True)
import pygame
print("  pygame imported", flush=True)

print("  importing pygame.mixer...", flush=True)
from pygame import mixer
print("  mixer imported", flush=True)

print("  importing scipy...", flush=True)
from scipy.spatial import distance
print("  scipy imported", flush=True)

print("STARTUP: modules imported successfully", flush=True)

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
        print("Initializing EnhancedDrowsinessDetector...", flush=True)
        self.root = root
        # We no longer use the splash screen; show the main window immediately
        # self.root.withdraw()  # Hide main window initially
        # print("Showing splash screen...", flush=True)
        # self.show_splash_screen()  # Show splash screen
        self.root.deiconify()
        print("Setting up window properties...", flush=True)
        self.setup_window_properties()
        print("(Deferred) setting up detection will occur when detection starts", flush=True)
        self.detection_initialized = False
        print("Setting up data tracking...", flush=True)
        self.setup_data_tracking()
        print("Setting up UI...", flush=True)
        self.setup_ui()
        print("Initialization complete!", flush=True)

    # splash screen code removed because it was preventing the main window from appearing
    # def show_splash_screen(self):
    #     """Display a splash screen with fade-in effect and loading animation"""
    #     ... (splash screen disabled) ...


    def close_splash(self):
        """Close splash screen and show main window"""
        print("Closing splash screen...", flush=True)
        self.splash.destroy()
        print("Showing main window...", flush=True)
        self.root.deiconify()  # Show main window
        print("Main window should now be visible", flush=True)

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
        except Exception as e:
            # audio initialization may fail if no working audio device is available
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

        # ensure detection components are initialized lazily
        if not getattr(self, 'detection_initialized', False):
            print("Initializing detection components before starting...", flush=True)
            try:
                self.setup_detection()
            except Exception as e:
                print(f"ERROR during setup_detection: {e}", flush=True)
                import traceback
                traceback.print_exc()
                messagebox.showerror("Initialization Error", f"Failed to initialize detection components: {e}")
                return
            self.detection_initialized = True

        try:
            print("Attempting to open camera...", flush=True)
            
            # Try simple camera open first
            self.cap = None
            for idx in range(5):
                print(f"Trying camera index {idx}...", flush=True)
                try:
                    cap_candidate = cv2.VideoCapture(idx)
                    if cap_candidate.isOpened():
                        print(f"Camera opened at index {idx}", flush=True)
                        self.cap = cap_candidate
                        break
                    else:
                        cap_candidate.release()
                except Exception as e:
                    print(f"Failed at index {idx}: {e}", flush=True)
            
            # If no camera found, offer demo mode
            if self.cap is None or not self.cap.isOpened():
                print("\nNo camera found. Offering demo mode...", flush=True)
                result = messagebox.askyesno(
                    "Camera Offline",
                    "Camera could not be accessed.\n\n"
                    "Would you like to run in DEMO MODE?\n"
                    "(Demo mode simulates alerts without actual camera input)\n\n"
                    "Yes = Continue in demo mode\n"
                    "No = Cancel"
                )
                if not result:
                    print("User cancelled. Stopping detection.", flush=True)
                    return
                
                # Run in demo mode
                print("Starting in demo mode...", flush=True)
                self.detection_active = True
                self.session_start_time = datetime.now()
                self.drowsiness_events = []
                self.alert_history_data = []
                
                self.camera_status.set_status("offline (demo)")
                self.detection_status.set_status("online")
                
                self.video_label.configure(text="📹 DEMO MODE (No Camera)")
                
                # Start demo thread instead
                self.detection_thread = threading.Thread(target=self.demo_loop, daemon=True)
                self.detection_thread.start()
                self.ui_update_thread = threading.Thread(target=self.update_ui_loop, daemon=True)
                self.ui_update_thread.start()
                return
            
            # Camera found - proceed normally
            print("Camera opened successfully", flush=True)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

            if os.path.exists(self.audio_file):
                try:
                    mixer.music.load(self.audio_file)
                    print(f"Audio file loaded successfully: {self.audio_file}", flush=True)
                except Exception as e:
                    print(f"Audio loading warning: {e}", flush=True)
            else:
                print(f"Audio file not found: {self.audio_file}", flush=True)

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
            print(f"Exception in start_detection: {e}", flush=True)

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

    def demo_loop(self):
        """Simulate drowsiness detection without a camera (for testing)"""
        try:
            import random
            blink_count = 0
            alert_threshold = 3
            
            while self.detection_active:
                # Simulate random blinks/yawns
                if random.random() < 0.1:  # 10% chance each iteration
                    blink_count += 1
                    if blink_count >= alert_threshold:
                        # Simulate an alert
                        current_time = datetime.now()
                        self.drowsiness_events.append(DrowsinessEvent(
                            timestamp=current_time,
                            ear_value=0.15,  # Simulated closed eyes
                            event_type="demo_drowsiness",
                            duration_seconds=0.5
                        ))
                        self.alert_history_data.append({
                            'time': current_time.strftime("%H:%M:%S"),
                            'type': 'Demo Alert',
                            'ear': 0.15
                        })
                        
                        # Play alert if available
                        if not self.audio_disabled and os.path.exists(self.audio_file):
                            try:
                                if not self.is_alert_playing:
                                    mixer.music.play(-1)
                                    self.is_alert_playing = True
                            except Exception as e:
                                print(f"Demo: could not play alert: {e}")
                        
                        blink_count = 0
                
                # Update UI indicators
                self.current_ear = 0.3 + random.random() * 0.2
                self.current_mar = 0.5 + random.random() * 0.2
                self.alertness_level = max(0, min(100, 100 - (blink_count * 20)))
                
                time.sleep(0.5)
        except Exception as e:
            print(f"Exception in demo_loop: {e}", flush=True)
            self.detection_active = False
            self.camera_status.set_status("offline")
            self.detection_status.set_status("offline")

    def detection_loop(self):
        """Main detection loop running in separate thread"""
        try:
            while self.detection_active and self.cap:
                ret, frame = self.cap.read()
                if not ret:
                    break

                # Convert to RGB for processing
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                rgb_frame.flags.writeable = False

                # Process frame for face mesh
                results = self.face_mesh.process(rgb_frame)
        except Exception as e:
            print(f"Exception in detection_loop: {e}", flush=True)
            import traceback
            traceback.print_exc()
            # stop detection to avoid repeated errors
            self.detection_active = False
            self.camera_status.set_status("offline")
            self.detection_status.set_status("offline")
            messagebox.showerror("Detection Error", f"An error occurred during detection: {e}")
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
    print("Starting application...", flush=True)
    try:
        root = tk.Tk()
        print("Tkinter window created", flush=True)
        app = EnhancedDrowsinessDetector(root)
        print("App initialized, showing window...", flush=True)
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        try:
            root.mainloop()
        except Exception as e2:
            # On Windows running from a closed console you can get WinError 6
            # (invalid handle) when the underlying Tk event loop tries to write to
            # stdout/stderr.  Treat this as a normal shutdown instead of an error.
            if isinstance(e2, OSError) and getattr(e2, 'winerror', None) == 6:
                print(
                    "mainloop terminated due to invalid handle (probably the console was closed)",
                    flush=True
                )
            else:
                print(f"ERROR in mainloop: {e2}", flush=True)
                import traceback as _tb
                _tb.print_exc()
        finally:
            print("mainloop finished", flush=True)
        print("Main loop exited", flush=True)
    except Exception as e:
        # Sometimes when the app is terminated by closing the console on Windows
        # Tkinter may raise "[WinError 6] The handle is invalid".  The inner
        # handler should catch this, but in case it propagates we just ignore it
        # so the program exits cleanly.
        if isinstance(e, OSError) and getattr(e, 'winerror', None) == 6:
            print("Exiting due to invalid handle (WinError 6); this is harmless.", flush=True)
        else:
            print(f"ERROR: {e}", flush=True)
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("STARTUP: __main__ block reached, calling main()...", flush=True)
    main()
