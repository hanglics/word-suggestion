from waitress import serve
from models import waitressConfig
import main

# Construct the production server using waitress
# can be configured through changing in config.json
serve (
    main.app, 
    host=waitressConfig["host"], 
    port=waitressConfig["port"],
    ipv4=waitressConfig["ipv4"], 
    ipv6=waitressConfig["ipv6"], 
    threads=waitressConfig["threads"],
    url_scheme=waitressConfig["url_scheme"]
)