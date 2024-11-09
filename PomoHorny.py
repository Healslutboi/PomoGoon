import vlc
import time
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import pygame
import random
import threading

# Global flag to stop the program and video playback
stop_program = False

def play_audio(audio_path):
    """Play the alarm audio file (using pygame for audio only)."""
    pygame.mixer.init()
    pygame.mixer.music.load(audio_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

def play_video(video_path, gui_root, iconify):
    """Play the selected video file with VLC and disable user interaction with the GUI."""
    if not os.path.exists(video_path):
        print(f"Error: The file at {video_path} does not exist.")
        return

    # Minimize or withdraw the GUI based on the user's choice
    if iconify:
        gui_root.iconify()
    else:
        gui_root.withdraw()

    # Create a new top-level window for fullscreen and control video display
    top = tk.Toplevel(gui_root)
    top.attributes("-fullscreen", True)  # Make the window fullscreen
    top.attributes("-topmost", True)     # Keep it always on top

    top.attributes("-disabled", True)    # Disable all user input on this window
    top.configure(bg="black")             # Set background color to black (optional)
    top.config(cursor="none")             # Hide the cursor during video playback


    # Create VLC MediaPlayer and play the video
    player = vlc.MediaPlayer(video_path)

    # Use the top-level window's handle (ID) to make the video fit inside this window
    player.set_hwnd(top.winfo_id())  # Bind the VLC window to the top-level window

    # Start the video in fullscreen mode
    player.play()
    time.sleep(1)  # Allow some time for the video to start

    if player.get_state() == vlc.State.Error:
        print(f"Error: Unable to play the video at {video_path}.")
        top.destroy()  # Close the top-level window if there's an error
        gui_root.deiconify()
        return

    # Wait until the video finishes playing or until the program is stopped
    while player.is_playing() and not stop_program:
        time.sleep(1)

    player.stop()
    top.destroy()  # Close the top-level window when the video finishes
    gui_root.deiconify()  # Restore the original GUI window


def get_random_video_path(folder_path):
    """Get a random video file path from the selected folder."""
    video_files = [os.path.join(root, file)
                   for root, dirs, files in os.walk(folder_path)
                   for file in files if file.endswith(('.mp4', '.avi', '.mkv'))]
    return random.choice(video_files) if video_files else None

def select_video_folder():
    """Open file dialog to select a video folder."""
    global video_folder
    video_folder = filedialog.askdirectory(title="Select Video Folder")
    if not video_folder:
        print("No video folder selected.")

def select_audio_file():
    """Open file dialog to select an audio file."""
    global audio_path
    audio_path = filedialog.askopenfilename(title="Select Audio File", filetypes=[("Audio Files", "*.mp3 *.wav")])
    if not audio_path:
        print("No audio file selected.")

def start_playback(gui_root, interval_minutes, iconify):
    """Start playback of audio and video after the specified interval."""
    global stop_program

    while True:
        countdown = int(interval_minutes * 60)
        while countdown > 0 and not stop_program:
            time.sleep(1)
            countdown -= 1

        if stop_program:  # If stop_program is set, stop the countdown
            return

        # Play the alarm audio
        play_audio(audio_path)

        # After alarm, select a random video and play it
        video_path = get_random_video_path(video_folder)
        if video_path:
            play_video(video_path, gui_root, iconify)

def panic():
    """Stop the program and all actions."""
    global stop_program
    stop_program = True
    print("Panic button pressed! Stopping program and video playback.")
    messagebox.showinfo("Panic!", "The program has been stopped.")

def on_close(root):
    """Handle window close action to confirm exit."""
    result = messagebox.askyesno("Exit", "Are you sure you want to exit?")
    if result:
        panic()  # Stop everything if confirmed
        root.quit()  # Close the window
        root.destroy()  # Destroy the root window

def main():
    global video_folder, audio_path
    video_folder = None
    audio_path = None

    root = tk.Tk()
    root.title("Media Player Setup")

    # Video folder selection button
    select_video_button = tk.Button(root, text="Select Video Folder", command=select_video_folder)
    select_video_button.pack(pady=10)

    # Audio file selection button
    select_audio_button = tk.Button(root, text="Select Audio File", command=select_audio_file)
    select_audio_button.pack(pady=10)

    # Interval entry
    interval_label = tk.Label(root, text="Enter the interval in minutes:")
    interval_label.pack(pady=10)
    interval_entry = tk.Entry(root)
    interval_entry.pack(pady=10)

    # Option to minimize or withdraw the GUI
    iconify_var = tk.BooleanVar(value=True)
    iconify_check = tk.Checkbutton(root, text="Minimize GUI while playing", variable=iconify_var)
    iconify_check.pack(pady=10)

    # Panic button to stop the program
    panic_button = tk.Button(root, text="Panic! Stop Program", command=panic)
    panic_button.pack(pady=10)

    def start():
        global stop_program
        stop_program = False
        try:
            interval_minutes = float(interval_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid interval provided.")
            return
        if not video_folder or not audio_path:
            messagebox.showerror("Error", "Video folder or audio file not selected.")
            return
        threading.Thread(target=start_playback, args=(root, interval_minutes, iconify_var.get()), daemon=True).start()
        root.iconify()  # Minimize the GUI window after start

    start_button = tk.Button(root, text="Start", command=start)
    start_button.pack(pady=10)

    # Override the window close (X) button behavior
    root.protocol("WM_DELETE_WINDOW", lambda: on_close(root))

    root.mainloop()

if __name__ == "__main__":
    main()
