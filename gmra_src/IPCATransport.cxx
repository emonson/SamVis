#include "Precision.h"

#include <stdio.h>

#include "EuclideanMetric.h"

#include "DenseVector.h"
#include "LinalgIO.h"

#include "MultiscaleSinkhornTransport.h"
//#include "MultiscaleTransportGLPK.h"
//#include "MultiscaleTransportMOSEK.h"
//#include "MultiscaleTransportCPLEX.h"
#include "MultiscaleTransportCPLEXnetwork.h"
//#include "MultiscaleTransportMCF.h"
#include "GMRAMultiscaleTransport.h"
#include "NodeDistance.h"
#include "RelativeGMRANeighborhood.h"
#include "IPCAGWT.h"

#include "CmdLine.h"

int main(int argc, char **argv){

  //Command line parsing
  TCLAP::CmdLine cmd("IPCA Transport", ' ', "1");

  TCLAP::ValueArg<std::string> t1Arg("","t1", "Tree data file", true, "",
      "tree data file");
  cmd.add(t1Arg);

  TCLAP::ValueArg<std::string> t2Arg("","t2", "Tree data file", true, "",
      "tree data file");
  cmd.add(t2Arg);


  TCLAP::ValueArg<std::string> outArg("o","out", "data file name", true, "", "file to store results in"); 
  cmd.add(outArg);
  
  TCLAP::ValueArg<int> s1Arg("","s1", "number of scales of tree 1", false, -1, "integer"); 
  cmd.add(s1Arg);
  
  TCLAP::ValueArg<int> s2Arg("","s2", "number of scales of tree 2", false, -1, "integer"); 
  cmd.add(s2Arg);

  TCLAP::ValueArg<Precision> rArg("r","rFactor", "Multiplicative factor for size of neighborhoods to consider when moving to finer scale", false, 0, "real"); 
  cmd.add(rArg);

  TCLAP::ValueArg<int> dArg("d","Wd", "W_d distance computation", false, 1, "integer"); 
  cmd.add(dArg);

/*
  TCLAP::ValueArg<int> pArg("p","propagation", "Solution proagation across scale", false, 0, "0 or 1"); 
  cmd.add(pArg);
  */


  TCLAP::ValueArg<int> sArg("s","strategy", "Neighborhood expansion strategy 0 =  Potential, 1 = Refine, 2 = Expand", false, 0, "0, 1 or 2"); 
  cmd.add(sArg);

  
  TCLAP::ValueArg<int> nArg("n","neighborhood", "Neighborhood type 0 = Generic, 1 = Relative", false, 0, "0 or 1"); 
  cmd.add(nArg);



 // TCLAP::SwitchArg mcfArg("m","mcf", "Use network simplex", false, 0); 
 // cmd.add(mcfArg);

  try{ 
    cmd.parse( argc, argv );
  } 
  catch (TCLAP::ArgException &e){ 
    std::cerr << "error: " << e.error() << " for arg " << e.argId() << std::endl; 
    return -1;
  }


  std::string t1FileName = t1Arg.getValue();
  std::string t2FileName = t2Arg.getValue();

  std::string outFileName = outArg.getValue();
  int nScales1 = s1Arg.getValue();
  int nScales2 = s2Arg.getValue();
  int p = dArg.getValue();
  //int propType = pArg.getValue();
  int sType = sArg.getValue();
  int nType = nArg.getValue();
  //bool mcf = mcfArg.getValue();

/*
  MultiscaleTransportGLPK<Precision>::PropagationType pType =
    MultiscaleTransportGLPK<Precision>::GramSchmidt;
  if(propType == 1){
    std::cout << "LP propagation" << std::endl;
    pType = MultiscaleTransportGLPK<Precision>::LP;
  }
*/

  LPBaseParameters<Precision> params;

  params.refinement = LPBaseParameters<Precision>::POTENTIAL;
  if( sType == 1 ){
    params.refinement = LPBaseParameters<Precision>::REFINE;
  }
  else if( sType == 2 ){
    params.refinement = LPBaseParameters<Precision>::EXPAND;
  }

  params.expansionFactor = rArg.getValue();




  IPCATree<Precision> t1;
  std::ifstream t1File(t1FileName.c_str(), std::ios_base::in | std::ios_base::binary);
  t1.unflatten(t1File);
  t1File.close();
  
  IPCATree<Precision> t2;
  std::ifstream t2File(t2FileName.c_str(), std::ios_base::in | std::ios_base::binary);
  t2.unflatten(t2File);
  t2File.close();


  IPCAGWT<Precision> gwt1;
  gwt1.setTree(&t1);

  IPCAGWT<Precision> gwt2;
  gwt2.setTree(&t2);

  EuclideanMetric<Precision> *metric = new EuclideanMetric<Precision>();
  NodeDistance<Precision> *d = new CenterNodeDistance<Precision>( metric);
  //NodeDistance<Precision> *d =  new WassersteinNodeDistance<Precision>();
  //
  t1.computeRadii(d);
  t1.computeLocalRadii(d);
  
  t2.computeRadii(d);
  t2.computeLocalRadii(d);

  GMRANeighborhood<Precision> *nh1;
  GMRANeighborhood<Precision> *nh2;
  if(nType == 0){
   nh1 = new GenericGMRANeighborhood<Precision>(t1, d);
   nh2 = new GenericGMRANeighborhood<Precision>(t2, d);
  }
  else{
    nh1 = new RelativeGMRANeighborhood<Precision>(t1, d);
    nh2 = new RelativeGMRANeighborhood<Precision>(t2, d);
  }

  std::vector<double> weights;

  std::vector< MultiscaleTransportLevel<Precision> * > t1Levels =
    GMRAMultiscaleTransportLevel<Precision>::buildTransportLevels(*nh1, weights,
        true);

  std::vector< MultiscaleTransportLevel<Precision> * > t2Levels =
    GMRAMultiscaleTransportLevel<Precision>::buildTransportLevels(*nh2, weights,
        true);
  
  MultiscaleTransport<Precision> *transport;
  transport = new MultiscaleTransportCPLEXnetwork<Precision>( params );
  //transport = new MultiscaleTransportGLPK<Precision>(params);

  //SinkhornParameters<Precision> sparams;
  //transport = new MultiscaleSinkhornTransport<Precision>(sparams);
     
  std::vector< TransportPlan<Precision> * > sols = transport->solve( t1Levels,
      t2Levels, p, nScales1, nScales2);

  
  FortranLinalg::DenseVector< Precision > dist(sols.size());
  FortranLinalg::DenseVector< int > vars(sols.size());
  
  for(unsigned int i=0; i < sols.size(); i++ ){
    TransportPlan<Precision> *s = sols[i];
    dist(i) = s->cost;
    vars(i) = s->getNumberOfPaths();
    delete s;
  }

  std::stringstream ss;
  ss << outFileName << ".data";
  FortranLinalg::LinalgIO<Precision>::writeVector(ss.str(), dist);
  
  std::stringstream ss2;
  ss2 << outFileName << "-nVariables.data";
  FortranLinalg::LinalgIO<int>::writeVector(ss2.str(), vars);


  for(unsigned int i=0; i < t1Levels.size(); ++i){
    delete t1Levels[i];
  }
  
  for(unsigned int i=0; i < t2Levels.size(); ++i){
    delete t2Levels[i];
  }

  t1Levels.clear();
  t2Levels.clear();

  dist.deallocate();
  vars.deallocate();
  delete d;
  delete metric;
  delete transport;
  delete nh1;
  delete nh2;

  return 0;

}
