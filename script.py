#!/usr/bin/env python3
import os
import subprocess
from openai import OpenAI  # New API interface
import whisper
from dotenv import load_dotenv
import time

# ANSI escape sequences for colored output
BLUE = "\033[94m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"

def print_header():
    header = f"""
{BOLD}{CYAN}===================================================================
          ETEPS Reading Club Learning Assists Production Tool
==================================================================={RESET}
    """
    print(header)

def choose_video_file():
    """
    Prompts the user to enter a directory, then lists available video files.
    Returns the full path of the selected file or None.
    """
    directory = input(f"{BOLD}Enter the directory containing your video files (press Enter for current directory): {RESET}").strip()
    if not directory:
        directory = os.getcwd()
    if not os.path.isdir(directory):
        print(f"{RED}Directory does not exist.{RESET}")
        return None

    video_extensions = ('.mp4', '.mov', '.avi')
    try:
        video_files = [f for f in os.listdir(directory) if f.lower().endswith(video_extensions)]
    except PermissionError as e:
        print(f"{RED}Permission error: Cannot access {directory}. Please check your system permissions.{RESET}")
        return None

    if not video_files:
        print(f"{YELLOW}No video files found in that directory.{RESET}")
        return None

    print(f"\n{BOLD}Video files in {directory}:{RESET}")
    for idx, file in enumerate(video_files, 1):
        print(f"  {GREEN}{idx}.{RESET} {file}")

    choice = input(f"\nSelect a video file by number or type the file name: ").strip()
    if choice.isdigit():
        index = int(choice)
        if 1 <= index <= len(video_files):
            return os.path.join(directory, video_files[index - 1])
        else:
            print(f"{RED}Invalid selection number.{RESET}")
            return None
    else:
        candidate = os.path.join(directory, choice)
        if os.path.exists(candidate):
            return candidate
        else:
            print(f"{RED}File not found.{RESET}")
            return None

def extract_audio(video_file, audio_file):
    """
    Extracts audio from the given video file using ffmpeg and saves it as a WAV file.
    """
    command = [
        "ffmpeg",
        "-y",  # Overwrite output file if it exists
        "-i", video_file,
        "-vn",  # No video
        "-acodec", "pcm_s16le",
        "-ar", "44100",  # Sampling rate
        "-ac", "2",  # Stereo
        audio_file
    ]
    subprocess.run(command, check=True)
    print(f"{GREEN}Audio extracted to {audio_file}{RESET}")

def transcribe_audio(audio_file, transcription_file):
    """
    Uses OpenAI's Whisper to transcribe the audio file.
    Uses the built-in progress bar (with verbose=False) and stores the transcription.
    """
    print(f"{BLUE}Loading Whisper model...{RESET}")
    model = whisper.load_model("base")  # Change the model if needed.
    print(f"{BLUE}Transcribing audio...{RESET}")
    result = model.transcribe(audio_file, verbose=False)
    transcription = result["text"]
    print(f"{GREEN}Transcription complete.{RESET}")
    with open(transcription_file, "w", encoding="utf-8") as f:
        f.write(transcription)
    print(f"{GREEN}Transcription saved to {transcription_file}{RESET}")
    return transcription

def generate_summary(transcription):
    """
    Uses the new OpenAI API interface to generate a summary from the transcription.
    """
    prompt = (
        "Please generate a concise and informative summary for the following reading club transcription:\n\n"
        f"{transcription}\n\nSummary:"
    )
    print(f"{BLUE}Generating summary with OpenAI API...{RESET}")
    client = OpenAI()
    completion = client.chat.completions.create(
      model="gpt-4o",
      messages=[
        {"role": "developer", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
      ]
    )
    summary = completion.choices[0].message.content.strip()
    print(f"{GREEN}Summary generated.{RESET}")
    return summary

def generate_flashcards(summary, transcription):
    """
    Uses the new OpenAI API interface to generate flashcards in CSV format.
    """
    prompt = (
        "Using the following summary and transcription from a reading club session, create a set of flashcards. "
        "Format the output as a CSV file with two columns: 'Front' and 'Back'. Only output the CSV content without any additional text.\n\n"
        f"Summary:\n{summary}\n\n"
        f"Transcription:\n{transcription}\n\n"
        "CSV:"
    )
    print(f"{BLUE}Generating flashcards with OpenAI API...{RESET}")
    client = OpenAI()
    completion = client.chat.completions.create(
      model="gpt-4o",
      messages=[
        {"role": "developer", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
      ]
    )
    flashcards_csv = completion.choices[0].message.content.strip()
    print(f"{GREEN}Flashcards generated.{RESET}")
    return flashcards_csv

def interactive_menu():
    print_header()

    print("Select the operation you would like to perform:")
    print("  1. Full workflow (extract audio, transcribe, generate summary, and flashcards)")
    print("  2. Extract audio only")
    print("  3. Transcribe audio only (and save transcription)")
    print("  4. Generate summary (from existing transcription file)")
    print("  5. Generate flashcards (requires transcription; summary will be generated if missing)")
    print("  6. Generate summary and flashcards (from existing transcription file)")
    print("  7. Quit")

    choice = input(f"\nEnter your choice (1-7): ").strip()

    # Prompt the user for the output folder name (create if it doesn't exist)
    output_folder = input(f"{BOLD}Enter the output folder for generated artefacts (default: outputs): {RESET}").strip()
    if not output_folder:
        output_folder = "outputs"
    os.makedirs(output_folder, exist_ok=True)

    # Build file paths using the output_folder
    transcription_file = os.path.join(output_folder, "transcription.txt")
    summary_file = os.path.join(output_folder, "summary.txt")
    flashcards_file = os.path.join(output_folder, "flashcards.csv")
    audio_file = os.path.join(output_folder, "audio.wav")

    if choice == "1":
        video_file = choose_video_file()
        if not video_file:
            return
        extract_audio(video_file, audio_file)
        transcription = transcribe_audio(audio_file, transcription_file)
        summary = generate_summary(transcription)
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(summary)
        flashcards_csv = generate_flashcards(summary, transcription)
        with open(flashcards_file, "w", encoding="utf-8") as f:
            f.write(flashcards_csv)
        print(f"{GREEN}Full workflow complete!{RESET}")
        print(f"{GREEN}Audio saved to {audio_file}{RESET}")
        print(f"{GREEN}Transcription saved to {transcription_file}{RESET}")
        print(f"{GREEN}Summary saved to {summary_file}{RESET}")
        print(f"{GREEN}Flashcards saved to {flashcards_file}{RESET}")

    elif choice == "2":
        video_file = choose_video_file()
        if not video_file:
            return
        extract_audio(video_file, audio_file)
        print(f"{GREEN}Audio extraction complete. File saved to {audio_file}{RESET}")

    elif choice == "3":
        video_file = choose_video_file()
        if not video_file:
            return
        extract_audio(video_file, audio_file)
        transcription = transcribe_audio(audio_file, transcription_file)
        print(f"{GREEN}Transcription complete. File saved to {transcription_file}{RESET}")

    elif choice == "4":
        if not os.path.exists(transcription_file):
            print(f"{RED}Transcription file not found. Please run transcription first.{RESET}")
            return
        with open(transcription_file, "r", encoding="utf-8") as f:
            transcription = f.read()
        summary = generate_summary(transcription)
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(summary)
        print(f"{GREEN}Summary generated and saved to {summary_file}{RESET}")

    elif choice == "5":
        if not os.path.exists(transcription_file):
            print(f"{RED}Transcription file not found. Please run transcription first.{RESET}")
            return
        with open(transcription_file, "r", encoding="utf-8") as f:
            transcription = f.read()
        if os.path.exists(summary_file):
            with open(summary_file, "r", encoding="utf-8") as f:
                summary = f.read()
        else:
            summary = generate_summary(transcription)
            with open(summary_file, "w", encoding="utf-8") as f:
                f.write(summary)
        flashcards_csv = generate_flashcards(summary, transcription)
        with open(flashcards_file, "w", encoding="utf-8") as f:
            f.write(flashcards_csv)
        print(f"{GREEN}Flashcards generated and saved to {flashcards_file}{RESET}")

    elif choice == "6":
        if not os.path.exists(transcription_file):
            print(f"{RED}Transcription file not found. Please run transcription first.{RESET}")
            return
        with open(transcription_file, "r", encoding="utf-8") as f:
            transcription = f.read()
        summary = generate_summary(transcription)
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(summary)
        flashcards_csv = generate_flashcards(summary, transcription)
        with open(flashcards_file, "w", encoding="utf-8") as f:
            f.write(flashcards_csv)
        print(f"{GREEN}Summary and flashcards generated and saved to {summary_file} and {flashcards_file}{RESET}")

    elif choice == "7":
        print(f"{GREEN}Goodbye!{RESET}")
        return
    else:
        print(f"{RED}Invalid choice. Exiting.{RESET}")

if __name__ == "__main__":
    load_dotenv()  # Loads any other env variables (like OPENAI_API_KEY)
    if not os.getenv("OPENAI_API_KEY"):
        raise EnvironmentError("Please set your OPENAI_API_KEY in the environment variables.")
    interactive_menu()