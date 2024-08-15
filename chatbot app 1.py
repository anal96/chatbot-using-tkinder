import tkinter as tk
from tkinter import simpledialog, messagebox, StringVar
import google.generativeai as genai
import speech_recognition as sr
import pyttsx3
import threading

mic_enabled = False  # Declare mic_enabled globally
history = []  # Conversation history list

def configure_and_create_model(api_key):
    """Configures the API key and creates a GenerativeModel instance."""
    genai.configure(api_key=api_key)

    generation_config = {
        "temperature": 1.0,
        "top_p": 0.95,
        "top_k": 0,
        "max_output_tokens": 8192,
    }

    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    ]

    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro-latest", generation_config=generation_config, safety_settings=safety_settings
    )
    return model

def chat(convo, user_input):
    """Sends user input to the model and retrieves its response."""
    convo.send_message(user_input)
    response = convo.last.text
    history.append((user_input, response))  # Append user input and response to history
    return response

def speak(text):
    """Converts text to speech using pyttsx3."""
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def listen():
    """Listens for user input using SpeechRecognition and returns text."""
    global mic_enabled
    if not mic_enabled:
        return None
    
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source)  # Adjust for ambient noise
        
        retry_count = 0  # Initialize retry count
        max_retry = 3    # Maximum number of retries
        
        while retry_count < max_retry:
            audio = r.listen(source)
            try:
                text = r.recognize_google(audio)
                print("You said:", text)
                return text.lower()
            except sr.UnknownValueError:
                print("Sorry, could not understand audio. Please try again.")
                retry_count += 1  # Increment retry count
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))
                return None
            else:
                # Speech detected, break out of the loop
                break

def get_input_method(input_method):
    """Returns a function to handle user input."""
    print("Input method:", input_method)  # Print input method for debugging
    global mic_enabled  # Declare mic_enabled as global
    if input_method == "mic🎤":
        mic_enabled = True
        return listen
    elif input_method == "Keyboard⌨️":
        mic_enabled = False
        return lambda: user_input_text.get("1.0", tk.END).strip()

def chat_thread(convo, input_method):
    """Function to handle chat in a separate thread."""
    user_input = get_input_method(input_method)()
    if user_input is None:
        return  # Stop execution if user input is empty or not recognized
    if user_input == "quit":
        root.quit()
    
    # Clear input box
    user_input_text.delete(1.0, tk.END)
    
    response = chat(convo, user_input)
    print("chatbot: ", response)

    # Display user input and chatbot response with appropriate alignment
    chat_window.tag_configure("left", justify="left")
    chat_window.tag_configure("right", justify="right")

    chat_window.insert(tk.END, "You👨‍🚀 : " + user_input + "\n", "left")
    chat_window.insert(tk.END, "\n")
    chat_window.insert(tk.END, "Chatbot🤖 : " + response + "\n", "left")
    chat_window.insert(tk.END, "\n")

    chat_window.see(tk.END)  # Scroll to the end of the chat window
    
    if response_preference.get() == "on":
        speak(response)

def clear_chat_window():
    """Clears all the contents of the chat window."""
    chat_window.delete(1.0, tk.END)

def main():
    """Main function to run the chatbot."""
    api_key = "AIzaSyBMr9BP9hAoGdCqT_3r4M5in9EplVaj_wA"  # Replace with your actual API key
    model = configure_and_create_model(api_key)
    convo = model.start_chat(history=[])

    global root
    root = tk.Tk()
    root.title("Chatbot")

    # Set background color and font styles
    root.configure(background="#f0f0f0")
    root.option_add("*Font", "Helvetica 12")

    # Title bar
    title_bar = tk.Label(root, text="  CHAT BOT", bg="#009688", fg="white", height=55, font=("Helvetica", 16, "bold"))
    title_bar.pack(fill=tk.X)

    # Load and display the image
    title_image = tk.PhotoImage(file="chatbot.png")  # Replace "chat.png" with the actual path
    title_image = title_image.subsample(9, 9)  # Resizing the image
    title_bar.config(image=title_image, compound=tk.LEFT)

    # Define chat_window before use
    global chat_window
    chat_window = tk.Text(root, height=20, width=100, bg="white", fg="black")
    chat_window.pack(pady=10)

    # Add radio buttons for response preference
    response_frame = tk.Frame(root, bg="#f0f0f0")
    response_frame.pack(pady=10)

    response_label = tk.Label(response_frame, text="Speaker🔊", bg="#f0f0f0")
    response_label.pack(side=tk.LEFT)

    global response_preference
    response_preference = tk.StringVar(root)
    response_preference.set("off")  # Default response preference

    response_yes_button = tk.Radiobutton(response_frame, text="on", variable=response_preference, value="on", bg="#f0f0f0")
    response_yes_button.pack(side=tk.LEFT, padx=10)

    response_no_button = tk.Radiobutton(response_frame, text="off", variable=response_preference, value="off", bg="#f0f0f0")
    response_no_button.pack(side=tk.LEFT)

    # Input frame
    input_frame = tk.Frame(root, bg="#f0f0f0")
    input_frame.pack()

    input_label = tk.Label(input_frame, text="You👨‍🚀:", bg="#f0f0f0")
    input_label.pack(side=tk.LEFT)

    global user_input_text
    user_input_text = tk.Text(input_frame, height=1, width=50)
    user_input_text.pack(side=tk.LEFT)
    user_input_text.insert(tk.END, "Enter your message...")  # Default message
    user_input_text.configure(fg="gray")  # Set text color to gray

    # Function to send message when Enter key is pressed
    def send_message(event):
        chat_thread(convo, input_method_var.get())

    # Bind Enter key to send_message function
    user_input_text.bind("<Return>", send_message)

    send_button = tk.Button(input_frame, text="Send➡️", bg="#009688", fg="white", command=lambda: threading.Thread(target=chat_thread, args=(convo, input_method_var.get())).start())
    send_button.pack(side=tk.LEFT, padx=10)

    send_button = tk.Button(input_frame, text="Voice🎙️", bg="#009688", fg="white", command=lambda: threading.Thread(target=chat_thread, args=(convo, input_method_var.get())).start())
    send_button.pack(side=tk.LEFT, padx=10)

    # Add a clear button to clear the chat window
    clear_button = tk.Button(root, text="Clear Chat🔄️", bg="#009688", fg="white", command=clear_chat_window)
    clear_button.pack(side=tk.BOTTOM, pady=10)

    global input_method_var
    input_method_var = StringVar(root)
    input_method_var.set("Keyboard⌨️")  # Default input method

    input_method_menu = tk.OptionMenu(root, input_method_var, "mic🎤", "Keyboard⌨️")
    input_method_menu.config(bg="#009688", fg="white")  # Set background color and text color
    input_method_menu.pack(side=tk.RIGHT, padx=20)

    # Configure Text widget to display comment boxes
    chat_window.tag_configure("comment", foreground="gray")

    root.mainloop()

if __name__ == "__main__":
    main()
