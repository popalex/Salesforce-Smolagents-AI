import datetime
import os

import pytz
import requests
import yaml
from dotenv import load_dotenv
from simple_salesforce import Salesforce
from smolagents import (CodeAgent, DuckDuckGoSearchTool, HfApiModel, load_tool,
                        tool)

from Gradio_UI import GradioUI

load_dotenv('.env')


# Below is an example of a tool that does nothing. Amaze us with your creativity!
@tool
def my_custom_tool(arg1:str, arg2:int)-> str: # it's important to specify the return type
    # Keep this format for the tool description / args description but feel free to modify the tool
    """A tool that does nothing yet 
    Args:
        arg1: the first argument
        arg2: the second argument
    """
    return "What magic will you build ?"

@tool
def get_current_time_in_timezone(timezone: str) -> str:
    """A tool that fetches the current local time in a specified timezone.
    Args:
        timezone: A string representing a valid timezone (e.g., 'America/New_York').
    """
    try:
        # Create timezone object
        tz = pytz.timezone(timezone)
        # Get current time in that timezone
        local_time = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        return f"The current local time in {timezone} is: {local_time}"
    except Exception as e:
        return f"Error fetching time for timezone '{timezone}': {str(e)}"

@tool
def get_active_insurance_policies() -> str:
    """A tool that fetches the number of active insurance policies from Salesforce.
    Returns:
        A string indicating the number of active insurance policies.
    """
    try:
        # Load Salesforce credentials from environment variables
        sf_username = os.getenv("SALESFORCE_USERNAME")
        sf_password = os.getenv("SALESFORCE_PASSWORD")
        sf_token = os.getenv("SALESFORCE_SECURITY_TOKEN")

        print("Loaded Salesforce credentials from environment variables.")

        # Connect to Salesforce
        sf = Salesforce(username=sf_username, password=sf_password, security_token=sf_token)

        print("Connected to Salesforce.")

        # Query Salesforce for active insurance policies
        # query = "SELECT COUNT() FROM InsurancePolicy__c WHERE Status__c = 'Active'"
        query = "SELECT COUNT() FROM Account WHERE Type = 'Customer - Direct' "
        print(f"Executing Salesforce query: {query}")
        result = sf.query(query)

        # Extract the count from the query result
        active_policies_count = result['totalSize']

        print(f"Active insurance policies count: {active_policies_count}") 

        return f"The number of active insurance policies is: {active_policies_count}"
    except Exception as e:
        return f"Error fetching active insurance policies: {str(e)}"

# final_answer = FinalAnswerTool()

# If the agent does not answer, the model is overloaded, please use another model or the following Hugging Face Endpoint that also contains qwen2.5 coder:
# model_id='https://pflgm2locj2t89co.us-east-1.aws.endpoints.huggingface.cloud' 

model = HfApiModel(
    max_tokens=2096,
    temperature=0.5,
    model_id='Qwen/Qwen2.5-Coder-32B-Instruct',
    # model_id='https://pflgm2locj2t89co.us-east-1.aws.endpoints.huggingface.cloud',
    custom_role_conversions=None,
)


# Import tool from Hub
image_generation_tool = load_tool("agents-course/text-to-image", trust_remote_code=True)

# Load system prompt from prompt.yaml file
with open("prompts.yaml", 'r') as stream:
    prompt_templates = yaml.safe_load(stream)
    
agent = CodeAgent(
    model=model,
    tools=[my_custom_tool,get_current_time_in_timezone,get_active_insurance_policies], # add your tools here (don't remove final_answer)
    max_steps=6,
    verbosity_level=1,
    grammar=None,
    planning_interval=None,
    name=None,
    description=None,
    prompt_templates=prompt_templates # Pass system prompt to CodeAgent
)

GradioUI(agent).launch()
