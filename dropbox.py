import collections
import os
import sys
import requests
import json

def get_initial(bearer):
    print("Grabbing initial list")
    url = "https://api.dropboxapi.com/2/files/list_folder"
    headers = {
        "Authorization": f"Bearer {bearer}",
        "Content-Type": "application/json",
    }
    data = {
        "path": "",
        "recursive": True,
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

def get_continue(cursor, bearer):
    print("Getting remaining list")
    url = "https://api.dropboxapi.com/2/files/list_folder/continue"
    headers = {
        "Authorization": f"Bearer {bearer}",
        "Content-Type": "application/json",
    }
    data = {
        "cursor": cursor,
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()


def get_files(bearer):
    cursor = None  # Signals continuation

    entries = []

    while True:
        if cursor is None:
            result = get_initial(bearer)
        else:
            result = get_continue(cursor, bearer)
        
        print("Adding {} new entries".format(len(result['entries'])))
        entries.extend(result['entries'])
        if result['has_more']:
            cursor = result['cursor']
        else:
            # No more files to load, we are good
            print("Found {} files".format(len(entries)))
            return entries


def split_path(path):
    parts = []
    
    while path:
        head, tail = os.path.split(path)
        if not tail:
            break
        parts.append(tail)
        path = head
    
    return parts[::-1]



class Tree(object):
    def __init__(self):
        self.size = 0
        self.children = dict()

    def add(self, file):
        path_parts = split_path(file["path_lower"])
        self.add_recursive(path_parts, file)

    def add_recursive(self, path_parts, file):
        self.size += file.get('size', 0)

        if not path_parts:
            # No more children to walk through
            return
        
        # Split the path and start building up the tree
        head, rest = path_parts[0], path_parts[1:]
        if head not in self.children:
            self.children[head] = Tree()
        child = self.children[head]
        child.add_recursive(rest, file)


    def to_dict(self):
        ordered_children = sorted(self.children.items(), key=lambda item: item[1].size, reverse=True)
        sorted_children = collections.OrderedDict()
        for name, tree in ordered_children:
            sorted_children[name] = tree.to_dict()
        return {"size": self.size, "size_2": int(self.size / 1024 / 1024), "children": sorted_children}


    def __str__(self):
        def to_dict(tree):
            return tree.to_dict()
        return json.dumps(self, default=to_dict)
        return 'Tree(size={}, children={})'.format(self.size, self.children)
    
    def __repr__(self):
        return str(self)


def organize(files):
    tree = Tree()
    for file in files:
        tree.add(file)
    return tree


def flamegraph(files):
    for file in files:
        print(';'.join(split_path(file['path_lower'])) + ' ' + str(file.get('size', 0)))


def main():
    bearer = sys.argv[1]
    files = get_files(bearer)
    tree = organize(files)
    print(tree)
    flamegraph(files)
    import pdb
    pdb.set_trace()


if __name__ == '__main__':
    main()
