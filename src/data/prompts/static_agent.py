STASTIC_OBJECTS = """
STEPS:
1. Use get_objects tool to get all objects data
2. Extract key descriptors from the question (color, shape, material)
3. Find the object that matches these descriptors exactly
4. Return that object's ID

IMPORTANT: Look for specific descriptors in the question:
- "purple object" → Find object with color="purple"
- "gray sphere" → Find object with color="gray" AND shape="sphere"  
- "metal cube" → Find object with material="metal" AND shape="cube"

DEBUG: Print your reasoning:
- "Looking for: [descriptors from question]"
- "Found match: Object X has [matching properties]"

Example:
Question: "What is the shape of the object to collide with the purple object?"
1. Descriptors from question: color="purple"
2. Search objects for color="purple" 
3. Found: Object 3 has color="purple"
4. Return: "Object ID: 3 (purple sphere)"

Response format: "Object ID: X (description)"
"""