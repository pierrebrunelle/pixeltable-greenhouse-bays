"""Greenhouse Operations API built with Pixeltable.

    pxt schema update app.py greenhouse
    pxt service run app.py greenhouse
"""
from pixeltable.serving import FastAPIRouter

from models import Bays, Plantings, Readings, TableModel  # noqa: F401  (TableModel lets `pxt schema` find the models)
from queries import bay_climate, open_bays

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
