import cv2
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import pygame
import os
from ultralytics import YOLO
model = YOLO('model1.pt')
# Initialize pygame mixer
model_relax = YOLO("model2.pt")
pygame.mixer.init()
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def show_static_image(image_path):
    # Open the image file
    image = Image.open(image_path)

    # Resize the image if needed
    image = image.resize((800, 500))

    # Convert the Image object into a Tkinter PhotoImage object
    tk_image = ImageTk.PhotoImage(image)

    # Update the label with the new image
    label_live_feed.configure(image=tk_image)
    label_live_feed.image = tk_image

# Function to capture image from camera
def capture_image():
    cap = cv2.VideoCapture(0)  # Open the default camera
    if not cap.isOpened():
        messagebox.showerror("Error", "Could not open camera.")
        return None

    ret, frame = cap.read()  # Read frame from the camera
    if not ret:
        messagebox.showerror("Error", "Could not read frame.")
        return None

    cap.release()  # Release the camera
    return frame

# Function to save captured image locally
def save_image(image):
    cv2.imwrite("captured_image.jpg", image)  # Save the image locally
    messagebox.showinfo("Success", "Image saved as captured_image.jpg")
    song_select_button.pack()  # Show the song selection button
    pause_button.pack()  # Show the pause button
    song_combobox.pack()  # Show the dropdown menu

# Function to handle capture image button click
def on_capture_button_click():
    song_combobox.set('')
    song_combobox['values'] = []
    captured_image = capture_image()
    if captured_image is not None:
        save_image(captured_image)
        label_live_feed.after_cancel(update_id)
          # Stop the live stream
        perform_object_detection(captured_image)

# Function to perform object detection
def perform_object_detection(image):
    # Load the YOLOv8 model
    # populate_song_combobox("")
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    
    for (x, y, w, h) in faces:
        # Extract the face region
        face_region = image[y:y+h, x:x+w]
        
        # Pass the face region to your relaxation model for emotion detection
        relax_emotion = model_relax(image, conf=0.5)
        
        # Assuming relax_emotion is a list of results, process each result
        for result in relax_emotion:
            if result.boxes:  # If the result contains bounding boxes
                box = result.boxes[0]  # Assuming only one box is detected
                class_id = int(box.cls)
                object_name = model_relax.names[class_id]
                print(object_name)
                
                # Draw bounding box around the face and label it if the object is 'open_eyes'
                if object_name == 'close_eye':
                    # Draw bounding box
                    cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    
                    # Label the face
                    cv2.putText(image, "Relax", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                    
                    # Save the resulting image
                    cv2.imwrite("result.jpg", image)
                    
                    # Show the image with bounding box and label
                    show_static_image("result.jpg")
                    
                    # Perform your desired action, such as mapping songs to folder
                    map_songs_to_folder("relax")
            
                # Run inference on the captured image
                else:
                    results = model(image,conf=0.5)
                    res_plotted = results[0].plot()
                    cv2.imwrite("result.jpg", res_plotted)
                    show_static_image("result.jpg")
                    # Check for detected objects
                    for result in results:
                        if result.boxes:
                            box = result.boxes[0]
                            class_id = int(box.cls)
                            object_name = model.names[class_id]
                            map_songs_to_folder(object_name)

# Function to map object name to folder and list songs
def map_songs_to_folder(object_name):
    # Define a dictionary mapping object names to song folders
    object_to_folder_map = {
        "sad": "songs/sad",
        "angry": "songs/angry",
        "happy": "songs/happy",
        "romantic": "songs/romantic",
        "relax": "songs/relax"
    }

    # Get the folder name based on the detected object
    folder_name = object_to_folder_map.get(object_name)

    # Check if folder exists
    if folder_name and os.path.exists(folder_name):
        # List all MP3 files within the folder
        song_files = [os.path.join(folder_name, file) for file in os.listdir(folder_name) if file.endswith('.mp3')]
        populate_song_combobox(song_files)
    else:
        messagebox.showinfo("Info", "No songs found for the detected object.")

# Function to populate song dropdown menu
def populate_song_combobox(song_files):
    song_combobox.config(values=song_files)  # Update the dropdown menu with song options

# Create the main application window
root = tk.Tk()
root.title("EmoSense")

# Configure style
style = ttk.Style()
style.configure("BW.TLabel", foreground="black", background="white")  # You can change the theme to any supported theme

# Create a label to display the live feed
label_live_feed = tk.Label(root)
label_live_feed.pack()

def on_submit_button_click():
    selected_song = song_combobox.get()  # Get the selected song from the dropdown menu
    if not selected_song:
        messagebox.showerror("Error", "Please select a song.")
        return
    try:
        pygame.mixer.music.load(selected_song)  # Load the selected song
        pygame.mixer.music.play()  # Play the selected song
    except pygame.error as e:
        messagebox.showerror("Error", f"Failed to play the song: {e}")

def on_pause_button_click():
    if pygame.mixer.music.get_busy():  # Check if music is playing
        pygame.mixer.music.pause()  # Pause the music
    else:
        messagebox.showinfo("Info", "No music is playing.")

# Create a button to capture an image
capture_button = tk.Button(root, text="Capture Image", command=on_capture_button_click)
capture_button.pack()

# Get the directory containing the music files
music_directory = "songs"

# Create a dropdown menu to select songs
song_combobox = ttk.Combobox(root)

# Create a button to select and play the song
song_select_button = tk.Button(root, text="Play", command=on_submit_button_click)

# Create a button to pause the music
pause_button = tk.Button(root, text="Pause", command=on_pause_button_click)

# Function to update live feed (unchanged from previous code)
def update_live_feed():
    ret, frame = cap.read()
    if ret:
        # Resize the frame to fit the container size (800x500)
        frame = cv2.resize(frame, (800, 500))

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert the frame to RGB format
        frame_pil = Image.fromarray(frame_rgb)  # Convert the frame to PIL format
        frame_tk = ImageTk.PhotoImage(frame_pil)  # Convert the frame to Tkinter format
        label_live_feed.configure(image=frame_tk)  # Update the live feed label
        label_live_feed.image = frame_tk
        global update_id
        update_id = label_live_feed.after(10, update_live_feed)

# Open the default camera (unchanged from previous code)
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    messagebox.showerror("Error", "Could not open camera.")
    root.destroy()

def start_live_feed():
    global cap
    cap = cv2.VideoCapture(0)  # Re-open the default camera
    if not cap.isOpened():
        messagebox.showerror("Error", "Could not open camera.")
        root.destroy()
        return

    # Call the update_live_feed function to start updating the live feed
    update_live_feed()

# Create a button to start live feed
start_feed_button = tk.Button(root, text="Start Live Feed", command=start_live_feed)
start_feed_button.pack()

# Call the update_live_feed function (unchanged from previous code)
update_live_feed()

# Run the Tkinter event loop
root.mainloop()