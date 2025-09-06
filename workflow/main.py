import os
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from llm.base import AgentClient
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from data.cache.memory_handler import MessageMemoryHandler
import chainlit as cl
from pathlib import Path

from data.prompts.static_agent import STASTIC_OBJECTS
from data.prompts.main_agent_prompt import SYSTEM_PROMPT
from data.prompts.searching_agent_prompt import SEARCHING_AGENT_PROMPT
from utils.basetools.graph_builder import CLEVRERGraphBuilder
from utils.basetools.reading_annotation import CLEVRERObjectHandler
from utils.basetools.searching_tool import CLEVRERSearchTool

provider = OpenAIProvider(api_key=os.getenv("OPENAI_API_KEY"))
model = OpenAIChatModel("gpt-4o-mini", provider=provider)

DATA_DIR = Path("/Users/ptdung/Coding/Github/soICT/dataset")
ANNOTATION_DIR = DATA_DIR / "annotation_train"
VIDEO_DIR = DATA_DIR / "video_train"
# dataset/annotation_train/annotation_00000-01000/annotation_00000.json
annotation_file = ANNOTATION_DIR / "annotation_00000-01000" / "annotation_00000.json"

graph = CLEVRERGraphBuilder(str(annotation_file))

annotation_inf = CLEVRERObjectHandler(str(annotation_file))
search_tool = CLEVRERSearchTool(str(annotation_file))

static_agent = AgentClient(
    model=model,
    system_prompt=STASTIC_OBJECTS,
    tools=[annotation_inf.get_objects]
).create_agent()

# Initialize searching agent with search tools
searching_agent = AgentClient(
    model=model,
    system_prompt=SEARCHING_AGENT_PROMPT,
    tools=[search_tool.search_object_trajectory]
).create_agent()

memory_handler = MessageMemoryHandler()


@cl.on_message
async def main(message: cl.Message):
    # First use static agent to extract object information
    static_response = await static_agent.run(message.content)
    print(f"Static Agent Response: {static_response.output}")
    # Then use searching agent with both the original question and static agent results
    search_input = f"Original question: {message.content}\n\nObject information: {static_response.output}\n\nPlease search for trajectory and collision data to answer the question."
    search_response = await searching_agent.run(search_input)
    
    await cl.Message(content=str(search_response.output)).send()
