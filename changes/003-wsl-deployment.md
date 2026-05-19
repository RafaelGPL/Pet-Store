# 003 — WSL Deployment

Identified that Python was not available on the Windows PATH so local smoke testing was not possible.
Located the Ubuntu WSL distribution on the machine and confirmed Python 3.8.10 and pip were available inside it.
Copied the project from the Windows filesystem into the WSL home directory using the /mnt/c mount point.
Upgraded pip inside WSL to resolve dependency resolution issues with the older bundled version.
Installed fastapi and uvicorn inside WSL using pip, which placed the uvicorn binary at ~/.local/bin/uvicorn outside the default PATH.
Started uvicorn using its full path with host 0.0.0.0 and port 8000.
Discovered that background processes started in one wsl bash invocation are killed when that session exits due to WSL1 process lifecycle behaviour.
Resolved the process lifetime issue by starting the server and running all tests within a single bash session.
Discovered that FastAPI was issuing 307 redirects on routes with trailing slashes; fixed this by adding redirect_slashes=False to the router.
Discovered that the 422 errors on initial POST calls were caused by shell quoting being mangled by the outer zsh process; replaced inline curl with a self-contained Python test script.
Fixed the test script to handle 204 No Content responses, which return an empty body that cannot be parsed as JSON.
Ran the full smoke test suite covering: create two pets, list all, fetch by id, patch fields, delete, confirm deletion via 404, and validate empty name returns 422.
All nine assertions passed against the live server running on WSL Ubuntu.
