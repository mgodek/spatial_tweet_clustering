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

packnames = ('cluster', 'tictoc', 'fossil')

###############################################################################

def setupCluster():
    # import R's utility package
    utils = rpackages.importr('utils')
    # select a mirror for R packages
    utils.chooseCRANmirror(ind=1) # select the first mirror in the list

    for x in packnames:
        if not rpackages.isinstalled(x):
            utils.install_packages(x)
            print ( "installing ", x )

    print( "In case lgfortran is missing make sure these have same used version of gcc, g++ and gfortran" )


###############################################################################

def clusterClara(tweetsMatrixFile, k, outputClusterFile, outputMedoidFile):
    print ( "Clara with ", k, " groups" )

    r_execClara = robjects.r('''
      library(Matrix)
      library(cluster)
      library(tictoc)
      function(tweetsMatrixFile, k, outputClusterFile, outputMedoidFile) {
         coorMat <- read.table(tweetsMatrixFile)

         r <- as.numeric(t(coorMat[,1]))
         c <- as.numeric(t(coorMat[,2]))
         v <- as.numeric(t(coorMat[,3]))
         matSp <- sparseMatrix(i=r,j=c,x=v, dims=c(max(r),max(c)))
         tic()
         clarax <- clara(matSp, k, metric = "euclidean", stand = FALSE, samples = 50, sampsize = min(max(r), 40 + 2 * k), trace = 4, medoids.x = TRUE, rngR = FALSE)
         print(toc())

         #print(clarax[4])
	 write.table(clarax[4],file=outputClusterFile,sep = " ")
	 write.table(clarax[2],file=outputMedoidFile,sep = " ")
         #plot(clarax)
         print(clarax)
      }
    ''')
    
    r_execClara(tweetsMatrixFile, k, outputClusterFile, outputMedoidFile)
    print( "Saved results to %s %s" % (outputClusterFile,outputMedoidFile) ) 
    return

###############################################################################

def clusterResultsRandIdx(clusterResult1, clusterResult2):
    print ( "Show clustering result" )

    r_execShowResults = robjects.r('''
      library(fossil)
      function(clusterResult1, clusterResult2) {         
         clusterData1 = read.table(clusterResult1)
         clusterData2 = read.table(clusterResult2)
         randIdx = rand.index(clusterData1[,1],clusterData2[,1])
         print(randIdx)
     }
    ''')
    r_execShowResults(clusterResult1,clusterResult2)
    return

###############################################################################
