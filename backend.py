import langchain
import pathlib
from langchain_core.language_models import BaseLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import ChatGoogleGenerativeAI
from langchain_community.llms import Ollama
import asyncio
from typing import List


def load_model(model_name="qwen2.5-coder:0.5b") -> BaseLLM:
    return Ollama(model=model_name)

# def load_model(model_name: str = "gemini-2-flash") -> BaseLLM:
#     return ChatGoogleGenerativeAI(model=model_name, convert_system_message_to_human=True)

def init_langchain():
    model = load_model()
    prompt = PromptTemplate.from_template(
        "You are an AI assistant that names files based on their content.\n"
        "You shouldn't explain anything, only output a file name for the content without extension.\n"
        "Suggest a descriptive name for the following file content:\n\n{content}\n\nName:"
    )
    chain = prompt | model | StrOutputParser()
    return chain

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
        # name = await chain.ainvoke({"content": content})
        # TODO:
        name = content[:10]
        return name.strip()
    except Exception as e:
        print(f"Error generating name for {file}: {e}")
        return None

async def generate_names_for_files(files: List[pathlib.Path], chain) -> List[str|None]:
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
            final_names.append(f"{file.parent}/{new_name}{file.suffix}")

    return final_names