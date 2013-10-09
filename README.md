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

### HTTP

The HTTP directory contains a project which involves loading in data which have been
decomposed with a technique call Geometric Multi-Resolution Analysis (GMRA). The 
visualizations combine an icicle view which represents the hierarchical breakdown 
of the data (MNIST handwritten 1s and 2s, in this case – see below for data), 
at various scales, plus a new type of scatterplot representing the distribution 
of the data at that scale.

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


## Dependencies

*Python:* The modules required beyond that of the standard library are:

- [numpy](http://www.numpy.org "Numpy")
- [simplejson](https://github.com/simplejson/simplejson)
- [CherryPy][]

Right now I'm using [homebrew](http://brew.sh) to install all of the major
dependencies under OS X 10.8 that I possibly can, including Python, originally
because I was having trouble bundling Python apps with the system Python.

I've never had any issues installing simplejson or CherryPy using pip. 
Numpy I sometimes have problems installing using pip, but it works fine
to clone the [numpy git repository](https://github.com/numpy/numpy.git), then
do `python setup.py install` in the main directory.

*Javascript:* All of the javascript dependencies are in the repository in the
libs directory, but here are a list of the currently used libraries:

- [d3.js][]
- [jQuery](http://jquery.com)
- [jQueryUI](http://jqueryui.com) subset including only the slider for now
- [jQuery tiny pubsub](https://gist.github.com/cowboy/661855) for events publish/subscribe


## Local Web Server Name Configuration

There is a file called server_example.json in the root of the repository. This
is the file which sets the local server name for all of the Javascript and Python
scripts in both the HTTP and path directories. This lets you also set the port
number used for the IPCA visualizations in HTTP and the simulated path visualizations
in path. See below for the reverse proxy setup instructions. 

*NOTE:* The scripts will expect the reverse proxy to be at server_name/remote9000/ 
if you put the port value at 9000. (i.e. that string, "remote", is hard-coded into
the scripts, so use that actual string in your reverse proxy name)


## Apache Web Server Configuration

The data servers I build using CherryPy run on a different port than the web server
which serves up the HTML pages. This means that an ajax call from the page to the
data server is considered a cross-domain request, which is not allowed under the
[same-origin policy](https://en.wikipedia.org/wiki/Same_origin_policy). 

At first I solved this by creating a PHP script for each type of call,
which would just act as a proxy -- requesting the data from the server
and passing it along to the javascript call (you can see this in the
repository history). 

Then, someone told me I could set up a "reverse proxy" in Apache which
would create a URL path that would pass things along to the other port
in the background. In my `/etc/apache2/users/username.conf` file, I add
lines like this:

```
ProxyPass /remote9000/  http://servername.sub.duke.edu:9000/
ProxyPass /remote9002/  http://servername.sub.duke.edu:9002/
```

which lets me just make a call to something like

`http://servername.sub.duke.edu/remote9000/allellipses?basis=1`

instead of 

`http://servername.sub.duke.edu:9000/allellipses?basis=1`

in my ajax call, which is considered "same origin".


## Additional Example Data

The IPCA visualizations in the HTTP directory use data from the [MNIST database of
handwritten digits](http://yann.lecun.com/exdb/mnist/). Specifically, the set of
images of handwritten 1s and 2s from the training set was used. You can download
the preprocessed data files (IPCA output plus labels) from [this repository](http://people.duke.edu/~emonson/MNIST12.zip)

As written, the Python server code in HTTP relies on those files being in a directory
called `test` sitting in the same directory level as this repository. 
`../../test/mnist12.ipca`, etc.
