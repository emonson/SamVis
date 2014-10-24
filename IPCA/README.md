## IPCA Explorer

The IPCA explorer is an ongoing project navigate data "sketches" generated with
[Geometric Multi-Resolution Analysis (GMRA)][gmra] through a web-based interface. 
The visualization combines an icicle view, which represents the hierarchical, low-dimensional breakdown 
of the data at various scales, plus a new type of scatterplot representing the distribution 
of the data at that scale, projected into the space of the parent distribution.

This is work with [Mauro Maggioni][mauro] and [Samuel Gerber][sam] at Duke University.

[mauro]: http://www.math.duke.edu/~mauro/
[gmra]: http://www.math.duke.edu/~mauro/code.html#GMRA
[sam]: http://www.math.duke.edu/~sgerber/


## Dependencies

### Python

The modules required beyond that of the standard library are:

- [CherryPy][] for a small HTTP server
- [Autobahn | Python][autobahn] WAMP websockets protocol, which depends on [Twisted][]
- [NumPy](http://numpy.org) for C-backed numerical processing and data structures
- [SciPy](http://www.scipy.org) for linear algebra

**Anaconda:** For my Python distribution I'm using [Anaconda][anaconda]
from [Continuum Analytics](http://www.continuum.io/). It comes 
with lots of pre-installed modules, including NumPy and SciPy, which are sometimes difficult
to install separately. It's free and available for all platforms,
and you can even get free academic licences for some "Add-Ons" to accelerate execution and I/O.
Also, it gets installed in your local home directory, so you don't need administrator
priviledges to install, and it won't overwrite or interfere with your other Python
installations. (The Anaconda executable directories must show up in your PATH before
the system Python installations...)

Anaconda doesn't come with [Autobahn | Python][autobahn] or [CherryPy][], 
so I just install them with `pip`. You can use
available recipies for the `conda` package manager that comes with Anaconda, but I don't 
usually bother. [Twisted][], which [Autobahn][autobahn] depends on, can be installed with
`conda`, though.

*Installation:* Go to [https://store.continuum.io/cshop/anaconda/][anaconda] to download Anaconda for your platform
and run the installer. Then do:

```
conda install twisted
pip install anaconda
pip install cherrypy
```

[anaconda]: https://store.continuum.io/cshop/anaconda/
[CherryPy]: http://cherrypy.org
[autobahn]: http://autobahn.ws/python/
[Twisted]: https://twistedmatrix.com/trac/


### JavaScript

All of the javascript dependencies are in the repository in the
libs directory off of the main repository, but here are a list of the currently used libraries:

- [d3.js](http://d3js.org/)
- [jQuery](http://jquery.com)
- [jQueryUI](http://jqueryui.com) subset including only the slider for now
- [jQuery tiny pubsub](https://gist.github.com/cowboy/661855) for events publish/subscribe
- [parseUri](http://blog.stevenlevithan.com/archives/parseuri) for parsing the page URI

**Homebrew:** Right now I'm using [homebrew](http://brew.sh) to install all of the major
dependencies under OS X 10.8 that I possibly can.

[git]: http://git-scm.com/ "Git"
[node]: http://nodejs.org/ "node.js"
[bower]: http://bower.io/ "Bower"


## Local Web Server Name Configuration

The file `server_conf_example.json` is an example of the file which sets the local server
name for both the Javascript and Python scripts. Make a copy and call it `server_conf.json`.
The latter is included in this project's `.gitignore` file, so changes you make
to your server configuration won't get recognized as changes to the project
source, plus your server-specific configuration values won't get overwritten
when you pull changes to the repository.

This config lets you set the port number used for the server so it won't conflict with
servers being used for other projects. 
The `path_web_dir` variable should reflect the symlink name
you set up in your Sites directory. See the "Symlink to project path" section
below. In that example the variables would be set as `SamVis/path`. 
Also see below for the reverse proxy setup instructions. 

Additionally, you use the `server_conf.json` file to set the path to the data
relative to the html and JS files for this project. 
It is fine to have this path outside of the directories that
can be served up by your web server. 

*NOTE:* If you put the port value at 9000, the scripts will expect the reverse 
proxy to be at `http://servername.sub.school.edu/remote9000/` 
*(i.e. that string, "remote", is hard-coded into
the scripts, so use that actual string in your reverse proxy name)*


## Data directory and files 

Right now the projects are set up to load multiple datasets into memory
so they can be served up when requested. There is a download link below with
some sample data. 

**HDF5 data:** The preliminary specification for the GMRA HDF5 file format is published
on the web in a [Google Doc here][hdf5spec].

**Matlab converter:**

**Resource Index:** When you start up the HTTP-based IPCA tree
server it will look for directories in the `ipca_data_dir` and put links
to visualizations at the address

`http://servername.sub.school.edu/remote9002/resource_index`

where that server name and 9002 port number you've set in the
`server_conf.json` file. What you'll see is a list of names the same as
your data directory names, but they'll all be links to visualization
pages.


## IPCA Example Data


[hdf5spec]: https://docs.google.com/document/d/1h50SPiZSpFG40TA8OfnBAC2E6csVmbTiOt6ltM3FIfo/pub
[mnist]: http://yann.lecun.com/exdb/mnist/
[sample_data]: http://people.duke.edu/~emonson/mnist12_1k.hdf5.zip