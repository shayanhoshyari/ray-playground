## Summary

I want to detect that a user dropped their http request.

I want to use this to cancel a long running ML job.

My idea was to use `request.is_disconnected()` from starlette/fastapi, but I am having issues. This function works when I have a vanilla fastapi app served by uvicorn. But when I embed the same app in a ray deployment, the function always returns false, i.e. thinks the user is not disconnected.


__My question is, how can I ask `ray` if user dropped the request?__


Here is a small repro:

### setup

From the root of repo

- Run `bash setup.py`
- Run `. .venv/bin/activate`


### uvicorn server.

* Run `uvicorn fastapi-disconnect.app:app --log-config=fastapi-disconnect/log.yaml`
* From another terminal, run python `fastapi-disconnect/request.py`
  * If you don't press ctrl+c, you will see this printed:
    ```
    INFO - Request still good, sleeping
    INFO - 127.0.0.1:35230 - "PUT / HTTP/1.1" 200
    ```
  * If you press Ctrl+c you should see
    ```
    INFO - Request dropped
    ```

### fastapi within ray
* Run `python fastapi-disconnect/rayapp.py`
* From another terminal, run `python fastapi-disconnect/request.py`
  * If you don't press ctrl+c, you will same behaviour as uvicorn.
  * If you press Ctrl+c you keep seeing `Request {'message': 'Hello boys'} still good, sleeping`, not consistent with uvicorn.

