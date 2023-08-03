from RPI_Operant.hardware.box import Box

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
              start_now=True, simulated = False, verbose = True)
    phase = box.timing.new_phase('setup_phase', length = 3)
    box.reset()
    
    #simplifying hardware calls
    door_1 = box.doors.door_1
    door_2 = box.doors.door_2
    poke_1 = box.nose_pokes.nose_port_1
    poke_2 = box.nose_pokes.nose_port_2
    LED_1 = box.outputs.LED_1
    LED_2 = box.outputs.LED_2
    speaker = box.speakers.speaker
    delay = box.get_delay()
    FR = box.get_software_setting(location = 'values', setting_name='FR', default = 1)
    #start beam break monitoring. calculate durations
    box.beams.door1_ir.start_getting_beam_broken_durations() 
    box.beams.door2_ir.start_getting_beam_broken_durations()
    reward_phase_d2 = box.timing.new_phase('reward_phase',length = 0.05)
    reward_phase_d1 = box.timing.new_phase('reward_phase',length = 0.05)
    
    
    phase.wait()
    total_time = box.get_software_setting(location = 'values', setting_name = 'experiment_length', default = 30*60)
    
    #wait to finish setup
    
    box.timing.new_round()

    poke_1.begin_monitoring()
    poke_2.begin_monitoring()

    total_time_phase = box.timing.new_phase('experiment', length = total_time)
    
    poke_1.set_poke_target(FR)
    poke_2.set_poke_target(FR)
    poke_1.activate_LED()
    poke_2.activate_LED()
    while total_time_phase.active():
        
        if door_1.is_open():
            if not reward_phase_d1.active():
                door_1.close(wait = True)
                poke_2.set_poke_target(FR)
                poke_2.activate_LED()
        
        if door_2.is_open():
            if not reward_phase_d2.active():
                door_2.close(wait = True)
                poke_1.set_poke_target(FR)
                poke_1.activate_LED()
        
        if poke_1.pokes_reached:
            poke_1.deactivate_LED()
            speaker.play_tone(tone_name = 'door_2_open', wait = True)
            timeout = box.timing.new_timeout(length = delay)
            timeout.wait()
            door_2.open()
            reward_phase_d2 = box.timing.new_phase('reward_phase_d2',length = box.software_config['values']['reward_length'])
            poke_1.reset_poke_count()
            
        if poke_2.pokes_reached:
            poke_2.deactivate_LED()
            speaker.play_tone(tone_name = 'door_1_open', wait = True)
            timeout = box.timing.new_timeout(length = delay)
            timeout.wait()
            door_1.open()
            reward_phase_d1 = box.timing.new_phase('reward_phase_d1',length = box.software_config['values']['reward_length'])
            poke_2.reset_poke_count()
            
    box.shutdown()

if __name__ == '__main__':
    run()
    
