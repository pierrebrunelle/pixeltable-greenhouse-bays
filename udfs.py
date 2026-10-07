"""Pixeltable UDFs for greenhouse operations (recorded by module path, e.g. `udfs.climate_band`)."""
import math

import pixeltable as pxt


@pxt.udf
def climate_band(temp_c: float, humidity_pct: float) -> str:
    """cold / ok / humid / stress from temperature and relative humidity."""
    if temp_c >= 32 or humidity_pct >= 85:
        return 'stress'
    if temp_c < 12:
        return 'cold'
    return 'humid' if humidity_pct >= 75 else 'ok'


@pxt.udf
def vpd_kpa(temp_c: float, humidity_pct: float) -> float:
    """Vapour-pressure deficit in kPa (Tetens equation)."""
    svp = 0.6108 * math.exp(17.27 * temp_c / (temp_c + 237.3))
    return round(svp * (1 - humidity_pct / 100), 2)


@pxt.udf
def bay_label(zone: str, bay_id: str, crop: str | None) -> str:
    return f'{zone.title()} · {bay_id}' + (f' · {crop}' if crop else ' · empty')
