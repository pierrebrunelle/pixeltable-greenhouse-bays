"""Greenhouse Operations API built with Pixeltable.

    pxt schema update app.py greenhouse
    pxt service run app.py greenhouse
"""
import pixeltable as pxt
import pixeltable.functions as pxtf
from pixeltable.serving import FastAPIRouter

from udfs import bay_label, climate_band, vpd_kpa

# ---- tables ----
TableModel = pxt.model_base()


class Bays(TableModel, name='bays', has_default_idxs=False):
    bay_id = pxt.Column(type=pxt.String, primary_key=True)
    zone: pxt.String
    crop: pxt.String | None
    status: pxt.String              # open / planted / resting

    label = bay_label(zone, bay_id, crop)

    __indexes__ = [pxt.BtreeIndex(zone), pxt.BtreeIndex(status), pxt.BtreeIndex(crop)]


class Readings(TableModel, name='readings', has_default_idxs=False):
    id = pxt.Column(value=pxtf.uuid.uuid7(), primary_key=True)
    bay_id: pxt.String
    taken_at: pxt.String
    temp_c: pxt.Float
    humidity_pct: pxt.Float

    band = climate_band(temp_c, humidity_pct)
    vpd = vpd_kpa(temp_c, humidity_pct)

    __indexes__ = [pxt.BtreeIndex(bay_id)]


class Plantings(TableModel, name='plantings', has_default_idxs=False):
    id = pxt.Column(value=pxtf.uuid.uuid7(), primary_key=True)
    bay_id: pxt.String
    crop: pxt.String
    planted_on: pxt.String
    status: pxt.String

    __indexes__ = [pxt.BtreeIndex(bay_id)]


# ---- queries ----
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


# ---- routes ----
greenhouse_api = FastAPIRouter(name='greenhouse_api')
greenhouse_api.add_insert_route(Bays, path='/bays', inputs=[Bays.bay_id, Bays.zone, Bays.crop, Bays.status],
                                outputs=[Bays.bay_id, Bays.label])
greenhouse_api.add_update_route(Bays, path='/bays/status', inputs=[Bays.status, Bays.crop],
                                outputs=[Bays.bay_id, Bays.status, Bays.label])
greenhouse_api.add_insert_route(Readings, path='/readings',
                                inputs=[Readings.bay_id, Readings.taken_at, Readings.temp_c, Readings.humidity_pct],
                                outputs=[Readings.id, Readings.band, Readings.vpd])
greenhouse_api.add_insert_route(Plantings, path='/plantings',
                                inputs=[Plantings.bay_id, Plantings.crop, Plantings.planted_on, Plantings.status],
                                outputs=[Plantings.id])
greenhouse_api.add_compute_route(Readings, path='/climate-band', inputs=[Readings.temp_c, Readings.humidity_pct],
                                 outputs=[Readings.band, Readings.vpd])
greenhouse_api.add_query_route(path='/bays/open', query=open_bays, method='get')
greenhouse_api.add_query_route(path='/bays/climate', query=bay_climate, method='get')
