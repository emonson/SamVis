import collections as C

MODE = 'breadth_first'
# MODE = 'depth_first'

# Iterative traversal
#   Note: for Python deque, 
#	      extendleft / appendleft --> [0, 1, 2] <-- extend / append
#				               popleft <--             --> pop

nodes = C.deque()
nodes.appendleft(root_node)

while len(nodes) > 0:
	if MODE == 'breadth_first':
		current_node = nodes.pop()
	elif MODE == 'depth_first':
		current_node = nodes.popleft()
	else:
		break
		
	# Calculate something on the current node
	print current_node['id']
	
	if 'children' in current_node:
		nodes.extendleft(current_node['children'])
		# for child in current_node['children']:
		# 	nodes.appendleft(child)
