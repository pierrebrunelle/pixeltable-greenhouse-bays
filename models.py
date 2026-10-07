"""Greenhouse tables with explicit B-tree indexes."""
import pixeltable as pxt
import pixeltable.functions as pxtf

from udfs import bay_label, climate_band, vpd_kpa

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
