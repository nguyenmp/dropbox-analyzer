# dropbox-analyzer
Figure out where the space in your dropbox is going

## Usage

Set up a bearer token that can read metadata of your files: https://developers.dropbox.com/oauth-guide

```
python3 dropbox.py 'BEARER_TOKEN'
```

The above will drop a json blob that you can navigate like the directory tree with cumulative file sizes annotated for each node in the tree.  The tree is sorted by largest first so focus on the top stuff.
