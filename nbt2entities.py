import nbtlib
import pyperclip
import argparse

CMD_BLOCK_LIMIT = 32500


def float2mcfloat(i,prec=3):
    return (str(i)[0:prec] + 'f')


def nbt2entities(filename,block_scale=1.0,offset_x=0.0,offset_y=0.0,offset_z=0.0,custom_name="",main_entity="block_display"):
    nbt_data = nbtlib.load(filename)
    bbox = { 'x': 1, 'y': 1, 'z': 1 }
    data = []
    
    for block in nbt_data['blocks']:
        state = block['state'].real
        block_id = nbt_data['palette'][state]['Name']
        if block_id == 'minecraft:air':
            continue

        x, y, z = block['pos'][0].real, block['pos'][1].real, block['pos'][2].real
        data.append({'block': block_id, 'x': x, 'y': y, 'z': z})

        bbox['x'] = max(bbox['x'], x)
        bbox['y'] = max(bbox['y'], y)
        bbox['z'] = max(bbox['z'], z)

    block_scale = float(block_scale)
    xscale = 1/(bbox['x'] + 1) * block_scale
    yscale = 1/(bbox['y'] + 1) * block_scale
    zscale = 1/(bbox['z'] + 1) * block_scale
    scale = min(xscale,yscale,zscale)
    
    s = float2mcfloat(scale)
    O = float2mcfloat(0.0)
    I = float2mcfloat(1.0)

    passengers = []
    for block in data:
        x = float2mcfloat(block['x'] * scale + float(offset_x))
        y = float2mcfloat(block['y'] * scale + float(offset_y))
        z = float2mcfloat(block['z'] * scale + float(offset_z))

        transform = ''
        transform += f"{s},{O},{O},{x},"
        transform += f"{O},{s},{O},{y},"
        transform += f"{O},{O},{s},{z},"
        transform += f"{O},{O},{O},{I}"

        props = {'name': ''}
        block_props = {} # TODO: implement block properties

        if custom_name != "":
            props['name'] = f'CustomName:"{custom_name}",'
            
        passengers.append(f"{{id:\"minecraft:block_display\",{props['name']}block_state:{{Name:\"{block['block']}\",Properties:{{}}}},transformation:[{transform}]}}")

    command = f'summon {main_entity} ~ ~1 ~ {{CustomName:\"{custom_name}\",Passengers:[{','.join(passengers)}]}}'

    return command


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='nbt2entities',
        description='',
        epilog=''
    )
    parser.add_argument('filename')
    parser.add_argument('-o', '--output_file')
    parser.add_argument('-s', '--scale')
    parser.add_argument('-ox', '--offset_x') # not implemented yet
    parser.add_argument('-oy', '--offset_y') # not implemented yet
    parser.add_argument('-oz', '--offset_z')  # not implemented yet
    parser.add_argument('-cn', '--custom_name') # makes command longer! use a short name
    parser.add_argument('-e', '--entity')
    parser.add_argument('-cb', '--clipboard', action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()
    
    params = {
        "filename": args.filename,
        "block_scale": args.scale,
        "offset_x": args.offset_x,
        "offset_y": args.offset_y,
        "offset_z": args.offset_z,
        "custom_name": args.custom_name,
        "main_entity": args.entity
    }
    not_none_params = {k:v for k, v in params.items() if v is not None}
    command = nbt2entities(**not_none_params)

    if args.verbose:
        command_length = len(command)
        print(command_length, '(command too long!)' if command_length > CMD_BLOCK_LIMIT else '')

    if args.clipboard:
        pyperclip.copy(command)

    if args.output_file:
        f = open(args.output_file, "w")
        f.write(command)
        f.close()
