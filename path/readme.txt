
This txt file describes everything you need to know about the various files contained in this folder.

d_info.mat - district info. 1127 length cell array where each struct contains the information for a local chart.

	fields in each chart struct:
	.index - global chart indices of neighbors. 
	(Aside: each neighbor will have a local index and a global index. index is a way of mapping from the local index to the global index. Even the point from which the chart was generated has its own local index. If you want to find the "center index" you can use the matlab code [cidx = find(d_info{i}.index == i)] )

	.lmks - location of landmarks corresponding to this district

	.TM - transfer matrix. used for transferring to neighboring district. use d_info{i}.TM(:,:,j) to transfer from chart i to chart j.

	.lmk_mean - means for transfer. again chart i to chart j is d_info{i}.lmk_mean(j,:)
	\\(see example code 1 below for transferring charts)\\
	.E - local eigenvectors of the covariance of lmk points.
	.U - matrix to transfer to global coordinates.
	.mu - mean to transfer to global coordinates.
	\\( see example code 2 below for transferring to global coords)\\
	.A - location of local marker points
	.v0 - set of reasonable initial velocities
	.sig, .F, .xi, .rvpC, .Iext, .ext, .Fxip are all used for local simulations
	.r - local radius (what i was calling epsilon)
	.t - local simulation time

\\ex. code 1 \\
% example code for transferring a point x with velocity v to a new chart. (mostly we only care about plotting positions though...)

% start at district index, transfer to chart corresponding to local index nnidx.
% dim is the local dimension of the chart.
                x = x - d_info{idx}.lmk_mean(nnidx,1:dim);
                x = x*d_info{idx}.TM(1:dim,1:dim,nnidx);
                v = v*d_info{idx}.TM(1:dim,1:dim,nnidx);
        
                % compute new local indices
                newidx = d_info{idx}.index(nnidx);
                cidx = find(d_info{newidx}.index == newidx);
                oldidx = find(d_info{newidx}.index == idx);
                idx = newidx; % update index
        
                x = x + d_info{idx}.lmk_mean(oldidx,1:dim);

\\ex. code 2 \\
% example code for transfer to global coordinates
        U = d_info{idx}.U(:,1:dim);
        x = x*U';
        x = x + d_info{idx}.mu(1:dim);
        v = v*U';


netpoints.mat - file containing original coordinates of points in the net. You could actually get this by using ex. code 2, and the .A field...

traj1.mat - file containing trajectory. includes the following:
	path_index - contains chart indices visited
	path - local coordinates of saved times
	t - times saved
	v_norm - norm of velocity at time t
	sim_opts - structure containing various options used

% code to plot a coarse grained path
plot(t,netpoints(path_index,:))

