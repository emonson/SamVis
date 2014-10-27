function X1 = MNIST_image_flip(X0)
% In the natural data orientation, when you send the MNIST images
% to the GUIs, they end up rotated 90 deg and flipped from the natural
% viewing orientation. This takes in [784 x n_points] and returns
% the same, but internally the vectors are rearranged.

% Rotate images for GUI
yy = reshape(X0,28,28,[]);
yy1 = permute(yy,[2 1 3]);
yy2 = flip(yy1,2);
X1 = reshape(yy2,784,[]);

end