import os
from dotenv import load_dotenv
from google import genai

# Read the secret key from your .env file
load_dotenv()

# Create ONE client; it holds your auth and is what you talk to
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# Ask the client's model service for a completion
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="You are talking to Mr. Nam, a teacher/ AI developer. Greet him in one short sentence",
)

print("Gemini replied:", response.text)
