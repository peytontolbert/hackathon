import asyncio
import json
import logging
import signal
from aiohttp import web
from config_agent import ConfigAgent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConfigServer:
    def __init__(self, host: str = "localhost", port: int = 1001):
        self.host = host
        self.port = port
        self.agent = ConfigAgent()
        self.app = web.Application()
        self.setup_routes()
        self._shutdown_event = None
        
    def setup_routes(self):
        """Set up server routes"""
        self.app.router.add_get("/.well-known/agent.json", self.get_agent_card)
        self.app.router.add_post("/", self.handle_request)
        
    async def get_agent_card(self, request: web.Request) -> web.Response:
        """Serve the agent capability card"""
        return web.json_response(self.agent.get_agent_card())
        
    async def handle_request(self, request: web.Request) -> web.Response:
        """Handle incoming A2A requests"""
        try:
            data = await request.json()
            response = await self.agent.handle_request(data)
            return web.json_response(response)
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return web.json_response({"error": str(e)}, status=500)
            
    async def start(self):
        """Start the server"""
        self._shutdown_event = asyncio.Event()
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        logger.info(f"Config server running at http://{self.host}:{self.port}")
        logger.info("Press Ctrl+C to stop the server")
        
        # Keep the server running until shutdown is requested
        await self._shutdown_event.wait()
        
        # Cleanup
        await runner.cleanup()
        logger.info("Server shutdown complete")
        
    def handle_shutdown(self, sig=None):
        """Handle shutdown signals"""
        if sig:
            logger.info(f"Received signal {sig.name}...")
        logger.info("Initiating shutdown...")
        if self._shutdown_event:
            self._shutdown_event.set()
        
    @classmethod
    async def create_and_start(cls, host: str = "localhost", port: int = 1001):
        """Create and start a new server instance"""
        server = cls(host, port)
        
        # Set up signal handlers
        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, lambda s, _: server.handle_shutdown(s))
            
        await server.start()
        return server

async def main():
    """Main entry point"""
    try:
        server = await ConfigServer.create_and_start()
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        return 1
    return 0

if __name__ == "__main__":
    # Run the server
    exit_code = asyncio.run(main()) 