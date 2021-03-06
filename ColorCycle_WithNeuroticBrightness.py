def main():
    import random as random
    random.seed()
    from time import sleep
    from phue import Bridge

    # user-specific settings
    lights_in_play = [
#                      'Front Porch', 
                      'Entryway', 'Foyer',
                      'Kitchen 1', 'Kitchen 2',
                      'TV', 'Ledge 1', 'Ledge 2', 'Ledge 3', 'Ledge 4',
                      'Office', 'Office Lamp 1A', 'Office Lamp 1B', 'Office Ledge',
                      'Bedroom 1', 'Bedroom 2', 'Bedroom Lamp 1A', 'Bedroom Lamp 1B', 'Bedroom Headboard', 'Bathroom Mirror',
                      'Tina Ledge'
# Hue bulbs
# LivingColors
# LightStrips
#                      'Front Porch', 'Entryway', 'Foyer', 'Office Lamp 1A', 'Office Lamp 1B', 'Bedroom Lamp 1A', 'Bedroom Lamp 1B',
#                      'TV', 'Ledge 1', 'Ledge 2', 'Ledge 3', 'Ledge 4', 'Office', 'Bedroom 1', 'Bedroom 2',
#                      'Bedroom Headboard', 'Tina Ledge', 'Bathroom Mirror', 'Office Ledge', 'Kitchen 1', 'Kitchen 2'
                      ]

    # command-line argument parser
    import argparse
    parser = argparse.ArgumentParser(
            prog = 'ColorCycle',
            prefix_chars = '-/',
            description = """This program takes a series of color and brightness inputs and changes bulb charateristics accordingly.
                             It assumes that lights that are on will be used. Lights are tested for 'on' status every transition.""")
    timinggroup = parser.add_mutually_exclusive_group()
    timinggroup.add_argument('-t', '--timing', help='Set tempo in seconds, decimal values allowed; positive values produce gradual changes, ' + 
                                               'negative values produce flash transitions', type=float)
    timinggroup.add_argument('-r', '--bpm', '--rate', help='Set tempo as beats per minute, decimal values allowed; positive values produce gradual changes, ' + 
                                            'negative values produce flash transitions', type=float)
    parser.add_argument('-w', '--wait', help='Set wait time separately from transition time (bpm or seconds)', type=float, default = 0.0)
    parser.add_argument('-c', '--hues', '--colors', help='A list of color values the lights will cycle through (0 - 65535)', type=int, nargs='+', default = [-1])
    parser.add_argument('-b', '--brightness', help='Set bulb brightness (0 - 254)', type=int, default=254)
    parser.add_argument('-bH', '--brightnessHue', help='Set Hue bulb brightness (0 - 254)', type=int, metavar='briHue')
    parser.add_argument('-bLC', '--brightnessLivingColors', help='Set LivingColors bulb brightness (0 - 254)', type=int, metavar='briLC')
    parser.add_argument('-bLS', '--brightnessLightStrips', help='Set LightStrips brightness (0 - 254)', type=int, metavar='briLS')
    parser.add_argument('-s', '--saturation', help='Set bulb color saturation (0 - 254)', type=int, default=254)
    parser.add_argument('-m', '--monochrome', help='Cycle through color list with all lights the same color', action="store_true", default=False)
    parser.add_argument('-o', '--ordered', help='Cycle through color list in order (do not randomize); apparent ' +
                                                'color "chase" order will be in reverse bulb order', action="store_true", default=False)
    parser.add_argument('-i', '--ids', help='A list of bulb id values to cycle through; bulbs will be turned on', type=int, nargs='+')
    parser.add_argument('-v', '--verbose', help='Increase output verbosity', action="store_true")
    # TODO: add option to specify bulb names
    # TODO: add option to specify lights by name wildcard, e.g. 'Office*' or 'Office' implying '*Office*' or '*office*'
    # TODO: add option to print list of bulb name/ID combos (with additional option to sort by ID# or name? -d, -di, -dn for 'directory, by id, by name'?)
    # TODO: add option to work on all but specified ids (e.g. "everything but front porch"); -x --exclude
    # TODO: add option to print list of 'legal' named colors (green, red, energize)
    # TODO: add option to specify colors as names
    # TODO: consider using the data from this page to write color names corresponding to hues: http://en.wikipedia.org/wiki/List_of_colors_(compact)
    # TODO: add option to specify bridge IP
    # TODO: design a GUI with checkboxes, etc. for options
    # TODO: add option to specify colors (and more?) as ranges, e.g. hues = [0-1000, 5000-6800, 40000-41000] would assign three colors chosen from those ranges
    
    args = parser.parse_args()
    if args.verbose:
        print('Verbosity set to ON')
        if args.timing is not None:
            if args.timing >= 0:
                print('Transition timing is set to ' + str(abs(args.timing)) + ' seconds with a wait time of ' + str(abs(args.wait)) + ' seconds')
            if args.timing < 0 and args.wait > 0.0:
                print('Transition timing is set to 0.0 seconds with a wait time of ' + str(abs(args.wait) + abs(args.timing)) + ' seconds')
            if args.timing == 0:
                print('Lights will be set once and program will exit')
            if args.timing >= 0:
                print('Transitions will be gradual')
            else:
                print('Transitions will be instant')
        if args.bpm is not None:
            # For bpm time specification, assume that sum(bpm, wait) = intended total bpm.
            # So for bpm=10 and wait=20, transitions should begin at a rate of 30 bpm (every 2.0 seconds)
            netbpm = abs(args.bpm) + abs(args.wait)
            print('Timing is set to ' + str(netbpm) + ' bpm with a transition/wait split of ' + 
                  str(round(abs(args.bpm) / netbpm, 0)) + '/' + str(round(abs(args.wait) / netbpm, 0)) + '%')
            if args.bpm == 0:
                print('Lights will be set once and program will exit')
            if args.bpm >= 0:
                print('Transitions will be gradual')
            else:
                print('Transitions will be instant')

        print('Hues that will be cycled through: ' + str(args.hues))
        if args.ids is not None:
            print('Bulbs that will be cycled through: ' + str(args.ids))
        if args.ordered:
            print('Colors and lamps will be cycled in the specified order')
        else:
            print('Colors and lamps will be cycled in random order')
        print('Color saturation set to ' + str(args.saturation))
        print('Brightness set to ' + str(args.brightness))
        if args.brightnessLivingColors is not None:
            print('Brightness for LivingColors lamps set to ' + str(args.brightnessLivingColors))
        if args.brightnessHue is not None:
            print('Brightness for Hue bulbs set to ' + str(args.brightnessHue))

    # assign brightness levels
    if args.brightnessHue is not None:
        bri_hue = args.brightnessHue # 0 to 254
    else:
        bri_hue = args.brightness
    if args.brightnessLivingColors is not None:
        bri_lc = args.brightnessLivingColors # 0 to 254
    else:
        bri_lc = args.brightness
    if args.brightnessLightStrips is not None:
        bri_ls = args.brightnessLightStrips # 0 to 254
    else:
        bri_ls = args.brightness

    # Convert timing/frequency to integer tenths of seconds (transitiontime).
    # Wait times are handled by sleep(), so wait time is in actual seconds.
    if args.timing is not None:
        # Frequency is in seconds
        if args.timing >= 0: 
            transitiontime = int(round(args.timing * 10, 0))
            waittime = args.wait
        else: # use negative timing to specify flash transitions
            transitiontime = 0
            waittime = -args.timing + args.wait
            # This arrangement allows a benign but nonsensical combination 
            # (e.g. flash transition of -10 seconds with a wait of 5 seconds).
            # If a negative timing and a wait time are specified, 
            # the timing and wait times will be added together.
            # This way, flipping a negative sign does not change the 
            # observed rate of changes.
    if args.bpm is not None:
        # Frequency is in bpm; netbpm is the sum of transition and wait values
        if args.bpm >= 0:
            transitiontime = int(round(60 / (args.bpm / netbpm) * 10, 0))
            waittime = 60 / (args.wait / netbpm)
        else: # use negative bpm to specify flash transitions
            transitiontime = 0
            waittime = 60 / netbpm
    if args.timing is None and args.bpm is None:
        transitiontime = 0
        waittime = 0
        

    # assign light ID numbers to Hue and LivingColors lists (mainly due to brightness differences)
    b = Bridge()
    lights = b.get_light_objects('name')
    light_ids_hue = []
    light_ids_lc = []
    light_ids_ls = []
    light_ids_in_play = []
    for name in lights_in_play:
        light_ids_in_play.append(int(b.get_light_id_by_name(name)))
        if b.get_light(int(b.get_light_id_by_name(name)))['modelid'] == 'LCT001': # Hue
             light_ids_hue.append(int(b.get_light_id_by_name(name)))
        elif b.get_light(int(b.get_light_id_by_name(name)))['modelid'] == 'LLC001': # LivingColors
             light_ids_lc.append(int(b.get_light_id_by_name(name)))
        elif b.get_light(int(b.get_light_id_by_name(name)))['modelid'] == 'LST001': # LightStrips
             light_ids_ls.append(int(b.get_light_id_by_name(name)))
        else:
            print('else error')

    if args.ids is not None:
        # Filter lights in use so that only specified bulbs are used.
        # Turn specified bulbs on.
        light_ids_in_play = [id for id in light_ids_in_play if id in args.ids]
        light_ids_hue = [id for id in light_ids_hue if id in args.ids]
        light_ids_lc = [id for id in light_ids_lc if id in args.ids]
        light_ids_ls = [id for id in light_ids_ls if id in args.ids]
        b.set_light(light_ids_in_play, 'on', True)

    # randomly assign colors to lights and issue the commands via the hub
    if args.monochrome:
        # Set all bulbs to the same color; cycle through colors
        light_ids_on = []
        huenum = -1
        while True:
            if args.ordered:
                huenum += 1
                huenum = huenum % len(args.hues) 
                hue = args.hues[huenum]
            else:
                hue = random.choice(args.hues)

            hue_verbose = hue # used only for verbose printing
            if hue == -1: # flag for white
                saturation = 0 # 0 to 254
                hue = random.choice([i for i in args.hues if i >= 0]) # choose from non-white values
            else:
                saturation = args.saturation # 0 to 254

            if hue == -2: # flag for black (off)
                # get light 'on' status and build a list of lights that are on; build fresh every time
                for id in light_ids_in_play:
                    if b.get_light(id, 'on'):
                        light_ids_on.append(id)
                command =  {'transitiontime' : transitiontime, 'on' : False}
                result = b.set_light(light_ids_in_play, command)
            else:
                # Set Hue bulbs
                light_ids_on_hue = [id for id in light_ids_hue if id in light_ids_on]
                if len(light_ids_on_hue) > 0:
                    # If any bulbs are in the list, turn them on
                    command_hue =  {'on' : True, 'transitiontime' : transitiontime, 'hue' : hue, 'sat' : saturation, 'bri' : bri_hue}
                    result = b.set_light(light_ids_on_hue, command_hue)
                else: # empty list
                    command_hue =  {'transitiontime' : transitiontime, 'hue' : hue, 'sat' : saturation, 'bri' : bri_hue}
                    result = b.set_light(light_ids_hue, command_hue)
                # Set LivingColors lamps
                light_ids_on_lc = [id for id in light_ids_lc if id in light_ids_on]
                if len(light_ids_on_lc) > 0:
                    # If any bulbs are in the list, turn them on
                    command_lc =  {'on' : True, 'transitiontime' : transitiontime, 'hue' : hue, 'sat' : saturation, 'bri' : bri_lc}
                    result = b.set_light(light_ids_on_lc, command_lc)
                else: # empty list
                    command_lc =  {'transitiontime' : transitiontime, 'hue' : hue, 'sat' : saturation, 'bri' : bri_lc}
                    result = b.set_light(light_ids_lc, command_lc)
                # Set LightStrips
                light_ids_on_ls = [id for id in light_ids_ls if id in light_ids_on]
                if len(light_ids_on_ls) > 0:
                    # If any bulbs are in the list, turn them on
                    command_ls =  {'on' : True, 'transitiontime' : transitiontime, 'hue' : hue, 'sat' : saturation, 'bri' : bri_ls}
                    result = b.set_light(light_ids_on_ls, command_ls)
                else: # empty list
                    command_ls =  {'transitiontime' : transitiontime, 'hue' : hue, 'sat' : saturation, 'bri' : bri_ls}
                    result = b.set_light(light_ids_ls, command_ls)

            if args.verbose:
                if len(light_ids_hue) > 0:
#                    print('Hue Bulb(s) ' + str(light_ids_hue) + ' set to hue = ' + str(hue) + ', sat = ' + str(saturation) + ', bri = ' + str(bri_hue))
                    print('Hue Bulb(s) {light_id} set to hue = {hue:>5}, sat = {sat:>3}, bri = {bri_lc:>3}'.format(light_id=light_ids_hue, hue=hue_verbose, sat=saturation, bri_lc=bri_hue))
                if len(light_ids_lc) > 0:
#                    print('LC  Bulb(s) ' + str(light_ids_lc) + ' set to hue = ' + str(hue) + ', sat = ' + str(saturation) + ', bri = ' + str(bri_lc))
                    print('LC Bulb(s) {light_id} set to hue = {hue:>5}, sat = {sat:>3}, bri = {bri_lc:>3}'.format(light_id=light_ids_lc, hue=hue_verbose, sat=saturation, bri_lc=bri_lc))
                if len(light_ids_ls) > 0:
#                    print('LightStrip(s) ' + str(light_ids_ls) + ' set to hue = ' + str(hue) + ', sat = ' + str(saturation) + ', bri = ' + str(bri_ls))
                    print('LightStrip(s) {light_id} set to hue = {hue:>5}, sat = {sat:>3}, bri = {bri_ls:>3}'.format(light_id=light_ids_ls, hue=hue_verbose, sat=saturation, bri_ls=bri_ls))
                print('-- pass complete, waiting ' + str(transitiontime / 10 + waittime) + ' seconds --')
            if transitiontime + waittime == 0.0:
                if args.verbose:
                    print('-- lights set, bpm = 0.0, exiting program --')
                break # end program
            else:
                sleep(transitiontime / 10 + waittime)

            if len(args.hues) == 1:
                if args.verbose:
                    print('-- only one color to cycle, exiting program --')
                # only one color, no reason to keep changing it
                break
    else:
        # Set bulbs to random colors; wait; repeat
        light_ids_on = []
        huenum = -1
        while True:
            saturation = args.saturation # 0 to 254
            if not args.ordered:
                random.shuffle(light_ids_in_play)
            else:
                huenum += 1
                huenum = huenum % len(args.hues)
            for light_index, light_id in enumerate(light_ids_in_play):
                if args.ordered:
                    # Each bulb is assigned hues in the user-specified order.
                    # The intial hue is set by cycling through the color list in order.
                    # Visual note: the apparent "chase" direction of colors is the reverse 
                    # of the order of lights. 
                    hue = args.hues[(light_index + huenum) % len(args.hues)]
                else:
                    hue = random.choice(args.hues)
                hue_verbose = hue # used only for verbose printing
                if hue == -1: # flag for white
                    saturation = 0 # 0 to 254
                    if len([i for i in args.hues if i >= 0]) > 0:
                        hue = random.choice([i for i in args.hues if i >= 0]) # choose from non-white/black values
                    else:
                        hue = 0 # no colors available to choose, assume red
                elif hue == -2: # flag for black
                    light_ids_on.append(light_id)
                    hue = random.choice([i for i in args.hues if i >= 0]) # choose from non-white/black values
                    command =  {'on' : False, 'transitiontime' : transitiontime}

                if hue_verbose != -2: # if not black
                    if light_id in light_ids_hue:
                        # Set Hue bulbs
                        if light_id in light_ids_on:
                            command =  {'on' : True, 'transitiontime' : transitiontime, 'hue' : hue, 'sat' : saturation, 'bri' : bri_hue}
                            light_ids_on.remove(light_id)
                        else:
                            command =  {'transitiontime' : transitiontime, 'hue' : hue, 'sat' : saturation, 'bri' : bri_hue}
                    elif light_id in light_ids_lc:
                        # Set LivingColors lamps
                        if light_id in light_ids_on:
                            command =  {'on' : True, 'transitiontime' : transitiontime, 'hue' : hue, 'sat' : saturation, 'bri' : bri_lc}
                            light_ids_on.remove(light_id)
                        else:
                            command =  {'transitiontime' : transitiontime, 'hue' : hue, 'sat' : saturation, 'bri' : bri_lc}
                    elif light_id in light_ids_ls:
                        # Set LightStrips
                        if light_id in light_ids_on:
                            command =  {'on' : True, 'transitiontime' : transitiontime, 'hue' : hue, 'sat' : saturation, 'bri' : bri_ls}
                            light_ids_on.remove(light_id)
                        else:
                            command =  {'transitiontime' : transitiontime, 'hue' : hue, 'sat' : saturation, 'bri' : bri_ls}
                    else:
                        print('else error')
                result = b.set_light(light_id, command)

                if args.verbose:
                    if light_id in light_ids_hue:
                        print('Bulb {light_id:>2} set to hue = {hue:>5}, sat = {sat:>3}, bri = {bri_hue:>3}'.format(light_id=light_id, hue=hue_verbose, sat=saturation, bri_hue=bri_hue))
                    elif light_id in light_ids_lc:
                        print('Bulb {light_id:>2} set to hue = {hue:>5}, sat = {sat:>3}, bri = {bri_lc:>3}'.format(light_id=light_id, hue=hue_verbose, sat=saturation, bri_lc=bri_lc))
                    elif light_id in light_ids_ls:
                        print('Bulb {light_id:>2} set to hue = {hue:>5}, sat = {sat:>3}, bri = {bri_ls:>3}'.format(light_id=light_id, hue=hue_verbose, sat=saturation, bri_ls=bri_ls))

                saturation = args.saturation # 0 to 254

            if args.verbose:
                print('-- pass complete, waiting ' + str(transitiontime / 10 + waittime) + ' seconds --')
            if transitiontime + waittime == 0.0:
                if args.verbose:
                    print('-- lights set, bpm = 0.0, exiting program --')
                break # end program
            else:
                sleep(transitiontime / 10 + waittime)

    # debug
#    import pdb
#    pdb.set_trace()
    # debug


if __name__ == '__main__':
    main()
