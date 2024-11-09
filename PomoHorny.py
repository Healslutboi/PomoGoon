import vlc
import time
import os
import tkinter as tk
from tkinter import simpledialog, filedialog
import pygame
import random

def play_audio(audio_path):
    # Initialize pygame mixer
    pygame.mixer.init()

    # Load the audio file
    pygame.mixer.music.load(audio_path)

    # Play the audio file
    pygame.mixer.music.play()

    # Wait until the audio finishes playing
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

def play_video(video_path):
    # Check if the video file exists
    if not os.path.exists(video_path):
        print(f"Error: The file at {video_path} does not exist.")
        return

    # Create an instance of the VLC player
    player = vlc.MediaPlayer(video_path)

    # Set the player to full-screen mode
    player.set_fullscreen(True)

    # Play the video
    player.play()

    # Add a delay to ensure the player starts
    time.sleep(1)

    # Check for errors
    if player.get_state() == vlc.State.Error:
        print(f"Error: Unable to play the video at {video_path}.")
        return

    # Wait until the video finishes playing
    while player.is_playing():
        time.sleep(1)

    # Stop the player and close the window
    player.stop()

def get_random_video_path(folder_path):
    # Get a list of all video files in the folder and subfolders
    video_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(('.mp4', '.avi', '.mkv')):
                video_files.append(os.path.join(root, file))
    # Select a random video file
    return random.choice(video_files) if video_files else None

def select_video_folder():
    global video_folder
    video_folder = filedialog.askdirectory(title="Select Video Folder")
    if not video_folder:
        print("No video folder selected.")

def select_audio_file():
    global audio_path
    audio_path = filedialog.askopenfilename(title="Select Audio File", filetypes=[("Audio Files", "*.mp3 *.wav")])
    if not audio_path:
        print("No audio file selected.")

def main():
    global video_folder, audio_path
    video_folder = None
    audio_path = None

    # Create a Tkinter root window
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Create a new window for selecting files
    file_select_window = tk.Toplevel(root)
    file_select_window.title("Select Files")

    # Add buttons to select video folder and audio file
    select_video_button = tk.Button(file_select_window, text="Select Video Folder", command=select_video_folder)
    select_video_button.pack(pady=10)

    select_audio_button = tk.Button(file_select_window, text="Select Audio File", command=select_audio_file)
    select_audio_button.pack(pady=10)

    # Add a button to start the main process
    start_button = tk.Button(file_select_window, text="Start", command=file_select_window.destroy)
    start_button.pack(pady=10)

    root.wait_window(file_select_window)

    if not video_folder or not audio_path:
        print("Video folder or audio file not selected. Exiting.")
        return

    # Ask the user for the interval in minutes
    interval_minutes = simpledialog.askfloat("Input", "Enter the interval in minutes:", minvalue=0.01)
    if interval_minutes is None:
        print("No interval provided. Exiting.")
        return

    while True:
        time.sleep(interval_minutes * 60)
        # Create a new Tkinter window to be on top and full screen
        top = tk.Toplevel()
        top.attributes("-fullscreen", True)  # Full screen
        top.attributes("-topmost", True)  # Always on top
        top.attributes("-disabled", True)  # Disable user input
        top.withdraw()  # Hide the window
        play_audio(audio_path)  # Play the audio
        video_path = get_random_video_path(video_folder)  # Get a random video file
        if video_path:
            print(f"Playing video: {video_path}")
            play_video(video_path)  # Play the video
        else:
            print("No video files found.")
        top.destroy()  # Destroy the window after the video is played

if __name__ == "__main__":
    main()