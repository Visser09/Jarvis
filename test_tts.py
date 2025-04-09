import edge_tts
import asyncio
import os

async def test_tts():
    print("Starting Edge TTS test...")
    try:
        # Step 1: Create communicate object
        print("Step 1: Creating communicate object...")
        communicate = edge_tts.Communicate("Hello sir, this is a test.", "en-GB-RyanNeural")
        print("✓ Communicate object created successfully")
        
        # Step 2: Generate and save audio
        print("Step 2: Generating and saving audio...")
        await communicate.save("test.mp3")
        print("✓ Audio generated and saved successfully")
        
        # Step 3: Try to play using system command
        print("Step 3: Attempting to play audio...")
        if os.name == 'nt':  # Windows
            os.system("start test.mp3")
        else:  # Linux/Mac
            os.system("xdg-open test.mp3")
        print("✓ Audio playback command sent")
        
        # Wait a moment
        await asyncio.sleep(2)
        
        # Cleanup
        try:
            os.remove("test.mp3")
            print("✓ Test file cleaned up")
        except:
            print("! Could not remove test file")
            
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print("Full traceback:")
        print(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(test_tts()) 