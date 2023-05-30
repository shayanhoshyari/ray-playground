# http_proxy_callback


Some code to help with testing https://github.com/ray-project/ray/pull/35619

How to launch vscode

- Cd into this folder.
- Run `. setup.sh`
- Open this folder in vscode.
- Launch the `RAY: HTTP CALLBACK` target.


The aim is to be able to see the code within ray's http_proxy in the debugger. Which is not happening now. Current situation is described in comments in `main.py`.


Contents:
  - main.py: file for local serving and debugging. This is the file we run in vscode for debugging.
  - runtime: The runtime env. FOr development we just install it as editable in python env.

