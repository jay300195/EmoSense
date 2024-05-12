import cv2
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import pygame
import os

# Initialize pygame mixer
pygame.mixer.init()

# Function to capture image from camera
def capture_image():
    cap = cv2.VideoCapture(0)  # Open the default camera (usually the webcam)
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
    captured_image = capture_image()
    if captured_image is not None:
        save_image(captured_image)
        label_live_feed.after_cancel(update_id)  # Stop the live stream
        captured_image = cv2.cvtColor(captured_image, cv2.COLOR_BGR2RGB)  # Convert the image to RGB format
        captured_image_pil = Image.fromarray(captured_image)  # Convert the image to PIL format
        captured_image_tk = ImageTk.PhotoImage(captured_image_pil)  # Convert the image to Tkinter format
        label_live_feed.configure(image=captured_image_tk)  # Display the captured image on a label
        label_live_feed.image = captured_image_tk

# Function to handle submit button click
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

# Function to handle pause button click
def on_pause_button_click():
    if pygame.mixer.music.get_busy():  # Check if music is playing
        pygame.mixer.music.pause()  # Pause the music
    else:
        messagebox.showinfo("Info", "No music is playing.")

# Create the main application window
root = tk.Tk()
root.title("Image Capture and Music Player")

# Create a label to display the live feed
label_live_feed = tk.Label(root)
label_live_feed.pack()

# Create a button to capture an image
capture_button = tk.Button(root, text="Capture Image", command=on_capture_button_click)
capture_button.pack()

# Get the directory containing the music files
music_directory = "songs"
# List the songs available in the directory
song_files = [os.path.join(music_directory, file) for file in os.listdir(music_directory) if file.endswith('.mp3')]

# Create a dropdown menu to select songs
song_combobox = ttk.Combobox(root, values=song_files)

# Create a button to select and play the song
song_select_button = tk.Button(root, text="Submit", command=on_submit_button_click)

# Create a button to pause the music
pause_button = tk.Button(root, text="Pause", command=on_pause_button_click)

# Function to update live feed
def update_live_feed():
    ret, frame = cap.read()
    if ret:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert the frame to RGB format
        frame_pil = Image.fromarray(frame_rgb)  # Convert the frame to PIL format
        frame_tk = ImageTk.PhotoImage(frame_pil)  # Convert the frame to Tkinter format
        label_live_feed.configure(image=frame_tk)  # Update the live feed label
        label_live_feed.image = frame_tk
        global update_id
        update_id = label_live_feed.after(10, update_live_feed)  # Repeat after 10 milliseconds

# Open the default camera (usually the webcam)
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    messagebox.showerror("Error", "Could not open camera.")
    root.destroy()

# Call the update_live_feed function to start displaying the live feed
update_live_feed()

# Run the Tkinter event loop
root.mainloop()
