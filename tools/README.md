# Build scripts

One script per device. Each one drives the Fusion 360 API to build that part
from named user parameters, and can be re-run to regenerate the model from
scratch.

Scripts are executed against a running Fusion 360 instance through Fusion's
local MCP server (Preferences, General, API, Fusion MCP Server). They are plain
Fusion API scripts and define the standard entry point:

    def run(_context: str):
        ...

| Script | Device |
|--------|--------|
| not yet written | 1. Built-up handle sleeve |
| not yet written | 2. Key turner |
| not yet written | 3. Bottle and jar opener |
| not yet written | 4. Zipper and button pull |
| not yet written | 5. Pen grip |
