# clusterView.py

from __future__ import absolute_import, print_function
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np

###############################################################################

def displayResultsOnMap():
    print( "displayResultsOnMap" )

    europeBB=[-31.266001, 27.636311, 39.869301, 81.008797]
    # setup stereographic basemap.
    # lat_ts is latitude of true scale.
    # lon_0,lat_0 is central point.
    m = Basemap(width=6000000,height=5000000,
                resolution='l',projection='stere',\
                lat_ts=0,lat_0=55,lon_0=20)
    m.drawcoastlines()
    m.fillcontinents(color='coral',lake_color='aqua')

    # draw parallels and meridians.
    # label parallels on right and top
    # meridians on bottom and left
    parallels = np.arange(0.,81,10.)
    # labels = [left,right,top,bottom]
    m.drawparallels(parallels,labels=[False,True,True,False])
    meridians = np.arange(0.,351.,20.)
    m.drawmeridians(meridians,labels=[True,False,False,True])

    m.drawmapboundary(fill_color='aqua')

    lon, lat = 21, 52 # Location of Waw
    # convert to map projection coords.
    # Note that lon,lat can be scalars, lists or numpy arrays.
    xpt,ypt = m(lon,lat)
    # convert back to lat/lon
    lonpt, latpt = m(xpt,ypt,inverse=True)
    m.plot(xpt,ypt,'ro')  # plot a blue dot there

    m.plot(xpt-100000,ypt-100000,'bo')  # plot a blue dot there
    # put some text next to the dot, offset a little bit
    # (the offset is in map projection coordinates)
    #plt.text(xpt+100000,ypt+100000,'Waw')

    # draw tissot's indicatrix to show distortion.
    #ax = plt.gca()
    #for y in np.linspace(m.ymax/20,19*m.ymax/20,9):
    #    for x in np.linspace(m.xmax/20,19*m.xmax/20,12):
    #        lon, lat = m(x,y,inverse=True)
    #        poly = m.tissot(lon,lat,1.5,100,\
    #                        facecolor='green',zorder=10,alpha=0.5)
    plt.title("Stereographic Projection")
    plt.show()

###############################################################################
