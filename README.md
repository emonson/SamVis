# d3.js client visualizations with number crunching data servers behind

These are a couple related projects which have [d3.js][] front end interactive
visualizations backed up by servers which load in data and process it on
demand to send to the clients. The idea is that even if the data is large
and cumbersome, lightweight visualizations can be used and efficiently delivered
to the client to explore the data. Right now most of the server code uses [CherryPy][]
to write the servers so I can use fast [NumPy][] routines for linear algebra, etc.

[d3.js]: http://d3js.org/ "d3.js"
[CherryPy]: http://cherrypy.org "CherryPy"
[NumPy]: http://numpy.org "NumPy"
