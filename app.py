import re
import yt_dlp
import gradio as gr

def get_playlist_details(playlist_url):
    ydl_opts = {
        'quiet': True,
        'extract_flat': False,  # Changed to get full video details
        'force_generic_extractor': False  # Changed to use native extractors
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f'"{playlist_url}"', download=False)
            entries = info.get('entries', [])
            total_videos = len(entries)
            
            # Get individual durations for more accurate calculations
            video_durations = [entry.get('duration', 0) for entry in entries]
            total_duration = sum(video_durations)
            avg_video_length = total_duration / total_videos if total_videos > 0 else 0
            
            return total_videos, total_duration, avg_video_length, video_durations
        except Exception as e:
            return "Invalid Playlist URL"

def format_time(total_seconds):
    # Fixed parameter name to avoid overwriting variable
    days = int(total_seconds // 86400)
    hours = int((total_seconds % 86400) // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    return f"{days}d {hours}h {minutes}m {seconds}s"

def youtube_tracker(playlist_url, watched_videos, choice, daily_hours=1, desired_videos=0, speed=1.0):
    details = get_playlist_details(playlist_url)
    if details == "Invalid Playlist URL":
        return "Invalid Playlist URL"
    
    total_videos, total_duration, avg_video_length, video_durations = details
    
    # If desired_videos is not specified or is greater than total_videos, use total_videos
    if desired_videos <= 0 or desired_videos > total_videos:
        desired_videos = total_videos
    
    # Calculate time based on ACTUAL durations of videos to watch, not averages
    if watched_videos < len(video_durations) and desired_videos <= len(video_durations):
        # Get the actual durations of the specific videos to watch
        specific_videos_duration = sum(video_durations[watched_videos:desired_videos])
        time_needed = specific_videos_duration / speed
        videos_to_watch = desired_videos - watched_videos
    else:
        # Fallback to average if we can't get specific durations
        videos_to_watch = max(desired_videos - watched_videos, 0)
        time_needed = videos_to_watch * avg_video_length / speed
    
    if choice == "Total Remaining Hours":
        return f"Remaining Time: {format_time(time_needed)}"
    elif choice == "Days to Finish at X Hours/Day":
        if daily_hours > 0:
            days_needed = time_needed / (daily_hours * 3600)
            return f"Days Needed: {format_time(days_needed * 86400)}"
        return "Unlimited days needed"
    elif choice == "Hours Needed for Specific Videos":
        return f"Time Needed for {videos_to_watch} Videos: {format_time(time_needed)}"
    else:
        return "Invalid choice. Please select an option."


with gr.Blocks(theme=gr.themes.Glass()) as demo:
    # Custom Logo and Title
    gr.Markdown(
        """
        <div style="text-align: center;">
            <img src="https://via.placeholder.com/150x150.png?text=StreamSync" alt="StreamSync Logo" style="border-radius: 50%; width: 150px; height: 150px; margin-bottom: 20px;">
            <h1 style="color: #4CAF50;">🌊 StreamSync</h1>
            <p><i>Your ultimate YouTube playlist tracker and planner!</i></p>
        </div>
        """
    )

    # Feature Logos Section
    gr.Markdown(
        """
        <div style="text-align: center; margin-bottom: 30px;">
            <h3>📋 Features:</h3>
            <p>📈 <b>Playback Speed Adjustment</b></p>
            <p>⏳ <b>Calculates Remaining Hours or Days</b></p>
            <p>🕒 <b>Customizable Daily Watch Plans</b></p>
        </div>
        """
    )

    # Tabs for better organization
    with gr.Tabs():
        # Tab for Basic Options
        with gr.TabItem("Basic Options"):
            playlist_url_input = gr.Textbox(
                label="Playlist URL", 
                placeholder="Enter YouTube playlist URL",
                info="Example: https://youtube.com/playlist?list=PL12345"
            )
            watched_input = gr.Number(
                label="Watched Videos", 
                value=0, 
                interactive=True,
                info="Number of videos you've already watched."
            )
        
        # Tab for Advanced Settings
        with gr.TabItem("Advanced Settings"):
            desired_input = gr.Number(
                label="Desired Videos", 
                value=0, 
                interactive=True,
                info="Number of videos you want to complete."
            )
            daily_hours_input = gr.Slider(
                label="Daily Watch Hours", 
                minimum=1, 
                maximum=10, 
                step=1, 
                value=1,
                info="How many hours per day you plan to watch."
            )
            playback_speed_input = gr.Radio(
                [1.0, 1.25, 1.5, 1.75, 2.0],
                label="Playback Speed",
                value=1.0,
                interactive=True,
                info="Choose your preferred playback speed."
            )
    
    # Output Section
    output_textbox = gr.Textbox(label="Output", show_copy_button=True)

    # Calculate Button
    calculate_button = gr.Button("Calculate")
    
    # Link button click to function
    calculate_button.click(
        youtube_tracker,
        inputs=[
            playlist_url_input,
            watched_input,
            gr.Radio(["Total Remaining Hours", "Days to Finish at X Hours/Day", "Hours Needed for Specific Videos"], value="Total Remaining Hours"),
            daily_hours_input,
            desired_input,
            playback_speed_input,
        ],
        outputs=[output_textbox]
    )

demo.launch()