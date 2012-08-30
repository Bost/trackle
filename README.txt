start local develompment server
google_appengine/dev_appserver.py helloworld/

start local develompment server with emailing:
google_appengine/dev_appserver.py --enable_sendmail helloworld/

deploy to google:
google_appengine/appcfg.py update helloworld/
