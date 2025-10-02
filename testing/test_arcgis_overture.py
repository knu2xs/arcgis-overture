"""
This is a stubbed out test file designed to be used with PyTest, but can 
easily be modified to support any testing framework.
"""

from pathlib import Path
import sys

import pandas as pd
import pytest

# get paths to useful resources - notably where the src directory is
self_pth = Path(__file__)
dir_test = self_pth.parent
dir_prj = dir_test.parent
dir_src = dir_prj / 'src'

# insert the src directory into the path and import the projct package
sys.path.insert(0, str(dir_src))
import arcgis_overture


def test_get_spatially_enabled_dataframe():
    """Test fetching segments (transportation data) data for a small area, Loup Loup Pass, WA"""
    extent = (-119.911,48.3852,-119.8784,48.4028)

    df = arcgis_overture.get_spatially_enabled_dataframe("segment", extent)
    
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert df.spatial.validate()


def test_get_spatially_enabled_dataframe_invalid_type():
    extent = (-119.911, 48.3852, -119.8784, 48.4028)
    with pytest.raises(ValueError, match="Invalid overture type"):
        arcgis_overture.get_spatially_enabled_dataframe("not_a_type", extent)


def test_get_spatially_enabled_dataframe_bbox_length():
    bad_bbox = (-119.911, 48.3852, -119.8784)  # Only 3 values
    with pytest.raises(ValueError, match="Bounding box must be a tuple of four values"):
        arcgis_overture.get_spatially_enabled_dataframe("segment", bad_bbox)


def test_get_spatially_enabled_dataframe_bbox_non_numeric():
    bad_bbox = (-119.911, 48.3852, "foo", 48.4028)
    with pytest.raises(ValueError, match="All coordinates in the bounding box must be numeric"):
        arcgis_overture.get_spatially_enabled_dataframe("segment", bad_bbox)

def test_get_spatially_enabled_dataframe_bbox_invalid_order():
    bad_bbox = (-119.8784, 48.3852, -119.911, 48.4028)  # minx > maxx
    with pytest.raises(ValueError, match="Invalid bounding box coordinates"):
        arcgis_overture.get_spatially_enabled_dataframe("segment", bad_bbox)
