import re
import langchain
import pathlib
from langchain_core.language_models import BaseLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import GoogleGenerativeAI
from langchain_ollama import OllamaLLM
import asyncio
from typing import List
from dotenv import load_dotenv



# def load_model(model_name="qwen2.5-coder:0.5b") -> BaseLLM:
#     print("Loading model:", model_name)
#     return OllamaLLM(model=model_name)

def load_model(model_name: str = "gemini-2.0-flash-lite") -> BaseLLM:
    print("Loading model:", model_name)
    load_dotenv()
    return GoogleGenerativeAI(model=model_name)


def init_langchain():
    model = load_model()
    prompt = PromptTemplate.from_template(
        "You are an AI assistant that names files based on their content.\n"
        "You shouldn't explain anything, only output a file name for the content without extension.\n"
        "The name should tell the user what the file is about, a summary perhaps. dont copy paste the file content.\n"
        "Suggest a descriptive name (in snake_case format only) for the following file content:\n\n{content}\n\nName:"
    )
    chain = prompt | model | StrOutputParser()
    return chain


def sanitize_filename(name: str, replace_space_with: str = "_", allow_dot: bool = False) -> str:
    """
    Sanitize a string to make it a safe filename.

    Parameters:
    - name: The input string.
    - replace_space_with: Character to replace spaces with (default: "_").
    - allow_dot: Whether to allow dots (default: False).

    Returns:
    - A sanitized string safe for use as a filename.
    """
    # Normalize spaces
    name = name.strip().replace(" ", replace_space_with)

    # Remove unsafe characters
    if allow_dot:
        # Allow only alphanumeric, underscore, dash, and dot
        name = re.sub(r"[^a-zA-Z0-9_\-\.]", "", name)
    else:
        # Allow only alphanumeric, underscore, and dash
        name = re.sub(r"[^a-zA-Z0-9_\-]", "", name)

    # Remove leading/trailing dots or dashes if present
    name = name.strip("._-")

    return name


async def generate_name_for_file(file: pathlib.Path, chain) -> str | None:
    '''Calls langchain to generate a name for the file.
    Can return None if the file is not text-based or if the generation fails.
    In which case we default to the old name for the file.
    '''
    # Try reading the file content
    content = ""
    try:
        with open(file, "r") as f:
            content = f.read()
    except:
        print(f"Could not read file {file}")
        return None

    try:
        name = await chain.ainvoke({"content": content})
        # print(f"Model response:{file.stem} -> {name}")
        return name.strip()
    except Exception as e:
        print(f"Error generating name for {file}: {e}")
        return None


async def generate_names_for_files(files: List[pathlib.Path], chain) -> List[str | None]:
    tasks = [generate_name_for_file(file, chain) for file in files]
    return await asyncio.gather(*tasks)


def generate_names(files: List[pathlib.Path]):
    '''Generates names for the files using langchain, asynchronously.
    Returns a list of new names for the files, if the generation succeeds.
    If the generation fails for a file, the name is set to the old name of the file.
    '''

    chain = init_langchain()

    # this may contain None values if the file is not text-based or if the generation fails
    new_names = asyncio.run(generate_names_for_files(files, chain))

    # Replace the None values with the original file names
    final_names = []
    for file, new_name in zip(files, new_names):
        if new_name is None:
            final_names.append(f"{file.parent}/{file.stem}{file.suffix}")
        else:
            new_name = sanitize_filename(new_name)
            final_names.append(f"{file.parent}/{new_name}{file.suffix}")

    return final_names
