"""Index-backed greenhouse queries."""
import pixeltable as pxt

from models import Bays, Readings


@pxt.query
def open_bays(zone: str):
    """Open bays in a zone (zone + status indexes)."""
    return Bays.where((Bays.zone == zone) & (Bays.status == 'open')).select(Bays.bay_id, Bays.label).order_by(Bays.bay_id)


@pxt.query
def bay_climate(bay_id: str):
    """Readings for one bay, newest first."""
    return Readings.where(Readings.bay_id == bay_id).select(
        Readings.taken_at, Readings.temp_c, Readings.humidity_pct, Readings.band, Readings.vpd
    ).order_by(Readings.taken_at, asc=False)
