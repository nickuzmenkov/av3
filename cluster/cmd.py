from aviator import Aviator

''' start code here
================================================================= '''

dim = int(input('dim: '))
mod = input('mod: ')
folder = input('dir: ')

rs = {
    '1': {20: '10', 40: '20'},
    '2': {60: '30', 80: '40'},
    '3': {100: '50', 120: '60'}
}

rs = rs[input('Reynolds Group: ')]

start_case = f'{dim}S-00-000'
hs = ['10', '20', '30', '40', '50', '60', '70']
ps = ['025', '050', '100', '150']

partition = input('Partition (cascadelake): ')
nodes = input('Nodes (1): ')
hours = input('Hours (24): ')

partition = partition if partition != '' else 'cascadelake'
nodes = int(nodes) if nodes != '' else 1
hours = int(hours) if hours != '' else 24

''' end code here
================================================================= '''

''' do not change anything
================================================================= '''

root = 'c:/users/frenc/yandexdisk/cfd/'
helper = Aviator(root + folder, start_case)

for h in hs:
    for p in ps:
        for vel, re in rs.items():
            msh = f'{dim}{mod}-{h}-{p}'
            job = f'{dim}{mod}-{h}-{p}-{re}'
            helper.job(job, msh, vel)

helper.execute(partition=partition, nodes=nodes, 
               dim=dim, hours=hours)

''' do not change anything
================================================================= '''
