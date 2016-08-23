# Using automated tasks with Invoke

This project uses `invoke` to run some automated tasks.

First, install it with:

```bash

$ sudo pip install invoke

```

You can now see the list of tasks by running at the root directory:

```bash

$ invoke --list

```

For instance, if I need to bump the current version number, I can run `invoke release.bump --feature` or `invoke release.bump --patch` and the according files will be modified.


The tasks are defined in `tasks.py`.
