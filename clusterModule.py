# clusterModule.py

from __future__ import absolute_import, print_function
import rpy2
import rpy2.robjects as robjects
# R vector of strings
from rpy2.robjects.vectors import StrVector
import rpy2.robjects.numpy2ri

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
        # file
        packnames_to_install = [x for x in packnames if not rpackages.isinstalled(x)]
        if len(packnames_to_install) > 0:
            utils.install_packages(StrVector(packnames))
            print ( "installing ", packnames )

def clusterClara(tweetsMatrixFile, k):
    print ( "Clara with ", k, " groups" )

    r_execClara = robjects.r('''
      library(cluster)
      function(x, k) {         
         x <- read.table('claraTweetsMatrixFile.txt') #TODO how to pass tweetsMatrixFile name?
         clarax <- clara(x, k, samples=50)
         clarax
         clarax$clusinfo
         ## using pamLike=TRUE  gives the same (apart from the 'call'):
         #all.equal(clarax[-8], clara(x, k, samples=50, pamLike = TRUE)[-8])
         plot(clarax)
	 save(clarax,file="claraOutput.txt")
     }
    ''')
    
    r_execClara(tweetsMatrixFile,k)
    #print(r_execClara.r_repr())
    return
