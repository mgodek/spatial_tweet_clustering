# clusterModule.py

from __future__ import absolute_import, print_function
import rpy2
import rpy2.robjects as robjects

packnames = ('cluster')

import rpy2.robjects.packages as rpackages

def setupCluster():
    if all(rpackages.isinstalled(x) for x in packnames):
        have_packages = True
    else:
        have_packages = False

    if not have_packages:
        # import R's utility package
        utils = rpackages.importr('utils')
        # select a mirror for R packages
        utils.chooseCRANmirror(ind=1) # select the first mirror in the list

    if not have_packages:
        # R vector of strings
        from rpy2.robjects.vectors import StrVector
        # file
        packnames_to_install = [x for x in packnames if not rpackages.isinstalled(x)]
        if len(packnames_to_install) > 0:
            utils.install_packages(StrVector(packnames_to_install))

def clusterClara(x, k):
    print ( "Clara with ", k, " groups" )

    robjects.r('''
        execClara <- function(r, verbose=FALSE) {
            if (verbose) {
                cat("I am calling execClara().\n")
            }
            2 * pi * r
            #clarax <- clara(x, k, samples=50)
            #clarax
            #clarax$clusinfo
            ## using pamLike=TRUE  gives the same (apart from the 'call'):
            #all.equal(clarax[-8],
            #          clara(x, k, samples=50, pamLike = TRUE)[-8])
            #plot(clarax)
        }
        
        execClara(3)
    ''')
    
    r_execClara = robjects.globalenv['execClara']
    print(r_execClara.r_repr())
    return
