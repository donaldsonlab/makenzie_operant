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
USER_SOFTWARE_CONFIG_PATH = '/home/pi/dave_miniscope_debug/setup_files/door_choice_testing.yaml'


box = Box()

def run():
    
    box.setup(run_dict=RUNTIME_DICT, 
              user_hardware_config_file_path=USER_HARDWARE_CONFIG_PATH,
              user_software_config_file_path=USER_SOFTWARE_CONFIG_PATH,
              start_now=True, simulated = False)
    
    
    #simplifying hardware calls
    door_1 = box.doors.door_1
    door_2 = box.doors.door_2
    lever_1 = box.levers.lever_1
    lever_2 = box.levers.lever_2
    speaker = box.speakers.speaker1
    delay = box.get_delay()
    
    box.reset()
    FR = box.get_software_setting(location = 'values', setting_name='FR', default = 1)
    for i in range(1,box.software_config['values']['rounds']+1, 1):

        box.timing.new_round()
        
        phase = box.timing.new_phase('levers_out', box.software_config['values']['lever_out'])
        
        speaker.play_tone(tone_name = 'round_start', wait = True)
        press_latency_1 = box.levers.lever_1.extend()
        press_latency_2 = box.levers.lever_2.extend(wait = True)
        
        #start the actual lever-out phase
        lever_1.wait_for_n_presses(n=FR, latency_obj = press_latency_1)
        lever_2.wait_for_n_presses(n=FR, latency_obj = press_latency_2)
        
        while phase.active():
        
            if lever_1.presses_reached:
                lever_1.retract()
                lever_2.retract()
                speaker.play_tone(tone_name = 'door_2_open', wait = True)
                
                timeout = box.timing.new_timeout(length = delay)
                timeout.wait()
                
                phase.end_phase()
                reward_phase = box.timing.new_phase('reward_phase',length = box.software_config['values']['reward_time'])
                
                lat = door_2.open()
                box.beams.door2_ir.monitor_beam_break(latency_to_first_beambreak = lat, end_with_phase=reward_phase)
                
            elif lever_2.presses_reached:
                lever_1.retract()
                lever_2.retract()
                speaker.play_tone(tone_name = 'door_1_open', wait = True)
                
                timeout = box.timing.new_timeout(length = delay)
                timeout.wait()
                
                phase.end_phase()
                reward_phase = box.timing.new_phase('reward_phase',length = box.software_config['values']['reward_time'])
                
                lat = door_1.open()
                box.beams.door1_ir.monitor_beam_break(latency_to_first_beambreak = lat, end_with_phase=reward_phase)

        if not lever_1.presses_reached and not lever_2.presses_reached:
            lever_1.retract()
            lever_2.retract()
            
        #if presses were reached, wait for reward phase
        if box.timing.current_phase.name == 'reward_phase':
            box.timing.current_phase.wait()
            if door_1.is_open():
                door_1.close()
            elif door_2.is_open():
                door_2.close()

        phase = box.timing.new_phase(name='ITI', length =box.software_config['values']['ITI_length'])
        
        phase.wait()
        
    
    
    box.shutdown()

if __name__ == '__main__':
    run()
    







