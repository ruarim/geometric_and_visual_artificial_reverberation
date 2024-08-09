import base64
from utils.api_key import OPENAI_API_KEY
from openai import OpenAI

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

def read_csv_text(csv_file_path: str):
    with open(csv_file_path, 'r') as file:
        return file.read()

def image_to_material(material_csv: str, image_path: str):
    client = OpenAI(api_key=OPENAI_API_KEY)

    csv_file_path = f'{material_csv}'
        
    materials_database = read_csv_text(csv_file_path)
    base64_image = encode_image(f'{image_path}')
    
    system_prompt = '''
    Acoustic Material Classifier. 
    Given a photo of a surface, identify the most likely material from the attached list of material names. 
    All predictions MUST exist in the provided materials.json file. 
    You must return a single-word response containing ONLY the material name, which is a key in the json file.'''
    user_prompt   = 'Identify the main material'
    
    response = client.chat.completions.create(
    model="gpt-4o",
    temperature=0.01,
    messages=[
        {"role": "system", "content": f"{system_prompt}"},
        {"role": "system", "content": f"{materials_database}"},
        {'role': "user",   "content": f"{user_prompt}"},
        {
        "role": "user",
        "content": [
            {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}",
                "detail": "high",
            },
            },
        ],
        }
    ],
    max_tokens=300,
    )
    
    material = response.choices[0].message.content
    print(f'MATERIAL FOUND: {material}')
    return material
    