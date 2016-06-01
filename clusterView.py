# clusterView.py

from __future__ import absolute_import, print_function
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
from numpy import ndarray

###############################################################################

def displayResultsOnMap(summaryParsedCoord, clusterResult, title):
    print( "displayResultsOnMap" )

    #europeBB=[-31.266001, 27.636311, 39.869301, 81.008797]
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

    ############## read coordinates #################
    fIn = open(summaryParsedCoord, 'r')

    rowCount=0
    for line in fIn:
        rowCount = rowCount + 1
    fIn.close()
    fIn = open(summaryParsedCoord, 'r')

    coordMat = ndarray((rowCount,3),int)
    rowIndex = 0
    for line in fIn:
        coordMat[rowIndex, 0] = rowIndex
        #id_str_json = line.split(' ', 1)[0]
        longitude = int(line.split(' ', 2)[1])
        latitude = int(line.split(' ', 2)[2])
        #print( "id_str_json=%s longitude=%d latit11ude=%d" % (id_str_json,longitude,latitude) )
        coordMat[rowIndex, 1] = latitude
        coordMat[rowIndex, 2] = longitude

        rowIndex = rowIndex + 1
    ############## read coordinates #################

    ############## read cluster results #################
    fCluster = open(clusterResult, 'r')

    clusterV = ndarray((rowCount,2),int)
    fCluster.readline() # ignore first line
    rowIndex = 0
    for line in fCluster:
        clusterV[rowIndex][0]=rowIndex
        clusterV[rowIndex][1]=int(line.split(' ', 1)[1])
        rowIndex = rowIndex + 1
    fCluster.close()
    ############## read cluster results #################

    #lon, lat = 21, 52 # Location of Waw
    # convert to map projection coords.
    # Note that lon,lat can be scalars, lists or numpy arrays.
    #xpt,ypt = m(lon,lat)

    noGroups = np.amax(clusterV[:,1])
    print( "noGroups=%d" % noGroups )

    colorsArray = ["bo", "ro", "go", "yo", "wo", "mo", "kx"]

    for i in range(1, noGroups+1):
        # get tweets indx for give group id
        subGroup = clusterV[clusterV[:,1] == i]
        # filter coord mat based on tweets ids from above line
        subCoordMat = coordMat[subGroup[:,0]]

        xpt,ypt = m(subCoordMat[:,2],subCoordMat[:,1])
        # convert back to lat/lon
        lonpt, latpt = m(xpt,ypt,inverse=True)

        #print( "x=%f y=%f xpt=%f ypt=%f" % (x, y, xpt, ypt) )
        m.plot(xpt,ypt,colorsArray[i-1])  # plot a point there

    # put some text next to the dot, offset a little bit
    # (the offset is in map projection coordinates)
    #plt.text(xpt+100000,ypt+100000,'Waw')

    plt.title(title)
    plt.show()

###############################################################################
