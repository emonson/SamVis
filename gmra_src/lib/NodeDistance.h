#ifndef NODEDISTANCE_H
#define NODEDISTANCE_H

#include "DenseVector.h"
#include "DenseMatrix.h"

#include "GMRATree.h"
#include "Metric.h"

template <typename TPrecision>
class GMRANode;


template < typename TPrecision >
class NodeDistance{

  public:
    virtual ~NodeDistance(){};

    virtual TPrecision distance(GMRANode<TPrecision> *n1, GMRANode<TPrecision> *n2) = 0;

};




template < typename TPrecision >
class CenterNodeDistance : public NodeDistance<TPrecision> {
  private:
    Metric<TPrecision> *metric;

  public:
    CenterNodeDistance(Metric<TPrecision> *m):metric(m){};

    ~CenterNodeDistance(){
    };

    TPrecision distance(GMRANode<TPrecision> *n1, GMRANode<TPrecision> *n2){
        using namespace FortranLinalg;
      DenseVector<TPrecision> &x1 = n1->getCenter();
      DenseVector<TPrecision> &x2 = n2->getCenter();
      return metric->distance(x1, x2);
    };
};




#endif
