#!usr/bin/env python3

import os
import sys
import subprocess
import folium
import json


def initialize_GRASS_notebook(binary, grassdata, location, mapset):

    # create GRASS GIS runtime environment
    sys.path.append(
        subprocess.check_output([binary, "--config", "python_path"], text=True).strip()
    )

    # do GRASS GIS imports
    import grass.script as gs
    import grass.jupyter as gj

    # set GRASS GIS session data
    return gj.init(grassdata, location, mapset)


def show(raster):
    import grass.jupyter as gj

    render_map = gj.Map()
    render_map.d_rast(map=raster)
    render_map.d_vect(map="counties", fill_color="none", width=2)
    return render_map.show()


def show_interactively(raster, opacity=0.8):
    import grass.jupyter as gj

    render_map = gj.InteractiveMap()
    render_map.add_raster(map=raster, opacity=opacity)
    return render_map.show()
