"""OSINT tool adapters for the Nexus MVP.

Every adapter hits a free, public, no-auth data source and returns a
normalized :class:`ToolResult` with source citations attached.
"""
from .geocode import geocode
from .flights import flights_near
from .earthquakes import recent_earthquakes
from .weather import weather_at

__all__ = ["geocode", "flights_near", "recent_earthquakes", "weather_at"]
