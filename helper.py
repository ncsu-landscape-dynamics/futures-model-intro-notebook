#!usr/bin/env python3

import os
import sys
import subprocess
import folium


def initialize_GRASS_notebook(binary, grassdata, location, mapset):

    # create GRASS GIS runtime environment
    gisbase = subprocess.check_output([binary, "--config", "path"], universal_newlines=True).strip()
    os.environ['GISBASE'] = gisbase
    sys.path.append(os.path.join(gisbase, "etc", "python"))

    # do GRASS GIS imports
    import grass.script as gs
    import grass.script.setup as gsetup

    # set GRASS GIS session data
    rcfile = gsetup.init(gisbase, grassdata, location, mapset)
    # default font displays
    os.environ['GRASS_FONT'] = 'sans'
    # overwrite existing maps
    os.environ['GRASS_OVERWRITE'] = '1'
    gs.set_raise_on_error(True)
    gs.set_capture_stderr(True)
    # set display modules to render into a file (named map.png by default)
    os.environ['GRASS_RENDER_IMMEDIATE'] = 'cairo'
    os.environ['GRASS_RENDER_FILE_READ'] = 'TRUE'
    os.environ['GRASS_LEGEND_FILE'] = 'legend.txt'
    
 
def adjust_futures_colors(raster):
    import grass.script as gs
    new_raster = raster + '_'
    info = gs.raster_info(raster)
    color = '0 200:200:200\n1 255:100:50\n{m} 255:255:0\n100 180:255:160'.format(m=info['max'])
    gs.mapcalc('{nr} = if({r} == -1, 100, {r})'.format(nr=new_raster, r=raster))
    gs.write_command('r.colors', map=new_raster, stdin=color, rules='-')
    return new_raster

def show(raster):
    from IPython.display import Image
    import grass.script as gs
    gs.run_command('d.erase')
    gs.run_command('d.rast', map=raster)
    gs.run_command('d.vect', map='counties', fill_color='none', width=2)
    return Image("map.png")

def show_interactively(raster):
    import grass.script as gs
    region = gs.parse_command('g.region', flags='lcg')
    raster = adjust_futures_colors(raster)
    gs.run_command('r.out.gdal', input=raster, output=raster + '_spm.tif', type='Byte')
    subprocess.call(['gdalwarp', '-t_srs', 'EPSG:3857',  raster + '_spm.tif', raster + '_merc.tif', '-overwrite'])
    subprocess.call(['gdal_translate', '-of', 'png', raster + '_merc.tif', raster + '_merc.png'])
    minlat = min(float(region['se_lat']), float(region['sw_lat']))
    maxlat = max(float(region['ne_lat']), float(region['nw_lat']))
    minlon = min(float(region['sw_long']), float(region['nw_long']))
    maxlon = min(float(region['se_long']), float(region['ne_long']))
    m = folium.Map(location=[35.87008220, -78.78423295])
    img = folium.raster_layers.ImageOverlay(
            name=raster,
            image=raster + '_merc.png',
            bounds=[[minlat, minlon], [maxlat, maxlon]],
            opacity=1,
            interactive=True,
            cross_origin=False,
        )
    img.add_to(m)
    folium.LayerControl().add_to(m)
    return m
