#ifndef WASSERSTEINNODEDISTANCE_H
#define WASSERSTEINNODEDISTANCE_H

#include "DenseVector.h"
#include "DenseMatrix.h"

#include "NodeDistance.h"
#include "GWT.h"
#include "Wasserstein.h"
#include "Metric.h"





template < typename TPrecision >
class WassersteinNodeDistance : public NodeDistance<TPrecision> {

  private:
    Wasserstein<TPrecision> wstein;
  public:

    WassersteinNodeDistance(){};
    ~WassersteinNodeDistance(){};

    TPrecision distance(GMRANode<TPrecision> *n1, GMRANode<TPrecision> *n2){
        using namespace FortranLinalg;
      GWTNode<TPrecision> *gwt1 = dynamic_cast<GWTNode<TPrecision> *>( n1 );
      if(gwt1 == NULL){
        GMRANodeDecorator<TPrecision> *dec =
          dynamic_cast< GMRANodeDecorator<TPrecision> *>( n1 );
        while(dec != NULL && gwt1==NULL){
           n1 = dec->getDecoratedNode();
           gwt1 = dynamic_cast<GWTNode<TPrecision> *>( n1 ); 
           dec = dynamic_cast< GMRANodeDecorator<TPrecision> *>( n1 );

        }
      }

      GWTNode<TPrecision> *gwt2 = dynamic_cast<GWTNode<TPrecision> *>( n2 );
      if(gwt2 == NULL){
        GMRANodeDecorator<TPrecision> *dec =
          dynamic_cast< GMRANodeDecorator<TPrecision> *>( n2 );
        while(dec != NULL && gwt2==NULL){
           n2 = dec->getDecoratedNode();
           gwt2 = dynamic_cast<GWTNode<TPrecision> *>( n2 ); 
           dec = dynamic_cast< GMRANodeDecorator<TPrecision> *>( n2 );

        }
      }


      DenseVector<TPrecision> sigma12 =
        Linalg<TPrecision>::Copy(gwt1->getSigma());
      DenseVector<TPrecision> sigma22 =
        Linalg<TPrecision>::Copy(gwt2->getSigma());
      for(int i=0; i< sigma12.N(); i++){
        sigma12(i) *= sigma12(i);
      }
      for(int i=0; i< sigma22.N(); i++){
        sigma22(i) *= sigma22(i);
      }

      
      TPrecision d = wstein.distance( gwt1->getPhi(), sigma12,
          gwt1->getCenter(), gwt2->getPhi(), sigma22, gwt2->getCenter() );
      sigma12.deallocate();
      sigma22.deallocate();
      return d;
    };

};




#endif

