from typing import List, Optional, Any
from pydantic import BaseModel
from google import genai
from io import BytesIO
from PIL import Image
import json
import os
from dotenv import load_dotenv
from src.data.prompts.image_relation_prompt import IMAGE_RELATION_PROMPT
load_dotenv()
# --- Config LLM Client ---
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# --- Pydantic Schemas ---
class ImageRelationInput(BaseModel):
    mask_frame: Any           
    original_img: Optional[Any] = None 
    prev_objects: Optional[List[str]] = None


class RelationOutput(BaseModel):
    relations: List[str]


class ImageRelationAgent:
    def __init__(self, model: str = "gemini-2.0-flash"):
        self.model = model
        self.prev_objects: Optional[List[str]] = None

    def _upload_image(self, img_array) -> Any:
        img_pil = Image.fromarray(img_array)
        buffer = BytesIO()
        img_pil.save(buffer, format="JPEG")
        buffer.seek(0)
        return client.files.upload(file=buffer, config={"mime_type": "image/jpeg"})

    def _extract_existing_ids(self, prev_objects: Optional[List[str]]) -> set:
        ids = set()
        if prev_objects:
            for rel in prev_objects:
                parts = [p.strip() for p in rel.split('-')]
                for obj in [parts[0], parts[-1]]:
                    obj_id = obj.split('(')[0].strip()
                    ids.add(obj_id)
        return ids

    def run(self, data: ImageRelationInput) -> RelationOutput:
        mask_file = self._upload_image(data.mask_frame)
        existing_ids = self._extract_existing_ids(data.prev_objects)

        prompt = IMAGE_RELATION_PROMPT.format(
            existing_ids=json.dumps(list(existing_ids), ensure_ascii=False)
        )

        if data.prev_objects:
            prompt += f"\nThông tin vật thể từ frame trước: {json.dumps(data.prev_objects)}"

        contents = [mask_file, prompt]
        if data.original_img is not None:
            original_file = self._upload_image(data.original_img)
            contents.append(original_file)


        response = client.models.generate_content(
            model=self.model,
            contents=contents
        )


        relations: List[str] = []
        for part in response.candidates[0].content.parts:
            if part.text:
                try:
                    parsed = json.loads(part.text)
                    if isinstance(parsed, list):
                        relations.extend(parsed)
                except json.JSONDecodeError:
                    relations.append(part.text.strip())

        self.prev_objects = relations

        return RelationOutput(relations=relations)