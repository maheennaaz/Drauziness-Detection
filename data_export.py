#!/usr/bin/env python3
"""
Enhanced Data Export Module for AI Drowsiness Detection System
"""
import csv
import json
import os
import statistics
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd


@dataclass
class SessionData:
    """Enhanced data structure for a single detection session"""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    total_drowsiness_events: int = 0
    alert_frequency_per_minute: float = 0.0
    average_ear: float = 0.0
    min_ear: float = 0.0
    max_ear: float = 0.0
    average_alertness: float = 0.0
    settings_used: Dict[str, Any] = None
    metadata: Dict[str, Any] = None

@dataclass
class DrowsinessEvent:
    """Data structure for individual drowsiness detection events"""
    timestamp: datetime
    ear_value: float
    event_type: str = "drowsiness_detected"
    duration_seconds: float = 0.0
    severity_level: str = "moderate"
    additional_data: Dict[str, Any] = None

@dataclass
class SessionReport:
    """Comprehensive session report structure"""
    session_data: SessionData
    events: List[DrowsinessEvent]
    summary_statistics: Dict[str, Any]
    recommendations: List[str]
    export_timestamp: datetime

class DataExporter:
    """Enhanced main class for exporting drowsiness detection data"""
    def __init__(self, base_export_path: str = "exports"):
        self.base_export_path = base_export_path
        self.ensure_export_directory()

    def ensure_export_directory(self) -> bool:
        """Create export directory if it doesn't exist with error handling"""
        try:
            if not os.path.exists(self.base_export_path):
                os.makedirs(self.base_export_path)
            return True
        except Exception as e:
            print(f"Error creating export directory: {e}")
            return False

    def generate_session_id(self) -> str:
        """Generate a unique session ID"""
        return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"

    def validate_data_before_export(self, session_data: SessionData,
                                 events: List[DrowsinessEvent]) -> Tuple[bool, str]:
        """Validate data before export to prevent corruption"""
        if not session_data:
            return False, "No session data provided"

        if not isinstance(session_data, SessionData):
            return False, "Invalid session data type"

        if not isinstance(events, list):
            return False, "Events must be a list"

        for event in events:
            if not isinstance(event, DrowsinessEvent):
                return False, f"Invalid event type: {type(event)}"

        return True, "Data validation passed"

    def export_to_csv(self, session_data: SessionData, events: List[DrowsinessEvent],
                     filename: Optional[str] = None) -> Tuple[bool, str]:
        """Export session data and events to CSV with enhanced error handling"""
        try:
            is_valid, message = self.validate_data_before_export(session_data, events)
            if not is_valid:
                return False, f"Data validation failed: {message}"

            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"drowsiness_session_{timestamp}.csv"

            filepath = os.path.join(self.base_export_path, filename)

            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Session Information'])
                writer.writerow(['Session ID', session_data.session_id])
                writer.writerow(['Start Time', session_data.start_time.isoformat()])
                writer.writerow(['End Time', session_data.end_time.isoformat() if session_data.end_time else 'N/A'])
                writer.writerow(['Duration (seconds)', session_data.duration_seconds])
                writer.writerow(['Total Drowsiness Events', session_data.total_drowsiness_events])
                writer.writerow(['Alert Frequency (per minute)', session_data.alert_frequency_per_minute])
                writer.writerow(['Average EAR', session_data.average_ear])
                writer.writerow(['Min EAR', session_data.min_ear])
                writer.writerow(['Max EAR', session_data.max_ear])
                writer.writerow(['Average Alertness', session_data.average_alertness])
                writer.writerow([])
                writer.writerow(['Drowsiness Events'])
                writer.writerow(['Timestamp', 'Value', 'Event Type', 'Duration (seconds)', 'Severity Level'])
                for event in events:
                    writer.writerow([
                        event.timestamp.isoformat(),
                        event.ear_value,
                        event.event_type,
                        event.duration_seconds,
                        event.severity_level
                    ])

            return True, f"Data successfully exported to {filepath}"

        except Exception as e:
            return False, f"Export failed: {str(e)}"

    def export_to_json(self, session_data: SessionData, events: List[DrowsinessEvent],
                      filename: Optional[str] = None) -> Tuple[bool, str]:
        """Export session data to JSON format"""
        try:
            is_valid, message = self.validate_data_before_export(session_data, events)
            if not is_valid:
                return False, f"Data validation failed: {message}"

            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"drowsiness_session_{timestamp}.json"

            filepath = os.path.join(self.base_export_path, filename)

            session_dict = asdict(session_data)
            events_dict = [asdict(event) for event in events]

            def datetime_serializer(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

            export_data = {
                'session_data': session_dict,
                'events': events_dict,
                'export_timestamp': datetime.now().isoformat(),
                'format_version': '1.0'
            }

            with open(filepath, 'w', encoding='utf-8') as jsonfile:
                json.dump(export_data, jsonfile, indent=2, default=datetime_serializer)

            return True, f"Data successfully exported to {filepath}"

        except Exception as e:
            return False, f"JSON export failed: {str(e)}"

    def generate_session_report(self, session_data: SessionData,
                              events: List[DrowsinessEvent]) -> SessionReport:
        """Generate a comprehensive session report"""
        summary_stats = self.calculate_session_statistics(session_data, events)
        recommendations = self.generate_recommendations(session_data, events)

        return SessionReport(
            session_data=session_data,
            events=events,
            summary_statistics=summary_stats,
            recommendations=recommendations,
            export_timestamp=datetime.now()
        )

    def calculate_session_statistics(self, session_data: SessionData,
                                   events: List[DrowsinessEvent]) -> Dict[str, Any]:
        """Calculate detailed session statistics"""
        if not events:
            return {
                'total_events': 0,
                'events_per_hour': 0.0,
                'average_event_duration': 0.0,
                'peak_drowsiness_hour': 'N/A',
                'severity_distribution': {}
            }

        total_events = len(events)
        session_duration_hours = session_data.duration_seconds / 3600
        events_per_hour = total_events / max(session_duration_hours, 1/60)

        event_durations = [event.duration_seconds for event in events if event.duration_seconds > 0]
        avg_event_duration = statistics.mean(event_durations) if event_durations else 0.0

        severity_counts = {}
        for event in events:
            severity = event.severity_level
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        peak_hour = 'N/A'
        if events and session_data.start_time:
            hours = [event.timestamp.hour for event in events]
            if hours:
                peak_hour = max(set(hours), key=hours.count)

        return {
            'total_events': total_events,
            'events_per_hour': round(events_per_hour, 2),
            'average_event_duration': round(avg_event_duration, 2),
            'peak_drowsiness_hour': peak_hour,
            'severity_distribution': severity_counts,
            'session_quality_score': self.calculate_quality_score(session_data, events)
        }

    def calculate_quality_score(self, session_data: SessionData,
                              events: List[DrowsinessEvent]) -> float:
        """Calculate a session quality score (0-100)"""
        if session_data.duration_seconds < 60:
            return 100.0

        score = 100.0
        events_per_minute = len(events) / (session_data.duration_seconds / 60)
        score -= min(50, events_per_minute * 10)

        if session_data.average_alertness < 70:
            score -= (70 - session_data.average_alertness) * 0.5

        return max(0.0, min(100.0, score))

    def generate_recommendations(self, session_data: SessionData,
                               events: List[DrowsinessEvent]) -> List[str]:
        """Generate personalized recommendations based on session data"""
        recommendations = []

        if not events:
            recommendations.append("Excellent session! No drowsiness detected.")
            return recommendations

        events_per_hour = len(events) / max(session_data.duration_seconds / 3600, 1/60)

        if events_per_hour > 5:
            recommendations.append("High frequency of drowsiness events detected. Consider taking regular breaks.")

        if session_data.average_alertness < 50:
            recommendations.append("Low average alertness detected. Ensure adequate sleep before driving.")

        if session_data.average_ear < 0.2:
            recommendations.append("Consistently low EAR values suggest fatigue. Consider resting.")

        if events and session_data.start_time:
            event_hours = [event.timestamp.hour for event in events]
            if any(hour in range(14, 16) for hour in event_hours):
                recommendations.append("Afternoon drowsiness detected. This is common due to circadian rhythms.")
            if any(hour in range(22, 6) for hour in event_hours):
                recommendations.append("Late night/early morning drowsiness detected. Avoid driving during these hours when possible.")

        if session_data.duration_seconds > 7200:
            recommendations.append("Long session detected. Take breaks every 2 hours during extended periods.")

        if any(event.event_type == "scarf_detected" for event in events):
            recommendations.append("Scarf covering face detected. Ensure clear visibility while driving.")

        if any(event.event_type == "yawn_detected" for event in events):
            recommendations.append("Yawning detected. Consider ventilating the vehicle or taking a short break.")

        if not recommendations:
            recommendations.append("Session completed successfully with minimal drowsiness events.")

        return recommendations

    def export_summary_report(self, session_report: SessionReport,
                            filename: Optional[str] = None) -> Tuple[bool, str]:
        """Export a formatted summary report"""
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"drowsiness_report_{timestamp}.txt"

            filepath = os.path.join(self.base_export_path, filename)

            with open(filepath, 'w', encoding='utf-8') as report_file:
                report_file.write("=" * 60 + "\n")
                report_file.write("AI DROWSINESS DETECTION - SESSION REPORT\n")
                report_file.write("=" * 60 + "\n\n")

                report_file.write("SESSION INFORMATION\n")
                report_file.write("-" * 20 + "\n")
                report_file.write(f"Session ID: {session_report.session_data.session_id}\n")
                report_file.write(f"Start Time: {session_report.session_data.start_time}\n")
                report_file.write(f"End Time: {session_report.session_data.end_time or 'In Progress'}\n")
                report_file.write(f"Duration: {session_report.session_data.duration_seconds / 60:.1f} minutes\n")
                report_file.write(f"Total Events: {session_report.session_data.total_drowsiness_events}\n\n")

                report_file.write("SESSION STATISTICS\n")
                report_file.write("-" * 18 + "\n")
                stats = session_report.summary_statistics
                report_file.write(f"Events per Hour: {stats.get('events_per_hour', 0)}\n")
                report_file.write(f"Average Event Duration: {stats.get('average_event_duration', 0):.1f} seconds\n")
                report_file.write(f"Session Quality Score: {stats.get('session_quality_score', 0):.1f}/100\n")
                report_file.write(f"Peak Drowsiness Hour: {stats.get('peak_drowsiness_hour', 'N/A')}\n\n")

                report_file.write("RECOMMENDATIONS\n")
                report_file.write("-" * 15 + "\n")
                for i, rec in enumerate(session_report.recommendations, 1):
                    report_file.write(f"{i}. {rec}\n")

                report_file.write(f"\nReport generated on: {session_report.export_timestamp}\n")

            return True, f"Summary report exported to {filepath}"

        except Exception as e:
            return False, f"Report export failed: {str(e)}"

    def list_exported_files(self) -> List[str]:
        """List all exported files in the export directory"""
        try:
            if not os.path.exists(self.base_export_path):
                return []
            return [f for f in os.listdir(self.base_export_path)
                   if os.path.isfile(os.path.join(self.base_export_path, f))]
        except Exception as e:
            print(f"Error listing exported files: {e}")
            return []

    def cleanup_old_exports(self, days_old: int = 30) -> Tuple[int, str]:
        """Clean up export files older than specified days"""
        try:
            if not os.path.exists(self.base_export_path):
                return 0, "Export directory does not exist"

            cutoff_date = datetime.now() - timedelta(days=days_old)
            files_removed = 0

            for filename in os.listdir(self.base_export_path):
                filepath = os.path.join(self.base_export_path, filename)
                if os.path.isfile(filepath):
                    file_date = datetime.fromtimestamp(os.path.getmtime(filepath))
                    if file_date < cutoff_date:
                        os.remove(filepath)
                        files_removed += 1

            return files_removed, f"Removed {files_removed} old export files"

        except Exception as e:
            return 0, f"Cleanup failed: {str(e)}"
