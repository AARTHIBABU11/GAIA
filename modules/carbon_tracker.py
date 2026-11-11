# modules/carbon_tracker.py

import time
import psutil  # type: ignore
import threading
from datetime import datetime, timedelta
import streamlit as st  # type: ignore


class CarbonTracker:
    """
    Track carbon footprint of AI operations
    Green AI optimized with real-time carbon intensity
    """

    # Default carbon intensity (gCO2 per kWh) - India grid average
    DEFAULT_CARBON_INTENSITY = 700

    # Power consumption estimates (watts) - CPU only for Green AI
    POWER_WATTS = {
        'cpu': 45,
        'gpu': 100,
        'memory': 3,
        'idle': 15
    }

    # Comparison with conventional AI (50x less efficient)
    CONVENTIONAL_MULTIPLIER = 50

    def __init__(self):
        self.total_emissions_g = 0
        self.total_energy_kwh = 0
        self.total_duration_seconds = 0
        self.operations = []
        self.current_operation = None
        self.start_time = None
        self.start_cpu = None
        self.last_emissions = 0
        self.carbon_intensity = self.DEFAULT_CARBON_INTENSITY
        self._intensity_updated = False

        # For real-time tracking
        self._monitoring = False
        self._monitor_thread = None

    def _get_carbon_intensity(self):
        """Get real-time carbon intensity (mock - replace with actual API)"""
        hour = datetime.now().hour

        if 10 <= hour <= 16:
            return 500
        elif 19 <= hour <= 23:
            return 800
        else:
            return 650

    def update_carbon_intensity(self, use_real_time=True):
        """Update carbon intensity based on real-time grid data"""
        if use_real_time:
            try:
                self.carbon_intensity = self._get_carbon_intensity()
                self._intensity_updated = True
            except Exception as e:
                print(f"Failed to update carbon intensity: {e}")
                self.carbon_intensity = self.DEFAULT_CARBON_INTENSITY
        else:
            self.carbon_intensity = self.DEFAULT_CARBON_INTENSITY

    def start_operation(self, operation_name):
        """Start tracking an operation"""
        self.current_operation = operation_name
        self.start_time = time.time()

        try:
            self.start_cpu = psutil.cpu_percent(interval=0.1)
        except:
            self.start_cpu = 30

        return self

    def end_operation(self):
        """End tracking and calculate emissions"""
        if self.start_time is None:
            return 0

        duration = time.time() - self.start_time
        self.total_duration_seconds += duration

        try:
            end_cpu = psutil.cpu_percent(interval=0.1)
            avg_cpu = (self.start_cpu + end_cpu) / 2
        except:
            avg_cpu = 30

        cpu_power_kw = (self.POWER_WATTS['cpu'] * (avg_cpu / 100)) / 1000
        idle_power_kw = self.POWER_WATTS['idle'] / 1000
        total_power_kw = cpu_power_kw + idle_power_kw

        energy_kwh = total_power_kw * (duration / 3600)

        emissions_g = energy_kwh * self.carbon_intensity
        self.last_emissions = emissions_g

        operation_data = {
            'name': self.current_operation,
            'duration': duration,
            'energy_kwh': energy_kwh,
            'emissions_g': emissions_g,
            'timestamp': datetime.now(),
            'cpu_avg': avg_cpu,
            'carbon_intensity': self.carbon_intensity
        }

        self.operations.append(operation_data)
        self.total_energy_kwh += energy_kwh
        self.total_emissions_g += emissions_g

        self.current_operation = None
        self.start_time = None

        return emissions_g

    def __enter__(self):
        self.start_operation("context_operation")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_operation()

    def track(self, operation_name):
        """Context manager for tracking operations"""
        return OperationContext(self, operation_name)

    def get_total_emissions(self):
        return self.total_emissions_g

    def get_total_energy(self):
        return self.total_energy_kwh

    def get_last_emissions(self):
        return self.last_emissions

    def get_operations_count(self):
        return len(self.operations)

    def get_summary(self):
        conventional_emissions = self.total_emissions_g * self.CONVENTIONAL_MULTIPLIER
        carbon_saved = conventional_emissions - self.total_emissions_g

        return {
            'total_emissions_g': round(self.total_emissions_g, 4),
            'total_emissions_kg': round(self.total_emissions_g / 1000, 6),
            'total_energy_kwh': round(self.total_energy_kwh, 6),
            'total_duration_seconds': round(self.total_duration_seconds, 2),
            'operations_count': len(self.operations),
            'conventional_emissions_g': round(conventional_emissions, 4),
            'carbon_saved_g': round(carbon_saved, 4),
            'carbon_saved_percent': round((carbon_saved / conventional_emissions) * 100, 1) if conventional_emissions > 0 else 0,
            'carbon_intensity': self.carbon_intensity,
            'last_emissions_g': round(self.last_emissions, 4)
        }

    def reset(self):
        self.total_emissions_g = 0
        self.total_energy_kwh = 0
        self.total_duration_seconds = 0
        self.operations = []
        self.current_operation = None
        self.start_time = None
        self.last_emissions = 0
        print("[OK] Carbon tracker reset")


class OperationContext:
    """Context manager for tracking operations with 'with' statement"""

    def __init__(self, tracker, operation_name):
        self.tracker = tracker
        self.operation_name = operation_name

    def __enter__(self):
        self.tracker.start_operation(self.operation_name)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.tracker.end_operation()


# Decorator to track function execution
def track_operation(tracker, operation_name):
    def decorator(func):
        def wrapper(*args, **kwargs):
            with tracker.track(operation_name):
                return func(*args, **kwargs)
        return wrapper
    return decorator


# Global tracker instance
tracker = CarbonTracker()