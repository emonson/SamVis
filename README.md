## d3.js client visualizations with number crunching data servers behind

These are a couple related projects which have [d3.js][] front end interactive
visualizations backed up by servers which load in data and process it on
demand to send to the clients. The idea is that even if the data is large
and cumbersome, lightweight visualizations can be used and efficiently delivered
to the client to explore the data. Right now most of the server code uses [CherryPy][]
to write the servers so I can use fast [NumPy][] routines for linear algebra, etc.

[d3.js]: http://d3js.org/ "d3.js"
[CherryPy]: http://cherrypy.org "CherryPy"
[NumPy]: http://numpy.org "NumPy"

This work is being done in collaboration with Mauro Maggioni, Miles Crosskey,
and Sam Gerber at Duke University.

## Directories
------------

### HTTP

The HTTP directory contains a project which involves loading in data which have been
decomposed with a technique related to Geometric Wavelets. The visualizations
combine an icicle view which represents the hierarchical breakdown of the data
(MNIST handwritten 1s and 2s, in this case), at various scales, plus a new type
of scatterplot representing the distribution of the data at that scale.

### path

Moving further with the simplified scatterplot idea, but now for following paths
in an abstract, potentially nonlinear and high-dimensional space which is represented 
locally by low-dimensional linear spaces.

### WebSocket

Just tests of [Autobahn][] and [ws4py][] websockets implementations for passing
arrays of data back and forth between client and server. No integration with the 
main visualizations for now.

[Autobahn]: http://autobahn.ws "Autobahn"
[ws4py]: https://github.com/Lawouach/WebSocket-for-Python "ws4py"
