# 006 — README and Requirements

Created README.md with a large ASCII block-art banner spelling out "PET STORE" using Unicode box-drawing characters.
Added a tagline clarifying the project is an archive for pets, not a shop.
Added status badges for Python version, FastAPI, SQLite, architecture style, code formatter, and Git workflow.
Wrote a "What is this?" section explaining the purpose of the API in plain language.
Listed the key features of the project in a bullet list.
Added a tech stack table covering framework, server, database, architecture, code style, and language version.
Included an annotated project structure tree showing every folder and its purpose.
Documented all nine API endpoints across two sections: Pets and Pet Events.
Provided example request and response JSON bodies for every endpoint that accepts or returns data.
Added an error responses table listing the 404 and 422 cases and when each occurs.
Wrote platform-specific Quick Start instructions for Windows (WSL2 and native PowerShell), macOS, and Linux.
Included a note for each platform about common PATH and Python version issues and how to work around them.
Added a dependencies table separating runtime packages from development packages with version requirements and purpose.
Added a Git-Flow section showing the branch hierarchy and a concrete example of starting and merging a feature branch.
Added an architecture overview section summarising the four DDD layers and their responsibilities.
Updated requirements.txt to include black as a development dependency alongside fastapi and uvicorn, with version constraints and inline comments separating runtime from dev dependencies.
Synced README.md, requirements.txt, and the new changelog file to the WSL project directory.
Staged and committed all changes on the develop branch with the message "Add README, update requirements".
