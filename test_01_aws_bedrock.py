"""
Test 1: AWS Bedrock Nova Lite connection
"""
import os
from dotenv import load_dotenv
from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage

load_dotenv()

print("🧪 Test 1: AWS Bedrock Connection")
print("=" * 60)

# Check credentials
print(f"✓ AWS_ACCESS_KEY_ID: {os.getenv('AWS_ACCESS_KEY_ID')[:10]}...")
print(f"✓ AWS_REGION: {os.getenv('AWS_REGION')}")
print(f"✓ MODEL: {os.getenv('BEDROCK_MODEL')}")

# Test connection
print("\n📡 Testing Bedrock API...")
llm = ChatBedrock(
    model_id=os.getenv("BEDROCK_MODEL", "amazon.nova-lite-v1:0"),
    region_name=os.getenv("AWS_REGION", "us-east-1"),
    model_kwargs={
        "temperature": 0.7,
        "max_tokens": 100,
    }
)

response = llm.invoke([HumanMessage(content="Say 'Hello from AWS Bedrock!' in one sentence.")])
print(f"✅ Response: {response.content}")
print("\n✅ Test 1 PASSED: AWS Bedrock is working!")
