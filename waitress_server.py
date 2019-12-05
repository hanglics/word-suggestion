from waitress import serve
from models import config
import main

# Production server
serve(
    main.app, 
    host=config["waitress_host"], 
    port="6688",
    ipv4=True, 
    ipv6=True, 
    threads=6,
    url_scheme="http"
    )