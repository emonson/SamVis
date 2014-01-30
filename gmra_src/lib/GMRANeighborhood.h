#ifndef GMRANEIGHBORHOOD_H
#define GMRANEIGHBORHOOD_H

#include "GMRATree.h"

#include <list>
#include <set>
#include <vector>


#include "EuclideanMetric.h"
#include "NodeDistance.h"






template <typename TPrecision>
class GMRANeighborhood{
  
  protected:
    GMRATree<TPrecision> &tree;
    NodeDistance<TPrecision> *dist;

  public:

    GMRANeighborhood(GMRATree<TPrecision> &t, NodeDistance<TPrecision> *d) : tree(t), dist(d){
    };

    virtual ~GMRANeighborhood(){};

    typedef typename std::pair< TPrecision, GMRANode<TPrecision> * >  Neighbor;
    typedef typename std::list< Neighbor > NeighborList;
    typedef typename NeighborList::iterator NeighborListIterator;
    

    virtual int neighbors(GMRANode<TPrecision> *node, TPrecision epsilon,
         NeighborList &result, int stopScale=1000000) const = 0;

    GMRATree<TPrecision> &getTree(){
      return tree;
    };


    NodeDistance<TPrecision> *getNodeDistance(){
      return dist;
    }
};





//Neighborhood search using only the GMRA tree structure
template <typename TPrecision>
class GenericGMRANeighborhood : public GMRANeighborhood<TPrecision>{
  
  private:
    typedef typename GMRANeighborhood<TPrecision>::Neighbor Neighbor;
    typedef typename GMRANeighborhood<TPrecision>::NeighborList NeighborList;
    typedef typename NeighborList::iterator NeighborListIterator;
    
    typedef typename GMRANode<TPrecision>::NodeVector  NodeVector;
    typedef typename NodeVector::iterator NodeVectorIterator;
    
  
  
  public:

    int neighbors(GMRANode<TPrecision> *x, TPrecision eps, NeighborList
        &collected, int stopScale=10000000) const{

      
      NeighborList nodes;
      GMRANode<TPrecision> *root = this->tree.getRoot();
      TPrecision d = this->dist->distance(x, root);
      nodes.push_back( Neighbor(d, root) );
     
      int nVisited =0; 
      int nCollected = 0;
      while( !nodes.empty() ){
        
        nVisited++;
        Neighbor &n = nodes.front();

        NodeVector kids = n.second->getChildren();
        
        if( n.second->isStop() || n.second->getScale() == stopScale || kids.size() == 0 ){
          if( n.first <= eps ){
            collected.push_back( n );
            nCollected++;
          }
        }
        else if( n.second->getScale() < stopScale ) {
          //For each kid check if nearest neighbors within epsilon are possible.
          for( NodeVectorIterator it = kids.begin(); it != kids.end(); ++it ){
            GMRANode<TPrecision> *kid = *it;
            TPrecision d = this->dist->distance(kid, x);
            if( d <= kid->getRadius() + eps ){
              nodes.push_back( Neighbor(d, kid) );
            }
          }
        }
        nodes.pop_front();
      }

      //std::cout << nVisited << ", " << nCollected << std::endl;
      return nCollected;
    };


      

    GenericGMRANeighborhood(GMRATree<TPrecision> &t, NodeDistance<TPrecision>
        *d) : GMRANeighborhood<TPrecision>(t, d){ 
    };
   

/*
    //find all points within epsilon
    std::list<int> epsilon(GMRANode<TPrecision> &x, TPrecision eps){
      std::list<int> &result;
      NeighborList candidates;
      collectNodes(x, eps, candidates);
      for(NeighborListIterator it = candidates.begin(); it !=  candidates.end();
          ++it){
        std::list<int> &points = it->getPoints();
        for(std:list<int>::iterator pit = points.begin(); pit<points.end();
            ++pit){
          DenseVector<TPrecision> &p = tree.getPoint(*pit);
          dist->distance(p, x);
          if(d < eps){
            result.push_back(*pit);
          }
        }
      }

      return result;
    }; 
  */ 




};









#endif
