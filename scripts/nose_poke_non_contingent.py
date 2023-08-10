from RPI_Operant.hardware.box import Box

from pathlib import Path
experiment_name = Path(__file__).stem
RUNTIME_DICT = {'vole':000, 'day':1, 'experiment':experiment_name, 'port_side':'same', 'active_door':'door_1'}
# # For Running on the Raspberry Pi: 
USER_HARDWARE_CONFIG_PATH = '/home/pi/local_rpi_files/default_hardware.yaml'
USER_SOFTWARE_CONFIG_PATH = '/home/pi/miniscope_dec_2022/setup_files/door_train.yaml'
 
box = Box()

def run():
    
    box.setup(run_dict=RUNTIME_DICT, 
              user_hardware_config_file_path=USER_HARDWARE_CONFIG_PATH,
              user_software_config_file_path=USER_SOFTWARE_CONFIG_PATH,
              start_now=True, simulated = False, verbose = False)
    phase = box.timing.new_phase('setup_phase', length = 3)
    box.reset()
    
    door_1 = box.doors.door_1
    door_2 = box.doors.door_2

    box.nose_pokes.nose_port_1.deactivate_LED()
    box.nose_pokes.nose_port_2.deactivate_LED()
    
    if RUNTIME_DICT['port_side'] == 'same':
    #simplifying hardware calls
        poke_d1 = box.nose_pokes.nose_port_1
        poke_d2 = box.nose_pokes.nose_port_2
        print('poke_2 == door_2\npoke_1==door_1')
    elif RUNTIME_DICT['port_side'] == 'opposite':
        poke_d1 = box.nose_pokes.nose_port_2
        poke_d2 = box.nose_pokes.nose_port_1
        print('poke_2 == door_1\npoke_1==door_2')
    else:
        print(f'port side wasnt parsed, but was given as {RUNTIME_DICT["port_side"]}')
    
    speaker = box.speakers.speaker
    delay = box.get_delay()
    FR = box.get_software_setting(location = 'values', setting_name='FR', default = 1)
    #start beam break monitoring. calculate durations
    box.beams.door1_ir.start_getting_beam_broken_durations() 
    box.beams.door2_ir.start_getting_beam_broken_durations()
    reward_phase = box.timing.new_phase('reward_phase',length = 0.05)

    
    
    phase.wait()
    total_time = box.get_software_setting(location = 'values', setting_name = 'experiment_length', default = 30*60)
    
    #wait to finish setup
    
    box.timing.new_round()

    poke_d1.begin_monitoring()
    poke_d2.begin_monitoring()

    total_time_phase = box.timing.new_phase('experiment', length = total_time)
    
    
    door_reward = False
    
    
    if RUNTIME_DICT['active_door'] == 'door_1':

        poke_active = poke_d1
        door_active = door_1

    elif RUNTIME_DICT['active_door'] == 'door_2':
        
        poke_active = poke_d2
        door_active = door_2

    else:
        print('neither door_1 nor door_2 defined as "active door", exiting')          
        box.shutdown()
        exit()

    poke_active.set_poke_target(FR)
    poke_active.activate_LED(percent_brightness = 50)
    non_contingent_timer =box.timing.new_phase('non_contingent_timer', length =  box.get_software_setting(location = 'values', setting_name='non_contingent_interval', 
                                                            default = 90))

    while total_time_phase.active():
        
        if door_reward:
            if not reward_phase.active():
                door_reward = False
                door_active.close(wait = True)
                poke_active.set_poke_target(FR)
                poke_active.activate_LED()
                non_contingent_timer.reset()
        

        if not non_contingent_timer.active() and not door_reward:
            poke_active.deactivate_LED()
            poke_active.reset_poke_count()
            speaker.play_tone(tone_name = f'{door_active.name}_open', wait = True)
            timeout = box.timing.new_timeout(length = delay)
            timeout.wait()
            door_active.open()
            door_reward = True
            reward_phase = box.timing.new_phase(f'reward_phase_{door_active.name}',length = box.software_config['values']['reward_length'])
            
            
            
        if poke_active.pokes_reached and not door_reward:
            poke_active.deactivate_LED()
            speaker.play_tone(tone_name = f'{door_active.name}_open', wait = True)
            timeout = box.timing.new_timeout(length = delay)
            timeout.wait()
            door_active.open()
            door_reward = True
            reward_phase = box.timing.new_phase(f'reward_phase_{door_active.name}',length = box.software_config['values']['reward_length'])
            poke_active.reset_poke_count()
            non_contingent_timer.reset()
            
    if door_reward:
        reward_phase.wait()
        door_active.close(wait = True)
        box.timing.new_timeout(length = 1)

    box.shutdown()

if __name__ == '__main__':
    run()
    
