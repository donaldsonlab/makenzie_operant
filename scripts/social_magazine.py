'''INCOMPLETE
UNTESTED'''


from pickle import FALSE
from RPI_Operant.hardware.box import Box
import time
import random
from pathlib import Path
experiment_name = Path(__file__).stem
RUNTIME_DICT = {'vole':000, 'day':1, 'experiment':experiment_name}
# # For Running on the Raspberry Pi: 
USER_HARDWARE_CONFIG_PATH = '/home/pi/local_rpi_files/default_hardware.yaml'
USER_SOFTWARE_CONFIG_PATH = '/home/pi/miniscope_dec_2022/setup_files/door_train.yaml'
 

box = Box()

def run():
    
    box.setup(run_dict=RUNTIME_DICT, 
              user_hardware_config_file_path=USER_HARDWARE_CONFIG_PATH,
              user_software_config_file_path=USER_SOFTWARE_CONFIG_PATH,
              start_now=False, simulated = False)
    phase = box.timing.new_phase('setup_phase', length = 5)

    #simplifying hardware calls
    door_1 = box.doors.door_1
    door_2 = box.doors.door_2
    lever_1 = box.levers.lever_1
    lever_2 = box.levers.lever_3
    speaker = box.speakers.speaker
    delay = box.get_delay()
    FR = box.get_software_setting(location = 'values', setting_name='FR', default = 1)

    box.reset()

    lever = lever_2
    next_lever = lever_1
    
    door = door_1
    next_door = door_2
    
    tone = 'door_1_open'
    next_tone = 'door_2_open'
    
    rep = 1
    phase.end_phase()
    for i in range(1,box.software_config['values']['reps']*box.software_config['values']['sets']*2+1, 1):
        
        if rep > box.software_config['values']['reps']:
            rep = 1
            d = door
            l = lever
            t = tone
            
            lever = next_lever
            door = next_door
            tone = next_tone
            
            next_lever = l
            next_door = d
            next_tone = t
            
            
            
        
        box.timing.new_round()

        
        lever_phase = box.timing.new_phase(lever.name + '_out', box.software_config['values']['lever_out'])
        speaker.play_tone(tone_name = 'round_start', wait = True)
        pause = box.timing.new_timeout(length = 0.25)
        pause.wait()
        press_latency = lever.extend()
        
        #start the actual lever-out phase
        lever.wait_for_n_presses(n = FR, latency_obj = press_latency)
        post_lever_timeout = box.timing.new_timeout(length = box.software_config['values']['lever_out_to_reward'])
        while lever_phase.active() and post_lever_timeout.active():
            '''waiting here for something to happen'''
        
            if lever.presses_reached:
                lat = lever.retract()
                if door.name == 'door_1':
                    box.beams.door1_ir.monitor_beam_break(latency_to_first_beambreak = lat, end_with_phase=reward_phase)
                else:
                    box.beams.door2_ir.monitor_beam_break(latency_to_first_beambreak = lat, end_with_phase=reward_phase)

                speaker.play_tone(tone_name = tone, wait = True)
                
                
                lever_phase.end_phase()
                reward_phase = box.timing.new_phase('reward_phase',length = box.software_config['values']['reward_length'])
                
                door.open()
                
                
        #only dispense if not already dispensed
        if not lever.presses_reached:
            
            speaker.play_tone(tone_name = tone, wait = True)
            
            lat = door.open()
            
            if door.name == 'door_1':
                box.beams.door1_ir.monitor_beam_break(latency_to_first_beambreak = lat, end_with_phase=reward_phase)
            else:
                box.beams.door2_ir.monitor_beam_break(latency_to_first_beambreak = lat, end_with_phase=reward_phase)
            
            reward_phase = box.timing.new_phase('reward_phase',length = box.software_config['values']['reward_length'])
            timeout = box.timing.new_timeout(length = box.software_config['values']['post_reward_retraction_delay'])
            timeout.wait()
            lever.retract()
            lever_phase.end_phase()
            
            
           
       
        
        reward_phase.wait()
        door.close()

        lever.reset_lever()
        
            
        phase = box.timing.new_phase(name='ITI', length = box.software_config['values']['ITI_length'])
        
        phase.wait()
        rep+=1
    
    
    box.shutdown()

if __name__ == '__main__':
    run()
    







