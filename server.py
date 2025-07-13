from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
import logging
from main import MCPAssistant

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="MCP Tool Assistant")

# Initialize templates
templates = Jinja2Templates(directory="templates")

# Initialize MCP Assistant
assistant = MCPAssistant()

class ChatRequest(BaseModel):
    message: str

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the main HTML page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat(chat_request: ChatRequest):
    """Handle chat requests"""
    try:
        result = assistant.handle_request(chat_request.message)
        return result
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        return {
            "success": False,
            "message": f"An error occurred: {str(e)}"
        }

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True) 