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
- [Autobahn | Python][autobahn] HTTP server + WAMP MVC websockets protocol (depends on [Twisted][])
- [NumPy][] for C-backed numerical processing and data structures
- [SciPy][] for linear algebra

[NumPy]: http://numpy.org "NumPy"
[SciPy]: http://www.scipy.org "SciPy"

**Anaconda:** For my Python distribution I'm using [Anaconda][anaconda]
from [Continuum Analytics](http://www.continuum.io/). It comes 
with lots of pre-installed modules, including [NumPy][] and [SciPy][], which are sometimes difficult
to install separately. It's free and available for all platforms,
and you can even get free academic licences for some "Add-Ons" to accelerate execution and I/O.
Also, it gets installed in your local home directory, so you don't need administrator
priviledges to install, and it won't overwrite or interfere with your other Python
installations. (The Anaconda executable directories must show up in your PATH before
the system Python installations, but that gets taken care of as part of the installation
process.)

Anaconda doesn't come with [Autobahn | Python][autobahn] or [CherryPy][], 
so I just install them with `pip`. You can use
available recipies for the `conda` package manager that comes with Anaconda, but I don't 
usually bother. [Twisted][], which [Autobahn][autobahn] depends on, can be installed with
`conda`, though.

*Installation:* Go to [https://store.continuum.io/cshop/anaconda/][anaconda] to download Anaconda for your platform
and run the installer. Then do:

```bash
conda install twisted
pip install anaconda
pip install cherrypy
```

[anaconda]: https://store.continuum.io/cshop/anaconda/
[CherryPy]: http://cherrypy.org
[autobahn]: http://autobahn.ws/python/
[Twisted]: https://twistedmatrix.com/trac/

**Homebrew:** Right now I'm using [homebrew][] to install all of the major
dependencies under OS X 10.8 that I possibly can, including [Git][]. 
See the [homebrew home page][homebrew]
for installation instructions for homebrew itself.

```bash
homebrew install git
```

[git]: http://git-scm.com/ "Git"
[homebrew]: http://brew.sh "Homebrew"

### JavaScript

All of the javascript dependencies are currently in the repository in the
libs directory off of the main repository:

- [d3.js](http://d3js.org/)
- [jQuery](http://jquery.com)
- [jQuery tiny pubsub](https://gist.github.com/cowboy/661855) for events publish/subscribe
- [parseUri](http://blog.stevenlevithan.com/archives/parseuri) for parsing the page URI
- [Autobahn | JS](http://autobahn.ws/js/) for WAMP MVC websockets communication

### Bootstrap CSS and font-awesome

I've been starting to use [Bower package manager][bower] to easily locally install all of my JavaScript 
and other web dependencies. Currently the IPCA Explorer still uses the above-mentioned JS libraries
in the libs directory, but I use [bower][] to install the [Bootstrap HTML/CSS/JS framework][bootstrap] 
for developing responsive (mobile-first) web applications and [Font Awesome][] for icons. When you type

```bash
bower install
```

the `bower.json` file in this directory is used, and dependencies get installed in a new
subdirectory called `bower_components`. (This will be ignored by git.)

[node]: http://nodejs.org/ "node.js"
[bower]: http://bower.io/ "Bower"
[bootstrap]: http://getbootstrap.com/ "Bootstrap"
[Font Awesome]: http://fortawesome.github.io/Font-Awesome/ "Font Awesome"


## Local Web Server Configuration

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

The data servers are set up to load multiple datasets into memory
so they can be served up when requested. There is a download link below with
some sample data. The data is stored in an [HDF5][] file. This allows us to
put all data and descriptive metadata into a single file, readable from almost
any programming language.

**HDF5 data:** The preliminary specification for the GMRA HDF5 file format is published
on the web in a [Google Doc here][hdf5spec].

**Sam binary converter:** There is a Python script, `sambinary_to_hdf5_converter.py`, which
will convert GMRA results generated by Sam's `gmra_src` code into the proper HDF5 format.

**Matlab converter:** Data generated with [Mauro's GMRA code][gmra] is converted to
the proper format with a Matlab script, `matlab_to_hdf5_write.m`, located in the `matlab`
directory of the man repository.

### Initial visualization page location

To see the visualizaiton and choose a dataset you will go to the server and port
you setup in the `server_conf.json` file, at the `ipca_explorer.html` page. For example:

[http://localhost:8080/ipca_explorer.html](http://localhost:8080/ipca_explorer.html)
[http://servername.sub.school.edu:8080/ipca_explorer.html](http://servername.sub.school.edu:8080/ipca_explorer.html)


## IPCA Example Data

There is a sample data file available [at this link][sample_data]. It is a zip-compressed
(6 Mb) HDF5 file of GMRA data processed in Matlab and converted to HDF5 with the Matlab script
in the `matlab` direcotry of the main repository.

[hdf5]: http://www.hdfgroup.org/HDF5/ "HDF5"
[hdf5spec]: https://docs.google.com/document/d/1h50SPiZSpFG40TA8OfnBAC2E6csVmbTiOt6ltM3FIfo/pub
[mnist]: http://yann.lecun.com/exdb/mnist/
[sample_data]: http://people.duke.edu/~emonson/mnist12_1k.hdf5.zip
