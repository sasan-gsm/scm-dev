# Gunicorn configuration file
import multiprocessing

# Bind to 0.0.0.0:8000
bind = "0.0.0.0:8000"

# Number of worker processes
workers = multiprocessing.cpu_count() * 2 + 1

# Worker class to use
worker_class = "sync"

# Timeout for worker processes
timeout = 120

# The maximum number of requests a worker will process before restarting
max_requests = 1000
max_requests_jitter = 50

# Logging
logfile = "/var/log/gunicorn/access.log"
loglevel = "info"
# accesslog = "/var/log/gunicorn/access.log"
# errorlog = "/var/log/gunicorn/error.log"
accesslog = "-"  # stdout
errorlog = "-"  # stderr

# Process name
proc_name = "scm_gunicorn"

# Django WSGI application path
wsgi_app = "scm.wsgi:application"

# Preload application code before worker processes are forked
preload_app = True

# Restart workers when code changes (development only)
reload = False

# Daemonize the Gunicorn process (run in background)
daemon = False
