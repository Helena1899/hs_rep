#!/usr/bin/env python3

import rospy
from std_msgs.msg import Float32
from std_msgs.msg import String
from std_msgs.msg import Bool # Assuming a boolean topic

import vlc  # need to install pip-vlc & sudo apt install vlc


btn_status = False
video_prompt = False
int_video_prompt = 0

video_timer_start = 0
video_timer_end = 0
video_reaction_time = None


def sub_hsr_btn_callback(data):
    global btn_status, video_timer_start, video_prompt, int_video_prompt
    btn_status = data.data
    if btn_status and video_prompt: # Check if the boolean message is True
        video_reaction_time = rospy.get_time()  - video_timer_start # Calculate the reaction time
        print("Video Reaction Time: ", video_reaction_time)
        pub_video_reaction_time.publish("HeadPrompt_" + str(int_video_prompt)+"_ReactionTime_"+str(video_reaction_time)) # Publish the reaction time
        video_filename = '/home/hsr-hmi/catkin_ws/src/tour_video_pkg/videos/elsa.mp4' # Path to the video file
        video_prompt = False

def sub_video_prompt_callback(data):
    global video_prompt, video_timer_start, int_video_prompt
    video_prompt = data.data
    video_timer_start = rospy.get_time()  # Record the start time
    pub_video_status.publish("TourVideo Prompt_"+str(int_video_prompt))
    int_video_prompt += 1
    pub_switch_led.publish(True)  # Turn off the LED

def play_video_fullscreen(video_path):
    # Use VLC to play video with audio in fullscreen
    instance = vlc.Instance('--fullscreen')
    player = instance.media_player_new()
    media = instance.media_new(video_path)
    player.set_fullscreen(True)
    player.set_media(media)
    player.play()

    pub_video_status.publish("TourVideo Played")
    pub_switch_led.publish(False)  # Turn on the LED

    # Wait until the video finishes
    while True:
        state = player.get_state()
        if state in [vlc.State.Ended, vlc.State.Error]:
            break
        rospy.sleep(0.1)

    player.stop()

    pub_video_status.publish("TourVideo Finished")

if __name__ == '__main__':
    rospy.init_node('prompt_video_cognitive_following_node', anonymous=True)
    # Subscriber Topics
    rospy.Subscriber('/hsrb/switch_input', Bool, sub_hsr_btn_callback) # Subscribe to your topic
    rospy.Subscriber('/robot_tour/video_prompt', Bool, sub_video_prompt_callback) # Subscribe to video play status

    # Publisher Topics
    pub_video_status = rospy.Publisher('/robot_tour/video_play_status', String, queue_size=10)
    pub_switch_led = rospy.Publisher('/hsrb/switch_led',Bool, queue_size=10)
    pub_video_reaction_time = rospy.Publisher('/robot_tour/video_reaction_time', String, queue_size=10)

    rospy.spin() # Keep the node running

