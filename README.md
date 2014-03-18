## d3.js client visualizations backed by Python-based data servers

These are a couple related projects which have [d3.js][] front end interactive
visualizations backed up by servers which load in data and process it on
demand to send to the clients. The idea is that even if the data is large
and cumbersome, lightweight visualizations can be used and efficiently delivered
to the client to explore the data. Right now most of the server code uses [CherryPy][]
to write the servers so I can use fast [NumPy][] and [SciPy][] routines for linear algebra, etc.

[d3.js]: http://d3js.org/ "d3.js"
[CherryPy]: http://cherrypy.org "CherryPy"
[NumPy]: http://numpy.org "NumPy"
[SciPy]: http://www.scipy.org "SciPy"

This work is being done in collaboration with Mauro Maggioni, Miles Crosskey,
and Sam Gerber at Duke University.


## Directories

### IPCA

The IPCA directory contains a project which involves loading in data which have been
decomposed with a technique call Geometric Multi-Resolution Analysis (GMRA). The 
visualizations combine an icicle view which represents the hierarchical breakdown 
of the data (MNIST handwritten 1s and 2s, in this case – see below for data), 
at various scales, plus a new type of scatterplot representing the distribution 
of the data at that scale.

### path

Moving further with the simplified scatterplot idea, but now for following paths
in an abstract, potentially nonlinear and high-dimensional space which is represented 
locally by low-dimensional linear spaces.

### gmra_src

The source code for Sam Gerber's GMRA routines. The only one we use right now
for this project is CreateIPCATree. You need to use the [CMake][] build system to
compile.

[CMake]: http://www.cmake.org "CMake"

### WebSocket

Just tests of [Autobahn][] and [ws4py][] websockets implementations for passing
arrays of data back and forth between client and server. No integration with the 
main visualizations for now.

[Autobahn]: http://autobahn.ws "Autobahn"
[ws4py]: https://github.com/Lawouach/WebSocket-for-Python "ws4py"

## Dependencies

### Python

The modules required beyond that of the standard library are:

- [NumPy][]
- [SciPy][]
- [CherryPy][]

**Homebrew:** Right now I'm using [homebrew](http://brew.sh) to install all of the major
dependencies under OS X 10.8 that I possibly can, including Python, originally
because I was having trouble bundling Python apps with the system Python.

I've never had any issues installing CherryPy using pip. 
I sometimes have problems installing both Numpy and SciPy using pip, but it works fine
to clone the [numpy git repository](https://github.com/numpy/numpy.git), 
and the [sci git repository](https://github.com/scipy/scipy.git), then
do `python setup.py install` in the main directory of each.

**Anaconda:** An attractive alternative for a Python distribution with lots of pre-installed
modules, including NumPy and SciPy, is [Anaconda](https://store.continuum.io/cshop/anaconda/)
from [Continuum Analytics](http://www.continuum.io/). It's free and available for all platforms,
and you can even get free academic licences for some "Add-Ons" to accelerate execution.

Right now Anaconda doesn't come with CherryPy. You can install it with `pip`, but it won't 
be managed in the same way as the rest of the Anaconda packages. 
To install it using the `conda` build system you need to do something like this
using the [conda-recipes](https://github.com/conda/conda-recipes):

```bash
cd anaconda/
git clone git@github.com:ContinuumIO/conda-recipes.git
conda build conda-recipes/cherrypy
cd conda-bld/
cd osx-64/
conda install cherrypy-3.2.4-py27_0.tar.bz2 
```

### JavaScript

All of the javascript dependencies are in the repository in the
libs directory, but here are a list of the currently used libraries:

- [d3.js][]
- [jQuery](http://jquery.com)
- [jQueryUI](http://jqueryui.com) subset including only the slider for now
- [jQuery tiny pubsub](https://gist.github.com/cowboy/661855) for events publish/subscribe
- [parseUri](http://blog.stevenlevithan.com/archives/parseuri) for parsing the page URI


## Apache Web Server Configuration

*Some of the following will be specific to Mac OS X (10.8) configuration, since
that's what I'm using for my production environment.*

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
in the background. In my `/etc/apache2/users/username.conf` file 
(substitute your own username on your machine), I add
ProxyPass lines like in this example:

```
<Directory "/Users/username/Sites/">
    Options Indexes MultiViews FollowSymLinks
    AllowOverride None
    Order allow,deny
    Allow from all
</Directory>

ProxyPass /remote9000/  http://servername.sub.school.edu:9000/
ProxyPass /remote9002/  http://servername.sub.school.edu:9002/
```

which lets me just make a call to something like

`http://servername.sub.school.edu/remote9000/allellipses?basis=1`

instead of 

`http://servername.sub.school.edu:9000/allellipses?basis=1`

in my ajax call, the former of which is considered "same origin".


## Apache Startup

OS X used to have a check-box in the System Preferences, Sharing pane for
"Web", which started up the built-in Apache server. Apache is still built in,
but you might need to create a ~/Sites directory, and you need to use the
command line to start up (or restart) Apache.

`sudo apachectl start`

Instead of `start`, you can also use `restart` or `stop`.


## Symlink to project path

Notice that my example Apache configuration file also had an additional "Option"
entry from what the default typically is: FollowSymLinks. This is so we can put
a symbolic link in our local Apache site path (listed in the username.conf Directory
line). From my home directory (in the terminal) I type:

```
ln -s /Users/username/Programming/SamVis/IPCA /Users/username/Sites/SamVisIPCA
ln -s /Users/username/Programming/SamVis/path /Users/username/Sites/SamVisPath
```

This way I can access the IPCA directory from

`servername.sub.school.edu/~username/SamVis/IPCA`


## Local Web Server Name Configuration

There is a file called `server_conf_example.json` in the root of the
repository. This is an example of the file which sets the local server
name for all of the Javascript and Python scripts in both the IPCA and
path directories..

Make a copy of `server_conf_example.json` and call it `server_conf.json`.
The latter is included in this project's `.gitignore` file, so changes you make
to your server configuration won't get recognized as changes to the project
source, plus your server-specific configuration values won't get overwritten
when you pull changes to the repository.

This config also lets you set the port number used for the IPCA visualizations
in `IPCA` and the simulated path visualizations in the `path` directory. 
The `ipca_web_dir` and `path_web_dir` variables should reflect the symlink name
you set up in your Sites directory. See the "Symlink to project path" section
below. In that example the variables would be set as `SamVis/path` and `SamVis/IPCA`
respectively. Also see below for the reverse proxy setup instructions. 

Additionally, you use the `server_conf.json` file to set the path to the data
for each type of visualization. These paths are relative to the html and JS files
for each project. It is fine to have this path outside of the directories that
can be served up by your web server. 

*NOTE:* If you put the port value at 9000, the scripts will expect the reverse 
proxy to be at `http://servername.sub.school.edu/remote9000/` 
*(i.e. that string, "remote", is hard-coded into
the scripts, so use that actual string in your reverse proxy name)*


## Data directory and files 

Right now the projects are set up to load multiple datasets into memory
so they can be served up when requested. The way this is handled is that
you set the data directory as stated above. In that directory you create
sub-directories with unique names for the datasets that will be
contained in each. For the "path" project there is sample data in the
repository. For the "IPCA" project there is a download link below with
some sample data. 

In the case of the IPCA tree data, there a JSON metadata file format which
is documented in `IPCA/metadata_spec.md`. *This file must be named data\_info.json.*
This metadata describes the file names, type of data, names and types of labels, etc,
since the binary file format we're currently using doesn't store any of this information.

*Resource Index:* When you start up the either the path or IPCA tree
server it will look for directories in the `ipca_data_dir` and put links
to visualizations at the address

`http://servername.sub.school.edu/remote9002/resource_index`

where that server name and 9002 port number you've set in the
`server_conf.json` file. What you'll see is a list of names the same as
your data directory names, but they'll all be links to visualization
pages.


## IPCA Example Data

The IPCA visualizations in the IPCA directory use data from the [MNIST database of
handwritten digits](http://yann.lecun.com/exdb/mnist/). Specifically, the set of
images of handwritten 1s and 2s from the training set was used. You can download
the preprocessed data files (IPCA output plus labels) from [this zip file](http://people.duke.edu/~emonson/mnist12_v5_d8c2.zip)

See above in the *Local Web Server Name Configuration* section for the expectations 
of the IPCA project regarding data directory structure.
