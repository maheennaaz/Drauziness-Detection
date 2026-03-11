import math
import time
import tkinter as tk
from datetime import datetime
from tkinter import ttk
from typing import List, Optional, Tuple


class ModernFrame(tk.Frame):
    """A modern frame with gradient background effect"""
    def __init__(self, parent, gradient_colors: Optional[List[str]] = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.gradient_colors = gradient_colors or ['#ffffff', '#f0f0f0']  # White theme
        self.configure(bg=self.gradient_colors[0])
        self.canvas = None
        self.bind("<Configure>", self._on_resize)

    def _on_resize(self, event):
        """Handle frame resizing"""
        if self.canvas:
            self._draw_gradient()

    def _draw_gradient(self):
        """Draw gradient background"""
        width = self.winfo_width()
        height = self.winfo_height()

        if width <= 1 or height <= 1:
            return

        self.canvas.delete("gradient")

        r1, g1, b1 = self.hex_to_rgb(self.gradient_colors[0])
        r2, g2, b2 = self.hex_to_rgb(self.gradient_colors[-1])

        for i in range(height):
            ratio = i / height
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.canvas.create_line(0, i, width, i, fill=color, tags="gradient")

    def create_gradient_canvas(self, width: int, height: int) -> tk.Canvas:
        """Create a canvas with gradient background"""
        self.canvas = tk.Canvas(
            self,
            width=width,
            height=height,
            highlightthickness=0,
            bd=0
        )
        self._draw_gradient()
        return self.canvas

    @staticmethod
    def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

class GradientButton(tk.Button):
    """A modern button with gradient background and hover effects"""
    def __init__(self, parent, text: str = "", command=None,
                 gradient_colors: Optional[List[str]] = None,
                 tooltip: Optional[str] = None, **kwargs):
        self.gradient_colors = gradient_colors or ['#25D366', '#128C7E']  # WhatsApp green
        self.hover_colors = [self.lighten_color(c, 0.2) for c in self.gradient_colors]
        self.default_colors = self.gradient_colors
        self.tooltip = tooltip
        self.tooltip_window = None

        super().__init__(
            parent,
            text=text,
            command=command,
            bg=self.gradient_colors[0],
            fg='white',
            font=('Segoe UI', 10, 'bold'),
            relief='flat',
            borderwidth=0,
            padx=20,
            pady=10,
            cursor='hand2',
            **kwargs
        )

        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

        if self.tooltip:
            self.bind("<Enter>", self.show_tooltip)
            self.bind("<Leave>", self.hide_tooltip)

    def on_enter(self, event):
        """Handle mouse enter event"""
        self.configure(bg=self.hover_colors[0])

    def on_leave(self, event):
        """Handle mouse leave event"""
        self.configure(bg=self.default_colors[0])

    def show_tooltip(self, event):
        """Show tooltip on hover"""
        if self.tooltip and not self.tooltip_window:
            x, y, _, _ = self.bbox("insert")
            x += self.winfo_rootx() + 25
            y += self.winfo_rooty() + 25

            self.tooltip_window = tk.Toplevel(self)
            self.tooltip_window.wm_overrideredirect(True)
            self.tooltip_window.wm_geometry(f"+{x}+{y}")

            label = tk.Label(
                self.tooltip_window,
                text=self.tooltip,
                bg="#f0f0f0",
                fg="#333333",
                relief='solid',
                borderwidth=1,
                padx=5,
                pady=5
            )
            label.pack()

    def hide_tooltip(self, event):
        """Hide tooltip"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

    @staticmethod
    def lighten_color(hex_color: str, factor: float) -> str:
        """Lighten a hex color by a factor"""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        rgb = tuple(min(255, int(c + (255 - c) * factor)) for c in rgb)
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

class StatusIndicator(tk.Frame):
    """A modern status indicator with color coding"""
    def __init__(self, parent, label: str, initial_status: str = "offline", **kwargs):
        super().__init__(parent, bg='#f0f0f0', **kwargs)

        self.label_text = label
        self.status_colors = {
            'online': '#25D366',   # WhatsApp green
            'offline': '#FF0000',  # Red
            'warning': '#FF9900',  # Orange
            'processing': '#0099FF' # Blue
        }

        self.canvas = tk.Canvas(
            self,
            width=12,
            height=12,
            bg='#f0f0f0',
            highlightthickness=0,
            bd=0
        )
        self.canvas.pack(side='left', padx=(0, 5))

        self.label = tk.Label(
            self,
            text=f"{label}: {initial_status.upper()}",
            font=('Segoe UI', 9),
            fg='#333333',
            bg='#f0f0f0'
        )
        self.label.pack(side='left')

        self.set_status(initial_status)

    def set_status(self, status: str):
        """Update the status indicator"""
        color = self.status_colors.get(status, '#999999')
        self.canvas.delete("all")
        self.canvas.create_oval(2, 2, 10, 10, fill=color, outline=color)
        self.label.configure(text=f"{self.label_text}: {status.upper()}")

class AnimatedProgressBar(tk.Frame):
    """An animated progress bar with modern styling"""
    def __init__(self, parent, label: str = "", color: str = '#25D366', **kwargs):
        super().__init__(parent, bg='#ffffff', **kwargs)

        self.color = color
        self.current_value = 0
        self.target_value = 0
        self.animation_speed = 2

        self.label = tk.Label(
            self,
            text=label,
            font=('Segoe UI', 9),
            fg='#333333',
            bg='#ffffff'
        )
        self.label.pack(anchor='w')

        self.progress_frame = tk.Frame(self, bg='#e0e0e0', height=8)
        self.progress_frame.pack(fill='x', pady=(2, 5))
        self.progress_frame.pack_propagate(False)

        self.canvas = tk.Canvas(
            self.progress_frame,
            height=8,
            bg='#e0e0e0',
            highlightthickness=0,
            bd=0
        )
        self.canvas.pack(fill='both', expand=True)

        self.value_label = tk.Label(
            self,
            text="0%",
            font=('Segoe UI', 8),
            fg='#333333',
            bg='#ffffff'
        )
        self.value_label.pack(anchor='e')

        self.animate_progress()

    def set_value(self, value: float):
        """Set the target value for the progress bar (0-100)"""
        self.target_value = max(0, min(100, value))

    def animate_progress(self):
        """Animate the progress bar to the target value"""
        if abs(self.current_value - self.target_value) > 0.5:
            if self.current_value < self.target_value:
                self.current_value = min(self.current_value + self.animation_speed, self.target_value)
            else:
                self.current_value = max(self.current_value - self.animation_speed, self.target_value)
        else:
            self.current_value = self.target_value

        self.draw_progress()
        self.after(50, self.animate_progress)

    def draw_progress(self):
        """Draw the progress bar"""
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        if width <= 1:
            self.after(10, self.draw_progress)
            return

        self.canvas.create_rectangle(0, 0, width, height, fill='#e0e0e0', outline='')
        fill_width = (self.current_value / 100) * width
        if fill_width > 0:
            self.canvas.create_rectangle(0, 0, fill_width, height, fill=self.color, outline='')
        self.value_label.configure(text=f"{self.current_value:.0f}%")

class AlertHistoryWidget(tk.Frame):
    """Widget to display alert history with scrolling"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg='#ffffff', **kwargs)

        title = tk.Label(
            self,
            text="🚨 Alert History",
            font=('Segoe UI', 10, 'bold'),
            fg='#FF0000',
            bg='#ffffff'
        )
        title.pack(pady=(0, 10))

        self.canvas = tk.Canvas(
            self,
            bg='#ffffff',
            highlightthickness=0,
            bd=0
        )
        self.scrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.canvas.yview
        )
        self.scrollable_frame = tk.Frame(self.canvas, bg='#ffffff')

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.alert_items = []

        self.placeholder = tk.Label(
            self.scrollable_frame,
            text="No alerts recorded yet",
            font=('Segoe UI', 9),
            fg='#999999',
            bg='#ffffff'
        )
        self.placeholder.pack(pady=20)

    def update_history(self, alerts: List[dict]):
        """Update the alert history display"""
        for item in self.alert_items:
            item.destroy()
        self.alert_items.clear()

        if not alerts:
            self.placeholder.pack(pady=20)
            return
        else:
            self.placeholder.pack_forget()

        for alert in reversed(alerts):
            alert_frame = tk.Frame(
                self.scrollable_frame,
                bg='#f0f0f0',
                relief='solid',
                bd=1
            )
            alert_frame.pack(fill='x', pady=2, padx=5)

            time_label = tk.Label(
                alert_frame,
                text=alert.get('time', 'Unknown'),
                font=('Segoe UI', 8, 'bold'),
                fg='#FF0000',
                bg='#f0f0f0'
            )
            time_label.pack(anchor='w', padx=5, pady=(2, 0))

            message = f"{alert.get('type', 'No message')} (EAR: {alert.get('ear', 0.0):.3f})"
            message_label = tk.Label(
                alert_frame,
                text=message,
                font=('Segoe UI', 9),
                fg='#333333',
                bg='#f0f0f0',
                wraplength=250,
                justify='left'
            )
            message_label.pack(anchor='w', padx=5, pady=(0, 2))

            self.alert_items.append(alert_frame)

# Remaining classes (MetricCard, LiveChart, etc.) remain unchanged for brevity
# Add rounded rectangle method to Canvas
def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
    """Create a rounded rectangle on canvas"""
    points = []
    points.extend([x1 + radius, y1])
    points.extend([x2 - radius, y1])
    for i in range(90, -1, -10):
        x = x2 - radius + radius * math.cos(math.radians(i))
        y = y1 + radius - radius * math.sin(math.radians(i))
        points.extend([x, y])
    points.extend([x2, y1 + radius])
    points.extend([x2, y2 - radius])
    for i in range(0, 91, 10):
        x = x2 - radius + radius * math.cos(math.radians(i))
        y = y2 - radius + radius * math.sin(math.radians(i))
        points.extend([x, y])
    points.extend([x2 - radius, y2])
    points.extend([x1 + radius, y2])
    for i in range(90, 181, 10):
        x = x1 + radius + radius * math.cos(math.radians(i))
        y = y2 - radius + radius * math.sin(math.radians(i))
        points.extend([x, y])
    points.extend([x1, y2 - radius])
    points.extend([x1, y1 + radius])
    for i in range(180, 271, 10):
        x = x1 + radius + radius * math.cos(math.radians(i))
        y = y1 + radius + radius * math.sin(math.radians(i))
        points.extend([x, y])
    return self.create_polygon(points, smooth=True, **kwargs)

tk.Canvas.create_rounded_rect = create_rounded_rect
