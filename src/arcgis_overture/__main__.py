import json

from arcgis.geometry import Geometry
from geomet import wkb, esri
import pandas as pd
from overturemaps import core as ovm

from .utils import get_logger

# configure module logging
logger = get_logger(logger_name="arcgis_overture", level="DEBUG")


def get_spatially_enabled_dataframe(
    overture_type: str,
    bbox: tuple[float, float, float, float],
    connect_timeout: int = None,
    request_timeout: int = None,
) -> pd.DataFrame:
    """
    Retrieve data from Overture Maps and return it as a Pandas spatially enabled DataFrame.

    Args:
        overture_type: Overture feature type to retrieve.
        bbox: Bounding box to filter the data. Format: (minx, miny, maxx, maxy).
        connect_timeout: Optional timeout in seconds for establishing a connection to the Overture Maps service.
        request_timeout: Optional timeout in seconds for waiting for a response from the Overture Maps service.

    !!! note

        To see available overture types, use `overturemaps.core.get_all_overture_types()`.

    Returns:
        A spatially enabled pandas DataFrame containing the requested Overture Maps data.
    """
    # validate the overture type
    available_types = ovm.get_all_overture_types()
    if overture_type not in available_types:
        raise ValueError(
            f"Invalid overture type: {overture_type}. Valid types are: {available_types}"
        )

    # validate the bounding box
    if len(bbox) != 4:
        raise ValueError(
            "Bounding box must be a tuple of four values: (minx, miny, maxx, maxy)."
        )
    if not all(isinstance(coord, (int, float)) for coord in bbox):
        raise ValueError(
            "All coordinates in the bounding box must be numeric (int or float)."
        )
    if bbox[0] >= bbox[2] or bbox[1] >= bbox[3]:
        raise ValueError(
            "Invalid bounding box coordinates: ensure that minx < maxx and miny < maxy."
        )

    # fetch the data from Overture Maps into an Arrow RecordBatchReader
    reader = ovm.record_batch_reader(
        overture_type, bbox, connect_timeout, request_timeout
    )

    # get an arrow table from the RecordBatchReader
    tbl = reader.read_all()

    tbl_cnt = tbl.num_rows
    logger.debug(f"Fetched {tbl_cnt} rows of '{overture_type}' data from Overture Maps.")
    if tbl_cnt == 0:
        logger.warning(f"No '{overture_type}' data found for the specified bounding box: {bbox}")

    # convert the table to a pandas DataFrame
    df = tbl.to_pandas()

    # get the geometry column from the metadata
    geo_meta = tbl.schema.metadata.get(b"geo")
    if geo_meta is None:
        raise ValueError("No geometry metadata found in the Overture Maps data.")
    geo_meta = json.loads(geo_meta.decode("utf-8"))
    geom_col = geo_meta.get("primary_column")
    if geom_col is None or geom_col not in df.columns:
        raise ValueError("No valid primary_geometry column defined in the Overture Maps metadata.")

    # convert the geometry column from WKB to arcgis Geometry objects
    df[geom_col] = df[geom_col].apply(lambda itm: Geometry(esri.dumps(wkb.loads(itm))))

    # set the geometry column using the ArcGIS GeoAccessor to get a Spatially Enabled DataFrame
    df.spatial.set_geometry(geom_col, sr=4326)

    return df