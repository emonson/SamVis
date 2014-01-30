#define VERBOSE


#include "Precision.h"

#include <stdio.h>

#include "EuclideanMetric.h"
#include "LinalgIO.h"
#include "IPCATree.h"
#include "DenseMatrix.h"
#include "CmdLine.h"
#include "NodeDistance.h"
  

NodeFactory<Precision> *getNodeFactory(int d, double t){
  if(t < 0){
    return new FixedNodeFactory<double>(d);
  }
  else if(t < 1){
    return new RelativePrecisionNodeFactory<double>(d, t);
  }
  else{
    return new RelativeRatioNodeFactory<double>(d, t);
  }
};







int main(int argc, char **argv){
  
  //Command line parsing
  TCLAP::CmdLine cmd("Create Iterated PCA Tree. Create a tree by iteratively splitting a point cloud according to local principal components.", ' ', "1");

  TCLAP::ValueArg<int> dArg("d","dim","Maximal number of principal comonents to compute per node", true, 3, "integer");
  cmd.add(dArg);

  TCLAP::ValueArg<int> cArg("c","childDim","Maximal number of children per node. I.e. each node can have at most 2^c children", true, 3, "integer");
  cmd.add(cArg);

  TCLAP::ValueArg<Precision> tArg("t", "threshold", "Threshold to determine dimensionality of a node. For t is between 0 and 1 min(d, k) principal components ar retained where k is the smallest number of principal components to capture 100*t percent of the variance of the data points in the node. For negative t each node has 2^d children if possible. For t > 1 it is min(d, k) the ratio between the variance of the k'th over the k'th+1 principal components has to be less than t.", true, -1, "double");
  cmd.add(tArg);

  TCLAP::ValueArg<Precision> eArg("e","epsilon","Parameter for stopping criterion, stop iterative splitting procedure when the specified stopping criterion is less than epsilon", true, 0.1, "double");
  cmd.add(eArg);
  
  TCLAP::ValueArg<int> stopArg("","stop","Stopping criterion. 1: Local R^2, stop if the R^2 of a node, i.e. R^2 with respect to the variance in the node is less than epsilon. 2: Total R^2, stop if the total R^2, i.e. R^2 with respect to the global varianc of the data is less than epsilon. 3: Node MSE, stop if the mean squared error of a node is less than epsilon 4: Node Radius, stop if the radius of a node is less than epsilon, 5: Relative node radius, stop if the radius of the node over the global radius is less than epsilon", true, 2, "integer");
  cmd.add(stopArg);
  
  TCLAP::ValueArg<int> splitArg("","split","Splitting strategy determines how to split a node into its children along the local principal components. 1: Mean, split nodes according to the positing of points with respect to the mean of the node. 2: Midpoint, split across the midpoint of each principal component. 3: Random Mean, add random shift to the mean. 4: Random Midpoint, add random shift to the midpoint location.", true, 2, "integer");
  cmd.add(splitArg);

  TCLAP::ValueArg<std::string> dataArg("x","data", "File with matrix for data point cloud, with each column a data point",  true, "", "matrix header file");
  cmd.add(dataArg);

  TCLAP::ValueArg<std::string> outArg("o","out", "File to store IPCATree in binary format in",  true, "", "file name");
  cmd.add(outArg);

  try{
	  cmd.parse( argc, argv );
	} 
  catch (TCLAP::ArgException &e){ 
    std::cerr << "error: " << e.error() << " for arg " << e.argId() << std::endl; 
    return -1;
  }

try{

  FortranLinalg::DenseMatrix<Precision> X = FortranLinalg::LinalgIO<Precision>::readMatrix(dataArg.getValue());
  Precision eps = eArg.getValue();
  std::string fileName = outArg.getValue();


  NodeFactory<Precision> *nf = getNodeFactory( dArg.getValue(), tArg.getValue() );


  IPCATree<Precision>::StoppingCriterium stop = IPCATree<Precision>::TOTAL_R2;
  switch( stopArg.getValue() ){
    case 1:
      stop = IPCATree<Precision>::NODE_R2;
      break;
    case 2:
      stop = IPCATree<Precision>::TOTAL_R2;
      break;
    case 3:
      stop = IPCATree<Precision>::NODE_MSE;
      break;
    case 4:
      stop = IPCATree<Precision>::NODE_RADIUS;
      break;
    case 5:
      stop = IPCATree<Precision>::RELATIVE_NODE_RADIUS;
      break;
  }



  IPCANode<Precision>::SplitStrategy split = IPCANode<Precision>::MEAN;
  switch( splitArg.getValue() ){
    case 1:
      split = IPCANode<Precision>::MEAN;
      break;
    case 2:
      split = IPCANode<Precision>::MIDPOINT;
      break;
    case 3:
      split = IPCANode<Precision>::RANDOM_MEAN;
      break;
    case 4:
      split = IPCANode<Precision>::RANDOM_MIDPOINT;
      break;
  }

  CenterNodeDistance<Precision> dist(new EuclideanMetric<Precision>());

  IPCATree<Precision> ipcaTree(eps, stop, nf, split, cArg.getValue() );
  ipcaTree.construct(X.data(), X.M(), X.N() );

  std::ofstream file(fileName.c_str(), std::ios_base::out | std::ios_base::binary);
  ipcaTree.flatten(file);

  file.close();

  X.deallocate();


  return 0;
}
catch(...){
  std::cout << "Not a matrix header file" << std::endl;
  return -1;
}

}
