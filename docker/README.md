# Astrometry.net Web Interface Dockerfiles

Many people visit this repository with the intention of deploying a local version of the astrometry.net web interface.
Although it's entirely feasible to manually follow the instructions in the `net` folder, we also provide docker files to enable a quick and efficient deployment.
However, it's important to note that these docker files are primarily designed for quick trials and development.
If you're planning to use them for production, they'll require further refinement, particularly in terms of security settings.

This folder contains two docker files.
The first is for the solver, which provides the command line tools for astrometry.net.
The second is for the web service, which includes the Django-based web server and API server. 
Here's how you can set up a docker container using these docker files.

## solver

In most cases, the solver requires an index to function.
A common approach is to download the pre-cooked index files.
One can use the command line provided below to download.
Please note that all the command lines referenced in this document assume that they are being executed under the repository root, such as `~/astrometry.net`, and not the current folder.
```
mkdir -p ../astrometry_indexes
pushd ../astrometry_indexes/ && \
for i in 4100 4200; do \
    wget -r -l1 --no-parent -nc -nd -A ".fits" http://data.astrometry.net/$i/;\
done
popd
```
The index could be fairly large, and it's likely you only need part of them.
Check out [this link](http://astrometry.net/doc/readme.html#getting-index-files) to understand whether it's possible to only download and use part of all the files.
Otherwise, downloading all the files will also work.

If web service is also desired, it's a good time to config the security settings (`appsecrets`).
`appsecrets-example` is a good start point.
If it's only for a quick peek, `cp -ar net/appsecrets-example net/appsecrets` is good enough.

Then one can build the docker image using the command line:
```
sudo docker build -t astrometrynet/solver:latest -f docker/solver/Dockerfile .
```
Again note the command should be executed in the repo root folder, not the current folder.

Then use this command to log into the container to use the command lines:
```
sudo docker run -v ~/astrometry_indexes:/usr/local/data -it astrometrynet/solver /bin/bash
```
Here `~/astrometry_indexes` is the host folder holding the indexes downloaded from the first step.
In the `solver` container, the command line tools are available for use.
For example, `solve-field`.

## webservice

This container depends on the `solver` container.
First follow the steps in the previous section to build the `solver` container.
Note if you made any changes to the repo, e.g. changing the secrets in the `appsecrets`, `solver` container needs to be rebuilt for the changes to take effect.

Then build the `webservice` container:
```
sudo docker build -t astrometrynet/webservice:latest -f docker/webservice/Dockerfile .
```

For the container to function properly, we still need to map the indexes folder to it, with some port mapping:
```
sudo docker run -p 8000:8000 -v ~/astrometry_indexes:/data/INDEXES astrometrynet/webservice
```

The the Astrometry.net website could be accessed on the host machine at http://localhost:8000.

## Gap to Production

Note the docker file still has quite some gap to production, especially in:

1. All the data is stored in a SQLite "database," which is essentially a file and subject to loss after the container terminates. The solution is to create a "real" database somewhere, and let the django connect to it through the network.
2. Similarly, all the user uploaded data, results, and logs will be lost after the container terminates. The solution is to map a volume to `net/data`.
3. A good practice to handle many requests at the same time is to put the endpoint behind some reverse proxy with load balancing. Apache and Nginx are good candidates.
