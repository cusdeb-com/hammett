"""The package contains OpenTelemetry instrumentation for Hammett framework."""

from hammett.telemetry.instrumentor import HammettInstrumentor, instrument_telemetry

__all__ = (
    'HammettInstrumentor',
    'instrument_telemetry',
)
