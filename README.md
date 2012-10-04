# Launch local develompment server:
```bash
dev_appserver.py --clear_datastore .
dev_appserver.py --debug .
dev_appserver.py --debug --clear_datastore --blobstore_path=~/gae/blobstore_dir --datastore_path=~/gae/datastore_file .
dev_appserver.py --clear_datastore --blobstore_path=~/gae/blobstore_dir --datastore_path=~/gae/datastore_file .
```

# Launch local develompment server with emailing:
```bash
dev_appserver.py --enable_sendmail .
```

# Deploy to google:
```bash
appcfg.py update .
```
