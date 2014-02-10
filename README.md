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

There is a file called server\_conf\_example.json in the root of the
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

*Data directory and file arrangement:* Right now the projects are set up to
load multiple datasets into memory so they can be served up when requested. The
way this is handled is that you set the data directory as stated above. In that
directory you create sub-directories with unique names for the datasets that will
be contained in each. For the "path" project there is sample data in the repository.
For the "IPCA" project there is a download link below with some sample data. Three
files are expected by the program: `tree.ipca`, which is the output of the GMRA
CreateIPCATree code in the gmra_src directory; `labels.data`, which is a binary
array of label integers, and `labels.data.hdr` which is the text header file
describing the labels data.

*NOTE:* The scripts will expect the reverse proxy to be at server_name/remote9000/ 
if you put the port value at 9000. (i.e. that string, "remote", is hard-coded into
the scripts, so use that actual string in your reverse proxy name)


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

in my ajax call, which is considered "same origin".


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


## IPCA Example Data

The IPCA visualizations in the IPCA directory use data from the [MNIST database of
handwritten digits](http://yann.lecun.com/exdb/mnist/). Specifically, the set of
images of handwritten 1s and 2s from the training set was used. You can download
the preprocessed data files (IPCA output plus labels) from [this zip file](http://people.duke.edu/~emonson/mnist12_v5_d8c1.zip)

See above in the *Local Web Server Name Configuration* section for the expectations 
of the IPCA project regarding data directory structure.
