## d3.js client visualizations backed by Python-based data servers

These are a couple related projects which have [d3.js][] front end interactive
visualizations backed up by servers which load in data and process it on
demand to send to the clients. The idea is that even if the data is large
and cumbersome, lightweight visualizations can be used and efficiently delivered
to the client to explore the data. The server code uses Python with [Autobahn][] and [CherryPy][]
to write the lightweight servers so I can use fast [NumPy][] and [SciPy][] routines for data manipulation
and linear algebra.

[d3.js]: http://d3js.org/ "d3.js"
[Autobahn]: http://autobahn.ws "Aubobahn"
[CherryPy]: http://cherrypy.org "CherryPy"
[NumPy]: http://numpy.org "NumPy"
[SciPy]: http://www.scipy.org "SciPy"

This work is being done in collaboration with [Mauro Maggioni][mauro], [Miles Crosskey][miles],
and [Samuel Gerber][sam] at [Duke University][duke].

[mauro]: http://www.math.duke.edu/~mauro/ "Mauro Maggioni"
[gmra]: http://www.math.duke.edu/~mauro/code.html#GMRA "GMRA"
[sam]: http://www.math.duke.edu/~sgerber/ "Sam Gerber"
[miles]: https://www.researchgate.net/profile/Miles_Crosskey "Miles Crosskey"
[duke]: http://www.duke.edu "Duke University"

## Directories

### IPCA

The IPCA explorer is an ongoing project navigate data "sketches" generated with
[Geometric Multi-Resolution Analysis (GMRA)][gmra] through a web-based interface. 
The visualization combines an icicle view, which represents the hierarchical, low-dimensional breakdown 
of the data at various scales, plus a new type of scatterplot representing the distribution 
of the data at that scale, projected into the space of the parent distribution.

### path

Moving further with the simplified scatterplot idea, but now for following paths
in an abstract, potentially nonlinear and high-dimensional space which is represented 
locally by low-dimensional linear spaces.

### gmra_src

The source code for Sam Gerber's GMRA routines. The only one we use right now
for this project is CreateIPCATree. You need to use the [CMake][] build system to
compile.

[CMake]: http://www.cmake.org "CMake"





