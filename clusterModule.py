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
         coorMat <- read.table(tweetsMatrixFile) #'summaryClaraTweetsMatrixFile.txt'

         ###### FOR TESTING #########
         #print( "NOTE!!! USING ONLY first 4k samples" )
         #coorMat <- coorMat[1:4000,] #TODO comment out: reduce size for test
         ###### FOR TESTING #########

         r <- as.numeric(t(coorMat[,1]))
         c <- as.numeric(t(coorMat[,2]))
         v <- as.numeric(t(coorMat[,3]))
         matSp <- sparseMatrix(i=r,j=c,x=v, dims=c(max(r),max(c)))
         clarax <- clara(matSp, k, metric = "euclidean", stand = FALSE, samples = 50, sampsize = min(max(r), 40 + 2 * k), trace = 0, medoids.x = TRUE, rngR = FALSE)

         print(clarax[4]) # TODO we need to save this vector. next line crashes :/
	 #write(clarax[4],file=outputFile,sep = " ")
         plot(clarax)
         print(clarax)
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
         #plot(clarax) #TODO need to check how to load and save data frame data. This approach fails
     }
    ''')
    r_execShowResults(clusterDataFile)
    return

###############################################################################
