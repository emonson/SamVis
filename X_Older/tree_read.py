#     void unflatten(std::ifstream &file){
#       file.read( (char*) &epsilon, sizeof(TPrecision) ) ;
#       file.read( (char*) &d, sizeof(unsigned int) )  ;
#       unsigned int m;   
#       file.read( (char*) &m, sizeof(unsigned int) );   
#       file.read( (char*) &minPoints, sizeof(int) );   
# 
#       std::list<IPCANode<TPrecision> *> nodes;
# 
#       IPCANode<TPrecision> *cur = NULL;
#       while( !file.eof() ){
# 
#         int nPhi = 0;
#         file.read((char*)&nPhi, sizeof(int));
#          
#         DenseMatrix<TPrecision> phi(m, nPhi);
#         file.read((char*)phi.data(), nPhi*m*sizeof(TPrecision));
# 
#         DenseVector<TPrecision> sigma(nPhi);
#         file.read((char*)sigma.data(), nPhi*sizeof(TPrecision));
# 
#         DenseVector<TPrecision> center(m);
#         file.read((char*)center.data(), m*sizeof(TPrecision));
# 
#         DenseVector<TPrecision> mse(d+1);
#         file.read((char*)mse.data(), (d+1)*sizeof(TPrecision));
# 
#         DenseVector<TPrecision> dir(m);
#         file.read((char*)dir.data(), m*sizeof(TPrecision));
#         
#         TPrecision a = 0;
#         file.read((char*)&a, sizeof(TPrecision) );
#         
#         int nPoints;
#         file.read( (char*) &nPoints, sizeof(int) );
#         std::vector<int> pts(nPoints);
#         file.read((char*)pts.data(), nPoints*sizeof(int) );
# 
#         TPrecision r;
#         file.read((char*) &r, sizeof(TPrecision) );
#         
#         bool isLeaf = false;
#         file.read((char*) &isLeaf, sizeof(bool) );
#         
# 
#         IPCANode<TPrecision> *node = new IPCANode<TPrecision>();
#         if(cur == NULL){
#           this->setRoot(node);
#         }
# 
#         node->r = r;
#         node->phi = phi;
#         node->sigma = sigma;
#         node->dir = dir;
#         node->a = a;
#         node->mse = mse;
#         node->center = center;
#         node->indices = pts;
# 
#         node->sigma2 = DenseVector<TPrecision>(sigma.N());
#         for(int i=0; i<sigma.N(); i++){
#           node->sigma2(i) = sigma(i) * sigma(i);
#         }
# 
#         if(cur != NULL){
#           if(!isLeaf){
#             nodes.push_back(node);
#           }
#           if(cur->getChildren().size() == 2){
#             cur = nodes.front();
#             nodes.pop_front();
#           }
#           cur->getChildren().push_back(node);
#         }
#         else{
#           cur = node;
#         }
#         file.peek();
#       }
# 
#     };

import struct
import numpy as N
import collections as C
import pprint
import json

f = open('../test/mnist12_d2.ipca', 'rb')

# Size of header
#       file.read( (char*) &epsilon, sizeof(TPrecision) ) ;
#       file.read( (char*) &d, sizeof(unsigned int) )  ;
#       file.read( (char*) &m, sizeof(unsigned int) );   
#       file.read( (char*) &minPoints, sizeof(int) );   

# Tree header
r_header = f.read(8 + 4 + 4 + 4)
(epsilon, d, m, minPoints) = struct.unpack("dIIi", r_header)

tree_root = None
nodes = C.deque()
cur = None
lite_tree_root = None
lite_nodes = C.deque()
lite_cur = None

id = 0

# Size of each segment
#         file.read((char*)phi.data(), nPhi*m*sizeof(TPrecision)); nPhi*m*8 +
#         file.read((char*)sigma.data(), nPhi*sizeof(TPrecision)); nPhi*8 +
#         file.read((char*)center.data(), m*sizeof(TPrecision)); m*8 +
#         file.read((char*)mse.data(), (d+1)*sizeof(TPrecision)); (d+1)*8 +
#         file.read((char*)dir.data(), m*sizeof(TPrecision)); m*8 +
#         file.read((char*)&a, sizeof(TPrecision) ); 8 +
#         file.read( (char*) &nPoints, sizeof(int) ); 4 +
#         file.read((char*)pts.data(), nPoints*sizeof(int) ); nPoints*4 +
#         file.read((char*) &r, sizeof(TPrecision) ); 8 +
#         file.read((char*) &isLeaf, sizeof(bool) ); 1

try:
	r_nPhi = f.read(4)
	while r_nPhi:
		(nPhi,) = struct.unpack("i", r_nPhi)
		phi = N.matrix(N.array(struct.unpack("d"*nPhi*m, f.read(8*nPhi*m))).reshape((nPhi,m)))
		sigma = N.array(struct.unpack("d"*nPhi, f.read(8*nPhi)))
		center = N.array(struct.unpack("d"*m, f.read(8*m)))
		mse = N.array(struct.unpack("d"*(d+1), f.read(8*(d+1))))
		dir = N.array(struct.unpack("d"*m, f.read(8*m)))
		(a,) = struct.unpack("d", f.read(8))
		(nPoints,) = struct.unpack("i", f.read(4))
		pts = N.array(struct.unpack("i"*nPoints, f.read(4*nPoints)))
		(r,) = struct.unpack("d", f.read(8))
		(isLeaf,) = struct.unpack("?", f.read(1))
		
		
#         IPCANode<TPrecision> *node = new IPCANode<TPrecision>();
#         if(cur == NULL){
#           this->setRoot(node);
#         }

		node = {}
		node['id'] = id
		node['children'] = C.deque()
		lite_node = {}
		lite_node['id'] = id
		lite_node['children'] = C.deque()
		if isLeaf:
			lite_node['value'] = nPoints
		
		if cur == None:
			tree_root = node
			lite_tree_root = lite_node

#         node->r = r;
#         node->phi = phi;
#         node->sigma = sigma;
#         node->dir = dir;
#         node->a = a;
#         node->mse = mse;
#         node->center = center;
#         node->indices = pts;
# 
#         node->sigma2 = DenseVector<TPrecision>(sigma.N());
#         for(int i=0; i<sigma.N(); i++){
#           node->sigma2(i) = sigma(i) * sigma(i);
#         }

		node['r'] = r
		node['phi'] = phi
		node['sigma'] = sigma
		node['dir'] = dir
		node['a'] = a
		node['mse'] = mse
		node['center'] = center
		node['indices'] = pts
		node['sigma2'] = sigma*sigma

# 
#         if(cur != NULL){
#           if(!isLeaf){ // node not isLeaf
#             nodes.push_back(node);
#           }
#           if(cur->getChildren().size() == 2){ // children full
#             cur = nodes.front();
#             nodes.pop_front();
#           }
#           cur->getChildren().push_back(node);
#         }
#         else{
#           cur = node;
#         }
#         file.peek();
#       }		
		
		# if previously read node is not empty. 
		# i.e. if node != root
		if cur != None:
		
			# if just-read node is not a leaf
			if not isLeaf:
				# put just-read node in the deque to be visited later
				nodes.append(node)
				lite_nodes.append(lite_node)
			
			# if children array of cur (previously read) is full
			# (I think an alternative to this if not dealing with a binary tree
			#   would be to keep track of everyone's parent node ID and check here 
			#   whether cur is the parent of node)
			if len(cur['children']) == 2:
				cur = nodes.popleft()
				lite_cur = lite_nodes.popleft()
			
			# fill up cur's children list
			cur['children'].append(node)
			lite_cur['children'].append(lite_node)
			
		else:
			cur = node
			lite_cur = lite_node
		
		r_nPhi = f.read(4)
		id = id + 1

finally:
	f.close()

# Clear out empty children

MODE = 'breadth_first'
# MODE = 'depth_first'

# Iterative traversal
#   Note: for Python deque, 
#	      extendleft / appendleft --> [0, 1, 2] <-- extend / append
#				               popleft <--             --> pop

nodes = C.deque()
nodes.appendleft(lite_tree_root)

while len(nodes) > 0:
	if MODE == 'breadth_first':
		current_node = nodes.pop()
	elif MODE == 'depth_first':
		current_node = nodes.popleft()
	else:
		break
		
	# Calculate something on the current node
	if 'children' in current_node:
		if len(current_node['children']) == 0:
			del current_node['children']
		else:
			current_node['children'] = list(current_node['children'])
	
	if 'children' in current_node:
		nodes.extendleft(current_node['children'])
		# for child in current_node['children']:
		# 	nodes.appendleft(child)

f = open('mnist12.json', 'w')
f.write(json.dumps(lite_tree_root))
f.close()

# DEBUG
# pprint.pprint(lite_tree_root)
# print json.dumps(lite_tree_root, indent=2)