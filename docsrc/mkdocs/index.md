---
title: Home
---
# ArcGIS Overture 0.1.0.dev0 Documentation

ArcGIS Overture makes it easy to get data from Overture Maps into ArcGIS. Getting data from Overture Maps into a
spatially enabled Pandas DataFrame is as easy as:

```python
# import the function
from arcgis_overture import get_spatially_enabled_dataframe

# Loup Loup Pass, WA - small area with trails and roads
extent = (-119.911, 48.3852, -119.8784, 48.4028)

# get the data
df = get_spatially_enabled_dataframe("segment", extent)
```

## Installation

```bash
pip install git+https://github.com/knu2xs/arcgis-overture
```

## API Reference

::: arcgis_overture
