# VAMP
## Download data
Download data [from this link](https://univaq-my.sharepoint.com/:u:/g/personal/luca_traini_univaq_it/EbIRQ-UgEpZMm_LniOU7ChgBBs6lNwpu2LGRGKufXyFwdw?e=NzyfUu)

Then run 
``tar -xvzf dump.tar.gz``

## Launch
Lauch the following commands

``docker-compose up -d mongodb``

``docker cp dump <container_name_or_id>:/tmp/dump``

``docker exec <container_name_or_id> bash -c "mongorestore /tmp/dump"``

## Start server

``FLASK_DEBUG=1 FLASK_APP=app.py flask run -p 8080 --host=0.0.0.0``

