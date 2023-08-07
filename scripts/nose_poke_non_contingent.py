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
    if RUNTIME_DICT['port_side'] == 'same':
    #simplifying hardware calls

        poke_d1 = box.nose_pokes.nose_port_1
        poke_d2 = box.nose_pokes.nose_port_2
    if RUNTIME_DICT['port_side'] == 'opposite':
        poke_d1 = box.nose_pokes.nose_port_2
        poke_d2 = box.nose_pokes.nose_port_1
    
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

    poke_d1.begin_monitoring()
    poke_d2.begin_monitoring()

    total_time_phase = box.timing.new_phase('experiment', length = total_time)
    
    
    door_1_reward = False
    door_2_reward = False
    
    
    if RUNTIME_DICT['active_door'] == 'door_1':
        poke_d1.set_poke_target(FR)
        poke_d1.activate_LED(percent_brightness = 50)
        non_contingent_timer =box.timing.new_phase('non_contingent_timer', length =  box.get_software_setting(location = 'values', setting_name='non_contingent_interval', 
                                                             default = 90))

        while total_time_phase.active():
            
            if door_1_reward:
                if not reward_phase_d1.active():
                    door_1_reward = False
                    door_1.close(wait = True)
                    poke_d1.set_poke_target(FR)
                    poke_d1.activate_LED()
                    non_contingent_timer.reset()
            

            if not non_contingent_timer.active() and not door_1_reward:
                poke_d1.deactivate_LED()
                poke_d1.reset_poke_count()
                speaker.play_tone(tone_name = 'door_2_open', wait = True)
                timeout = box.timing.new_timeout(length = delay)
                timeout.wait()
                door_1.open()
                door_1_reward = True
                reward_phase_d1 = box.timing.new_phase('reward_phase_d1',length = box.software_config['values']['reward_length'])
                
                
                
            if poke_d1.pokes_reached and not door_1_reward:
                poke_d1.deactivate_LED()
                speaker.play_tone(tone_name = 'door_1_open', wait = True)
                timeout = box.timing.new_timeout(length = delay)
                timeout.wait()
                door_1.open()
                door_1_reward = True
                reward_phase_d1 = box.timing.new_phase('reward_phase_d1',length = box.software_config['values']['reward_length'])
                poke_d1.reset_poke_count()
                non_contingent_timer.reset()
                

            
    elif RUNTIME_DICT['active_door'] == 'door_2':
        poke_d2.set_poke_target(FR)
        poke_d2.activate_LED()
        non_contingent_timer =box.timing.new_phase('non_contingent_timer', length =  box.get_software_setting(location = 'values', setting_name='non_contingent_interval', 
                                                             default = 90))
        while total_time_phase.active():
            
            if door_2_reward:
                if not reward_phase_d2.active():
                    door_2_reward = False
                    door_2.close(wait = True)
                    poke_d2.set_poke_target(FR)
                    poke_d2.activate_LED()
                    non_contingent_timer.reset()
                    
            if not non_contingent_timer.active() and not door_2_reward:
                poke_d2.deactivate_LED()
                poke_d2.reset_poke_count()
                speaker.play_tone(tone_name = 'door_2_open', wait = True)
                timeout = box.timing.new_timeout(length = delay)
                timeout.wait()
                door_2.open()
                door_2_reward = True
                reward_phase_d2 = box.timing.new_phase('reward_phase_d2',length = box.software_config['values']['reward_length'])
                
            if poke_d2.pokes_reached and not door_2_reward:
                non_contingent_timer.reset()
                poke_d2.deactivate_LED()
                speaker.play_tone(tone_name = 'door_2_open', wait = True)
                timeout = box.timing.new_timeout(length = delay)
                timeout.wait()
                door_2.open()
                door_2_reward = True
                reward_phase_d2 = box.timing.new_phase('reward_phase_d2',length = box.software_config['values']['reward_length'])
                poke_d2.reset_poke_count()
    else:
        print('neither door_1 nor door_2 defined as "active door", exiting')          
    box.shutdown()

if __name__ == '__main__':
    run()
    
