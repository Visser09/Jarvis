import os
import requests

def test_api_key():
    # Set API key directly
    api_key = "sk_e9b6a835b30c12ea56b5e72bee707d61e9750be182489fdd"
    
    try:
        # Test the API key by making a direct request to ElevenLabs API
        headers = {
            "xi-api-key": api_key
        }
        response = requests.get(
            "https://api.elevenlabs.io/v1/voices",
            headers=headers
        )
        
        if response.status_code == 200:
            print("Success: ElevenLabs API key loaded successfully")
            voices = response.json()
            print(f"Found {len(voices['voices'])} available voices")
            return True
        else:
            print(f"Error: API returned status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error testing API key: {str(e)}")
        return False

if __name__ == "__main__":
    test_api_key() 