# Launch local develompment server:
```bash
dev_appserver.py --clear_datastore helloworld/
dev_appserver.py --debug helloworld/
dev_appserver.py --debug --clear_datastore --blobstore_path=~/gae/blobstore_dir --datastore_path=~/gae/datastore_file helloworld/
dev_appserver.py --clear_datastore --blobstore_path=~/gae/blobstore_dir --datastore_path=~/gae/datastore_file helloworld/
```

# Launch local develompment server with emailing:
```bash
dev_appserver.py --enable_sendmail helloworld/
```

# Deploy to google:
```bash
appcfg.py update helloworld/
```
