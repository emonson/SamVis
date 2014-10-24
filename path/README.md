## path

Moving further with the simplified scatterplot idea developed for IPCA, but now for following paths
in an abstract, potentially nonlinear and high-dimensional space which is represented 
locally by low-dimensional linear spaces. This is work with [Miles Crosskey][miles], 
and was originally motivated by simplified molecular dynamics simulations, but is applicable to
many types of dynamical systems. For more information about the technique, see [his
ATLAS paper](https://www.researchgate.net/publication/261325344_ATLAS_A_geometric_approach_to_learning_high-dimensional_stochastic_systems_near_manifolds).

[miles]: https://www.researchgate.net/profile/Miles_Crosskey "Miles Crosskey"


## Dependencies

### Python

The modules required beyond that of the standard library are:

- [CherryPy](http://cherrypy.org)
- [NumPy](http://numpy.org)
- [SciPy](http://www.scipy.org)

**Anaconda:** For my Python distribution I'm using [Anaconda](https://store.continuum.io/cshop/anaconda/)
from [Continuum Analytics](http://www.continuum.io/). It comes 
with lots of pre-installed modules, including NumPy and SciPy, which are sometimes difficult
to install. It's free and available for all platforms,
and you can even get free academic licences for some "Add-Ons" to accelerate execution.

Right now Anaconda doesn't come with CherryPy, so I just install it with `pip`. You can use
available recipies for the `conda` package manager that comes with Anaconda, but I don't 
usually bother.

### JavaScript

All of the javascript dependencies are in the repository in the
libs directory off of the main repository, but here are a list of the currently used libraries:

- [d3.js](http://d3js.org/)
- [jQuery](http://jquery.com)
- [jQueryUI](http://jqueryui.com) subset including only the slider for now
- [jQuery tiny pubsub](https://gist.github.com/cowboy/661855) for events publish/subscribe
- [jQuery UI Touch Punch](http://touchpunch.furf.com/) so slider works with mobile touch interaction
- [parseUri](http://blog.stevenlevithan.com/archives/parseuri) for parsing the page URI


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

Right now the project is set up to load multiple datasets into memory
so they can be served up when requested. You set the data directory (as stated above)
in the `server_conf.json` file. In that directory you create
sub-directories with unique names for the datasets that will be
contained in each. There are a few sample datasets in the repository.

*Resource Index:* When you start up the path
server it will look for directories in the `path_data_dir` and put links
to visualizations at the address

`http://servername.sub.school.edu/remote9002/resource_index`

where that server name and 9002 port number you've set in the
`server_conf.json` file. What you'll see is a list of names the same as
your data directory names, but they'll all be links to visualization
pages.


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
ln -s /Users/username/Programming/SamVis/path /Users/username/Sites/SamVis/Path
```

This way I can access the path directory from

`servername.sub.school.edu/~username/SamVis/path`

