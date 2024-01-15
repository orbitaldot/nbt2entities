import nbtlib
import pyperclip
import argparse

CMD_BLOCK_LIMIT = 32500

def nbt_load(filename):
    nbt_data = nbtlib.load(filename)
    palette = nbt_data['palette']
    bbox = {
        'x': 1,
        'y': 1,
        'z': 1
    }
    data = []
    for block in nbt_data['blocks']:
        pos = block['pos']
        state = block['state'].real
        x,y,z = pos[0].real,pos[1].real,pos[2].real

        bbox['x'] = max(bbox['x'], x)
        bbox['y'] = max(bbox['y'], y)
        bbox['z'] = max(bbox['z'], z)
        block_id = palette[state]['Name']

        if block_id == 'minecraft:air':
            continue

        data.append({'block': block_id, 'x': x, 'y': y, 'z': z})

    return {
        'blocks': data,
        'bbox': bbox
    }


def float2mcfloat(i,prec=6):
    return (str(i)[0:prec] + 'f')


def make_command(data):
    xscale = 1/(data['bbox']['x'] + 1)
    yscale = 1/(data['bbox']['y'] + 1)
    zscale = 1/(data['bbox']['z'] + 1)
    scale = min(xscale,yscale,zscale)
    
    s = float2mcfloat(scale)
    O = float2mcfloat(0.0)
    I = float2mcfloat(1.0)
        
    passengers = []

    for block in data['blocks']:
        x = float2mcfloat(block['x'] * scale)
        y = float2mcfloat(block['y'] * scale)
        z = float2mcfloat(block['z'] * scale)

        transform = ''
        transform += f"{s},{O},{O},{x},"
        transform += f"{O},{s},{O},{y},"
        transform += f"{O},{O},{s},{z},"
        transform += f"{O},{O},{O},{I}"
   
        passengers.append(f"{{id:\"minecraft:block_display\",block_state:{{Name:\"{block['block']}\",Properties:{{}}}},transformation:[{transform}]}}")

    command = f'summon block_display ~ ~1 ~ {{CustomName:\"skyblock\",Passengers:[{','.join(passengers)}]}}'

    return command


def main():
    parser = argparse.ArgumentParser(
        prog='nbt2entities',
        description='',
        epilog=''
    )
    parser.add_argument('filename')
    parser.add_argument('-o', '--output_file')
    parser.add_argument('-c', '--clipboard', action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    data = nbt_load(args.filename)
    command = make_command(data)

    if args.verbose:
        command_length = len(command)
        print(command_length, '(command too long!)' if command_length > CMD_BLOCK_LIMIT else '')

    if args.clipboard:
        pyperclip.copy(command)

    if args.output_file:
        f = open(args.output_file, "w")
        f.write(command)
        f.close()


main()