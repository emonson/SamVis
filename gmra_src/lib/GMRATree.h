#ifndef GMRATREE_H
#define GMRATREE_H

#include "DenseVector.h"
//#include "NodeDistance.h"

#include <list>
#include <vector>

#include <iostream>

template <typename TPrecision>
class NodeDistance;


//Node class
template <typename TPrecision>
class GMRANode{
  
  public:
    
    typedef typename std::vector< GMRANode<TPrecision> *> NodeVector;
    typedef typename NodeVector::iterator NodeVectorIterator;



  private:

    TPrecision radius;
    TPrecision localRadius;

    class CalculateRadius{
      private:
        NodeDistance<TPrecision> *d;
        GMRANode<TPrecision> *source;
        TPrecision radius;

        void visit(GMRANode<TPrecision> *node){
          if(node->getChildren().size() == 0){
            radius = std::max( d->distance(source, node), radius );
          }

          NodeVector kids = node->getChildren();
          for(int i=0; i<kids.size(); i++){
            visit(kids[i]);
          }
        };

      public:
        CalculateRadius(GMRANode<TPrecision> *n, NodeDistance<TPrecision> *dist) :
          d(dist), source(n), radius(0){
        };

        TPrecision calculateRadius(){
          radius = 0;
          visit(source);
          return radius;
        };

    };




  public:
    
    GMRANode(){
      radius = -1;
      localRadius = -1;
    };

    virtual ~GMRANode(){};

    //Get a list of children nodes for this node
    virtual NodeVector &getChildren() = 0;

    virtual GMRANode<TPrecision> *getParent() = 0;    
    virtual void setParent(GMRANode<TPrecision> *p) = 0;

    virtual int getScale() = 0;
    virtual void setScale(int s) = 0;

    virtual bool isStop() = 0;
    virtual void setStop(bool s) = 0;

    virtual GMRANode<TPrecision> *findDescendant(FortranLinalg::DenseVector<TPrecision> &x) = 0;

    //Get the points as indicies into the data matrix X used to construct the
    //tree
    virtual std::vector<int> &getPoints() = 0;
   

    //Partition representative and radius 
    virtual FortranLinalg::DenseVector<TPrecision> &getCenter() = 0;
    
    virtual TPrecision getRadius(){
      return radius;
    };



    virtual TPrecision getLocalRadius(){
      return localRadius;
    };



    void computeRadius(NodeDistance<TPrecision> *dist){
      CalculateRadius rc(this, dist);
      radius = rc.calculateRadius();
    };




    void computeLocalRadius(NodeDistance<TPrecision> *dist){
      NodeVector &kids = getChildren();
      localRadius = 0;
      for(int i=0; i<kids.size(); i++){
        localRadius = std::max(localRadius, dist->distance(this, kids[i]) );
      }

    };


    virtual void translate(FortranLinalg::DenseVector<TPrecision> &x) = 0;
    virtual void affine(FortranLinalg::DenseMatrix<TPrecision> &A) = 0;

};



//Node class
template <typename TPrecision>
class GMRANodeBase : public GMRANode<TPrecision>{
  
  public:

    typedef typename GMRANode<TPrecision>::NodeVector NodeVector;
    typedef typename NodeVector::iterator NodeVectorIterator;


  private:

    GMRANode<TPrecision> *parent;
    int scale;
    bool stop;


  public:
    
    GMRANodeBase(){
      parent = NULL;
      stop = false;
    };

    virtual ~GMRANodeBase(){
    };

    virtual GMRANode<TPrecision> *getParent(){
      return parent;
    };
    
    virtual void setParent(GMRANode<TPrecision> *p){
      parent = p;
    };

    virtual int getScale(){
      return scale;
    };

    virtual void setScale(int s){
      scale = s;
    };

    virtual bool isStop(){
      return stop;
    };

    virtual void setStop(bool s){
      stop = s;
    };


};



template <typename TPrecision>
class QueryGMRANode : public GMRANodeBase<TPrecision>{

  private: 
    FortranLinalg::DenseVector<TPrecision> &center;

  public:
 
    typedef typename GMRANode<TPrecision>::NodeVector NodeVector;
    typedef typename NodeVector::iterator NodeVectorIterator;
  
    QueryGMRANode(FortranLinalg::DenseVector<TPrecision> &c) : center(c){
    };

    FortranLinalg::DenseVector<TPrecision> &getCenter(){
      return center;
    };

    NodeVector &getChildren(){
      static NodeVector children;
      return children;
    };

    TPrecision getRadius(NodeDistance<TPrecision> *dist, bool recompute=false){
      return -1;
    };

    std::vector<int> &getPoints(){
      static std::vector<int> empty;
      return empty;
    };

}; 






template <typename TPrecision>
class GMRANodeDecorator : public GMRANode<TPrecision>{

  private:
    GMRANode<TPrecision> *node;

  public:
    typedef typename GMRANode<TPrecision>::NodeVector NodeVector;
    typedef typename NodeVector::iterator NodeVectorIterator;

    GMRANodeDecorator(GMRANode<TPrecision> *n) : node(n){
    };
    
    virtual ~ GMRANodeDecorator(){
      delete node;
    };


    //Get a list of children nodes for this node
    virtual NodeVector &getChildren() {
      return node->getChildren();
    };

    virtual GMRANode<TPrecision> *getParent(){
      return node->getParent();
    };

    virtual void setParent(GMRANode<TPrecision> *p) {
      node->setParent(p);
    };

    virtual int getScale(){
      return node->getScale();
    };

    virtual void setScale(int s){
      node->setScale(s);
    };

    virtual bool isStop(){
      return node->isStop();
    }
    virtual void setStop(bool s) {
      node->setStop(s);
    };

    virtual GMRANode<TPrecision> * findDescendant(FortranLinalg::DenseVector<TPrecision> &x){
      return node->findDescendant(x);
    };

    //Get the points as indicies into the data matrix X used to construct the
    //tree
    virtual std::vector<int> &getPoints(){
      return node->getPoints();
    };
   

    //Partition representative and radius 
    virtual FortranLinalg::DenseVector<TPrecision> &getCenter(){
      return node->getCenter();
    };

    virtual TPrecision getRadius(){
      return node->getRadius();
    };


    virtual TPrecision getLocalRadius(){
      return node->getLocalRadius();
    };


    virtual GMRANode<TPrecision> *getDecoratedNode(){
      return node;
    };

   
    virtual void translate(FortranLinalg::DenseVector<TPrecision> &x){
      node->translate(x);
    };


    virtual void affine(FortranLinalg::DenseMatrix<TPrecision> &A){
      node->affine(A);
    }; 

};






//Visitor for implementing actions on the GMRATree structure
template <typename TPrecision>
class Visitor{
  public:
    //
    virtual void visit(GMRANode<TPrecision> *node) = 0;

};






//Tree data structure
template <typename TPrecision>
class GMRATree{


private:

  GMRANode<TPrecision> *root;

  class DeleteVisitor : public Visitor<TPrecision>{
    public:
      //
      virtual void visit(GMRANode<TPrecision> *node){
        delete node;
      }
  };


public:

   
    virtual ~GMRATree(){
      DeleteVisitor del;
      depthFirstVisitor(&del);
    };

    //X an m * n matrix of n  m-dimensional data points stored in column major
    //order
    virtual void construct(TPrecision *X, int m, int n) = 0;
   
    //Add more points to the tree
    virtual void add(TPrecision *x) = 0;

    //Get Leaf node for data point x
    virtual std::vector<GMRANode<TPrecision> *> getLeafPath(TPrecision *x) = 0;
   
    virtual FortranLinalg::DenseVector<TPrecision> getPoint(int index) = 0;

    //Get root node of the tree
    GMRANode<TPrecision> *getRoot(){ 
      return root;
    };



    void setupParents(){
      
      //Set up parent pointers
      class SetParent : public Visitor<TPrecision>{
        public:
          //
          virtual void visit(GMRANode<TPrecision> *node){
            int scale = 1;
            GMRANode<TPrecision> *p = node->getParent();
            if(p != NULL){
              scale = node->getScale()+1;
            }
            else{
              node->setScale(0);
            }
            std::vector< GMRANode<TPrecision> * > &children = node->getChildren();
            for(unsigned int i=0; i<children.size(); i++){
              children[i]->setParent( node );
              children[i]->setScale( scale );
            }
          };
      
      };

      SetParent parenter;
      //Breadth first required  for setting scale correctly
      breadthFirstVisitor(&parenter);

    };


    void setRoot(GMRANode<TPrecision> *r){
      root= r;
    };



    //Pass each node in depth first order to the Visitor v
    void depthFirstVisitor(Visitor<TPrecision> *v){
      depthFirst( v, getRoot() );
    };



    //Pass each node in breadth first order to the Visitor v
    void breadthFirstVisitor(Visitor<TPrecision> *v){
      std::list<GMRANode<TPrecision> *> nodes;
      nodes.push_back( getRoot() );
      while(!nodes.empty()){
        GMRANode<TPrecision> *node = nodes.front();
        nodes.pop_front();

        v->visit(node);
        std::vector<GMRANode<TPrecision> *> children = node->getChildren();
        for(typename std::vector<GMRANode<TPrecision>*>::iterator it = children.begin(); it !=
           children.end(); ++it){ 
          nodes.push_back(*it);
        }
      }
    };


    void computeRadii(NodeDistance<TPrecision> *dist){
      class RadiusVisitor : public Visitor<TPrecision>{
        private:
          NodeDistance<TPrecision> *dist;
        public:

          RadiusVisitor(NodeDistance<TPrecision> *d):dist(d){
          };

          void visit(GMRANode<TPrecision> *node){
              node->computeRadius(dist);  
          };
      };

      RadiusVisitor vis(dist);
      this->breadthFirstVisitor(&vis);

    };

    void computeLocalRadii(NodeDistance<TPrecision> *dist){
      class RadiusVisitor : public Visitor<TPrecision>{
        private:
          NodeDistance<TPrecision> *dist;
        public:

          RadiusVisitor(NodeDistance<TPrecision> *d):dist(d){
          };

          void visit(GMRANode<TPrecision> *node){
              node->computeLocalRadius(dist);  
          };
      };

      RadiusVisitor vis(dist);
      this->breadthFirstVisitor(&vis);

    };


  private:

    void depthFirst(Visitor<TPrecision> *v, GMRANode<TPrecision> *node){
      std::vector<GMRANode<TPrecision> *> children = node->getChildren();
      for(typename std::vector< GMRANode<TPrecision>* >::iterator it = children.begin(); it !=
          children.end(); ++it){ 
         depthFirst( v, *it );
      }
      v->visit( node );
    };

};




#endif
