# clusterModule.py

from __future__ import absolute_import, print_function
import subprocess
import rpy2
import rpy2.robjects as robjects
# R vector of strings
from rpy2.robjects.vectors import StrVector
import rpy2.robjects.numpy2ri
from numpy import array
import rpy2.robjects.packages as rpackages

###############################################################################

packnames = ('cluster')

###############################################################################

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

###############################################################################

def clusterClara(tweetsMatrixFile, k, outputFile):
    print ( "Clara with ", k, " groups" )

    r_execClara = robjects.r('''
      library(Matrix)
      library(cluster)
      function(tweetsMatrixFile, k, outputFile) {
         coorMat <- read.table(tweetsMatrixFile)
         r <- as.numeric(t(coorMat[,1]))
         c <- as.numeric(t(coorMat[,2]))
         v <- as.numeric(t(coorMat[,3]))
         matSp <- sparseMatrix(i=r,j=c,x=v, dims=c(max(r),max(c)))
         #clarax <- clara(matSp[1:600,1:500], k, samples=50) TODO need to decrease the size of data
         clarax <- clara(matSp, k, samples=50)
         ## using pamLike=TRUE  gives the same (apart from the 'call'):
         #all.equal(clarax[-8], clara(matSp, k, samples=50, pamLike = TRUE)[-8])
         #plot(clarax)
	 save(clarax,file=outputFile)
      }
    ''')
    
    r_execClara(tweetsMatrixFile, k, outputFile)
    return

###############################################################################

def clusterResults(clusterDataFile):
    print ( "Show clustering result" )

    r_execShowResults = robjects.r('''
      function(outputFileName) {         
	 clarax <- load(outputFileName)
         plot(clarax) #TODO need to check how to load and save data frame data. This approach fails
     }
    ''')
    r_execShowResults(clusterDataFile)
    return

###############################################################################
