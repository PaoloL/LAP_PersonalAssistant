from server import mcp
import tools.fastmcp_youtrack

import logging
logging.basicConfig(level=logging.DEBUG)

# Entry point to run the server
if __name__ == "__main__":
    logging.info("Starting MCP Server")
    mcp.run()
