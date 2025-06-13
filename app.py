from pydantic import BaseModel, Field
from typing import List
import asyncio
import json

import os
from graphiti_core import Graphiti
from graphiti_core.llm_client.gemini_client import GeminiClient, LLMConfig
from graphiti_core.embedder.gemini import GeminiEmbedder, GeminiEmbedderConfig
from graphiti_core.nodes import EpisodeType
from datetime import datetime, timezone
import google.generativeai as genai


class ExtractableEntity(BaseModel):
    name: str = Field(description='Name of the entity (lowercase)')
    entity_type: str = Field(description='Type of the entity (lowercase and snake case)')
    singular: bool = Field(description='Whether the entity is singular (true) or plural (false)')
    description: str = Field(description='Description of how entity is described or introduced in the text')


class ExtractableRelationship(BaseModel):
    entity_1: str = Field(description='Name of entity 1 (lowercase)')
    entity_2: str = Field(description='Name of entity 2 (lowercase)')
    relationship_type: str = Field(description='Type of relationship between entity 1 and 2 (lowercase and snake case)')
    description: str = Field(description='Description of how relationship is described or introduced in the text')


class EntitiesRelationships(BaseModel):
    entities: List[ExtractableEntity] = Field(description='List of entities', default=[])
    relationships: List[ExtractableRelationship] = Field(description='List of relationships between entities',
                                                         default=[])


def get_prompt(chunk):
    # prompt

    format_instructions = """
    Respond with only a JSON object that follows this structure:
    {{
      "content": {{
        "entities": [
          {{
            "name": "marie curie",
            "entity_type": "scientist",
            "singular": true,
            "description": "Marie Curie is introduced as a scientist who discovered radium."
          }}
        ],
        "relationships": [
          {{
            "entity_1": "marie curie",
            "entity_2": "radium",
            "relationship_type": "discovered",
            "description": "Marie Curie is said to have discovered radium."
          }}
        ]
      }},
      "type": "json",
      "description": "structured knowledge extraction from text"
    }}
    """

    chunk = "Marie Curie discovered radium and worked at Sorbonne University in Paris."

    prompt = f"""
    Your task is to extract a list of entities and their relationships from the given text.

    Instructions for extracting **entities**:
    1. Only include important and relevant proper nouns (no pronouns, prepositions, or adjectives).
    2. Avoid generic entities.
    3. Use lowercase for entity names and snake_case for types.
    4. Use 'singular': true if the entity represents a unique item or person.

    Instructions for extracting **relationships**:
    1. Include only relationships between entities you have extracted.
    2. Use lowercase names and snake_case for the relationship type.
    3. Relationships are directed from entity_1 to entity_2.
    4. Include a reverse relationship if it's bidirectional.

    Instructions for **descriptions**:
    1. Describe how each entity and relationship is introduced in the text.
    2. Include an excerpt from the text to support the description.

    {format_instructions}

    The text is: "{chunk}"
    """
    prompt2=prompt.format(format_instructions=format_instructions,chunk=chunk)
    return prompt2

genai.configure(api_key="AIzaSyC6yHwqS0J-5SZP7SNMoBxxfrGjK8a-5rk")
MODEL_NAME = "gemini-2.0-flash"


async def get_structured_data(chunk):
    prompt=get_prompt(chunk)
    model = genai.GenerativeModel(MODEL_NAME)
    chat = model.start_chat()
    response = await chat.send_message_async(prompt)
    result = response.text.strip().removeprefix("```json").removesuffix("```").strip()

    response_dict = json.loads(result)
    return response_dict


def get_graphiti_obj():
    api_key =os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable must be set")

    # Initialize Graphiti with Gemini clients
    graphiti = Graphiti(
        "bolt://localhost:7687",
        "neo4j",
        "neodj password",
        llm_client=GeminiClient(
            config=LLMConfig(
                api_key=api_key,
                model="gemini-2.0-flash"
            )
        ),
        embedder=GeminiEmbedder(
            config=GeminiEmbedderConfig(
                api_key=api_key,
                embedding_model="embedding-001"
            )
        )
    )
    return graphiti

async def add_episode(graphiti,episode):
    try:
        # Initialize the graph database with graphiti's indices. This only needs to be done once.
        await graphiti.build_indices_and_constraints()

        await graphiti.add_episode(
            name=f'Freakonomics Radio',
            episode_body=json.dumps(episode['content']),
            source=EpisodeType.json,
            source_description=episode['description'],
            reference_time=datetime.now(timezone.utc),
        )


    finally:
        # close the connection
        await graphiti.close()
        print('\nConnection closed')
async def find_episode(graphiti,query):
    try:
        await graphiti.build_indices_and_constraints()
        results = await graphiti.search(query)

        for result in results:
            print(f'UUID: {result.uuid}')
            print(f'Fact: {result.fact}')
            if hasattr(result, 'valid_at') and result.valid_at:
                print(f'Valid from: {result.valid_at}')
            if hasattr(result, 'invalid_at') and result.invalid_at:
                print(f'Valid until: {result.invalid_at}')
            print('---')

    finally:
        await graphiti.close()
        print('\nConnection closed')
if __name__ == "__main__":
    graphiti = get_graphiti_obj()
    #res=asyncio.run(get_prompt("Marie Curie discovered radium and worked at Sorbonne University in Paris."))

    result =asyncio.run(get_structured_data("Marie Curie discovered radium and worked at Sorbonne University in Paris."))
    #print(result)




    asyncio.run(add_episode(graphiti,result))
    #asyncio.run(main(graphiti))




