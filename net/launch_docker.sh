sudo docker run -it -p 8000:8000 -p 6794:6794 -v /mnt/data/astrometry.net/net/data:/home/nova/astrometry/net/data -v /mnt/data/astrometry_indexes:/data/INDEXES astrometrynet/webservice /bin/bash
