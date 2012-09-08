start local develompment server
dev_appserver.py --debug --clear_datastore --blobstore_path=~/gae/blobstore_dir --datastore_path=~/gae/datastore_file helloworld/
dev_appserver.py --clear_datastore --blobstore_path=~/gae/blobstore_dir --datastore_path=~/gae/datastore_file helloworld/

start local develompment server with emailing:
dev_appserver.py --enable_sendmail helloworld/

deploy to google:
appcfg.py update helloworld/
