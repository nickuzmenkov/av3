import pandas as pd
import numpy as np




''' constants '''
RAD = .005
LEN = .3
AREA = 2 * np.pi * RAD * LEN

RHO = 1.225
LAM = .0242
PR = .744
TWALL = 1000 

''' directory '''
root = 'C:\\Users\\frenc\\YandexDisk\\cfd\\out\\'

''' functions '''


def Reynolds(velocity, viscosity):
    return velocity * RHO * 2 * RAD / viscosity


def Nusselt(heat, temperature):
    return heat / AREA / (TWALL - temperature) * 2 * RAD / LAM


def Nusselt0_Petukhov(reynolds, cf):
    return cf * reynolds * PR / 8 / (1 + 900 / reynolds + 12.7 * (cf / 8) ** .5 * (PR ** .6667 - 1))


def Nusselt0_Kraussold(reynolds):
    return .023 * reynolds ** .8 * PR ** .4


def Cf(ploss, velocity):
    return ploss * 4 * RAD / LEN / RHO / velocity ** 2


def Cf0(reynolds):
    return 0.3164 / reynolds ** .25


''' setup flat baseline '''
# df0 = pd.read_csv(root + '2F.csv', 
#     index_col=['Height', 'Pitch', 'ReynoldsTh'])

# df0['ReynoldsAc'] = Reynolds(df0['Velocity'], df0['Viscosity'])
# df0['Nusselt'] = Nusselt(df0['HeatFlux'], df0['Temperature'])
# df0['Cf'] = Cf(df0['PressureLoss'], df0['Velocity'])

# df0['NusseltError'] = df0['Nusselt'] / Nusselt0_Petukhov(df0['ReynoldsAc'], df0['Cf'])
# df0['CfError'] = df0['Cf'] / Cf0(df0['ReynoldsAc'])

# df0.to_csv(root + '2F.csv')

''' evaluate rough '''
mode = 'R'

df0 = pd.read_csv(root + '2F.csv', 
    index_col=['Height', 'Pitch', 'ReynoldsTh'])
df = pd.read_csv(root + f'2{mode}.csv', 
    index_col=['Height', 'Pitch', 'ReynoldsTh'])

df['ReynoldsAc'] = Reynolds(df['Velocity'], df['Viscosity'])

Nu0 = Nusselt0_Kraussold(df['ReynoldsAc']) * np.broadcast_to(df0['NusseltError'].values.reshape(1, -1), 
    (len(df) // len(df0), len(df0))).reshape(-1,)
Cf0 = Cf0(df['ReynoldsAc']) * np.broadcast_to(df0['CfError'].values.reshape(1, -1), 
    (len(df) // len(df0), len(df0))).reshape(-1,)

df['Nusselt'] = Nusselt(df['HeatFlux'], df['Temperature']) / Nu0
df['Cf'] = Cf(df['PressureLoss'], df['Velocity'])  / Cf0
df['Performance'] = df['Cf'] ** .4 / df['Nusselt'] ** 1.4

df.to_csv(root + f'2{mode}.csv')

''' inspect '''
# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
print(df)


class Evaluator():


    def __init__(self):
        pass


    @staticmethod
    def values(path):
        data = []
        with open(path, 'r') as file:
            for line in file.readlines():
                for x in line.split():
                    try:
                        data.append(float(x))
                    except ValueError:
                        continue
        return data

    heights = {'00': .00,
               '10': .01,
               '20': .02,
               '30': .03,
               '40': .04,
               '50': .05,
               '60': .06,
               '70': .07}
    pitches = {'000': .00,
               '025': .25,
               '050': .5,
               '100': 1.,
               '150': 1.5}
    reynolds = {'10': 10e3,
                '20': 20e3,
                '30': 30e3,
                '40': 40e3,
                '50': 50e3,
                '60': 60e3}

    def evaluate(self):
        ''' delete previous output file '''
        try:
            os.remove('..\\..\\..\\out\\out.csv')
        except FileNotFoundError:
            pass
        
        ''' collect data '''
        data = []
        for path in glob('..\\..\\..\\out\\*.txt'):
            out = self.values(path)

            ''' decode name '''
            h, p, r = path[16:25].split('-')

            height = Helper.heights[h]
            pitch = Helper.pitches[p]
            reynolds = Helper.reynolds[r]

            ''' evaluate rough '''
            velocity = out[3]
            viscosity = out[5]
            temperature = out[7]
            heat_flux = out[10]
            pressure_loss = out[11] - out[12]

            ''' evaluate flat '''
            # velocity = out[1]
            # viscosity = out[3]
            # temperature = out[5]
            # heat_flux = out[7]
            # pressure_loss = out[8] - out[9]

            data.append([height, 
                         pitch, 
                         reynolds, 
                         velocity, 
                         viscosity,
                         temperature, 
                         heat_flux,
                         pressure_loss])

        df = pd.DataFrame(data, columns=['Height', 
                                         'Pitch', 
                                         'ReynoldsTh', 
                                         'Velocity', 
                                         'Viscosity', 
                                         'Temperature', 
                                         'HeatFlux',
                                         'PressureLoss'])
        df.set_index(['Height', 'Pitch', 'ReynoldsTh'], inplace=True)
        df.to_csv('../../../out/out.csv')
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            print(df)
