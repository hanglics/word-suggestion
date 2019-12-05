from waitress import serve
from models import waitressConfig
import main

# Production server
serve (
    main.app, 
    host=waitressConfig["host"], 
    port=waitressConfig["port"],
    ipv4=waitressConfig["ipv4"], 
    ipv6=waitressConfig["ipv6"], 
    threads=waitressConfig["threads"],
    url_scheme=waitressConfig["url_scheme"]
)