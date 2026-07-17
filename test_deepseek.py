from dotenv import load_dotenv

load_dotenv()

from app.llm.deepseek_client import call_deepseek

res = call_deepseek("Say hello in JSON format only")
print(res)