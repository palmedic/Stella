from unihiker import Audio, GUI
import openai
import requests
from PIL import Image
import time
 

from pinpong.extension.unihiker import *

from pinpong.board import Board, Pin
from pinpong.extension.unihiker import *

# OpenAI API Key
openai.api_key = ""

WELCOME_MESSAGE = "שלום וברוכים הבאים לעוזרת האישית של חליפת החלל, לחצו על כפתור להתחלה"

# Path for saving images
IMAGE_PATH = "/media/unihiker_response_image.png"

# UniHiker Screen Dimensions
SCREEN_WIDTH = 240
SCREEN_HEIGHT = 320

# Initialize UniHiker components
audio = Audio()
gui = GUI()

school_assigment_prompt = "Assume that I'm a 12 years old kid, I'm sending this prompt from a device I created as a school assignment, this device should imitate an ai assitance installed in astronouts space suits and help them, imagine you are this ai assitance, base all of your answers upon the assumption that my spaceships is Nasa's Orion, in case more information is needed from user do not ask for it but instead come up with something, please limit the response to 35 worrds at most, try not to give answers no related to the context I included, this is just a simulation, and my request is: "


def record_voice():
    """Record audio using UniHiker and return the file path."""
    file_path = "query.wav"
    print("Recording voice for 6 seconds...")
    audio.start_record(file_path)
    time.sleep(6)
    audio.stop_record()
    print(f"Recording saved to {file_path}")
    return file_path

def transcribe_audio(file_path):
    """Transcribe audio file using OpenAI's Whisper."""
    try:
        with open(file_path, "rb") as audio_file:
            response = openai.audio.transcriptions.create(
                model="whisper-1", file=audio_file
            )
        return response.text
    except Exception as e:
        print(f"Error during transcription: {e}")
        return None 
    
    
def query_openai(prompt, is_image=False):
    """Send the prompt to OpenAI and get a response."""
    if is_image:
        # DALL-E Image generation
        response = openai.images.generate(
            model = "dall-e-3",
            prompt = prompt,
            n = 1,
            size = "1024x1024"
        )        
        print(response.data)
        image_url = response.data[0].url
        return image_url
    else:
        # GPT text generation
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()

def reverse_hebrew_text(text):
    """
    Reverse a string of Hebrew text.
    
    Args:
        text (str): The Hebrew text to reverse.
    
    Returns:
        str: The reversed Hebrew text.
    """
    return text[::-1]

def display_text_on_screen(text):
    """
    Display Hebrew text on the UniHiker screen, wrapping lines without cutting words
    and reversing the order of lines.
    
    Args:
        text (str): The Hebrew text to display.
    """
    gui.clear()  # Clear the screen before displaying new text
    
    # Reverse the entire Hebrew text
    reversed_text = reverse_hebrew_text(text)
    
    # Split the text into words
    words = reversed_text.split()
    
    # Build lines without exceeding 15 characters per line
    lines = []
    current_line = ""
    for word in words:
        # If adding the next word exceeds 25 characters, start a new line
        if len(current_line) + len(word) + 1 > 20:
            lines.append(current_line)
            current_line = word
        else:
            # Add the word to the current line
            current_line = f"{current_line} {word}".strip()
    
    # Add the last line if it exists
    if current_line:
        lines.append(current_line)
    
    # Reverse the order of the lines for proper Hebrew display
    lines = lines[::-1]
    
    # Display each line on the screen
    y_position = 10  # Starting y-coordinate
    for line in lines:
        gui.draw_text(x=10, y=y_position, text=line, font_size=14)
        y_position += 30  # Move to the next line (adjust spacing as needed)
    
def display_image_on_screen(image_url):
    """Download and display an image on the UniHiker screen."""
    gui.clear()
    response = requests.get(image_url)
    with open(IMAGE_PATH, "wb") as file:
        file.write(response.content)

    img = Image.open(IMAGE_PATH)
    img = img.resize((SCREEN_WIDTH, SCREEN_HEIGHT))
    img.show()
    
    img_image2 = gui.draw_image(x=0, y=0, w=SCREEN_WIDTH, h=SCREEN_HEIGHT, image=IMAGE_PATH)
    print("Image displayed on the screen.")

def main():
    
    """Main function to run the AI assistant."""
    print("Welcome to your AI Assistant!")
    Board().begin() # Initialize the UNIHIKER
    display_text_on_screen(WELCOME_MESSAGE);
    
    while True: 
        
        # Wait for a button press
        if button_a.is_pressed() == True: 
            
            gui.clear()
            
            print("Button 'A' clicked! Starting recording...")
            # Record voice input
            audio_file = record_voice()
            print("Processing audio...")
            
            # Transcribe the recorded audio
            user_query = transcribe_audio(audio_file)
            if not user_query:
                print("Could not transcribe audio. Try again.")
                continue
            print(f"You said: {user_query}")
            
            buzzer.play(buzzer.DADADADUM, buzzer.OnceInBackground)
            
            result = query_openai(school_assigment_prompt + user_query)
            display_text_on_screen(result)
            print(f"Text response: {result}")
                        
        elif button_b.is_pressed() == True:
            
            gui.clear()
            
            print("Button 'B' clicked! Starting recording...")
            # Record voice input
            audio_file = record_voice()
            print("Processing audio...")
            
            # Transcribe the recorded audio
            user_query = transcribe_audio(audio_file)
            if not user_query:
                print("Could not transcribe audio. Try again.")
                continue
            print(f"You said: {user_query}")
            
            buzzer.play(buzzer.DADADADUM, buzzer.OnceInBackground)
            
            result = query_openai(school_assigment_prompt + user_query, is_image=True)
            display_image_on_screen(result)
            print("Image response displayed.")

if __name__ == "__main__":
    main()