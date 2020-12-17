from glob import glob
import pandas as pd
import numpy as np
import re


class Collector():


    name = re.compile('[0-9][A-Z]-[0-9][0-9]-[0-9][0-9][0-9]-[0-9][0-9]')
    hs = {
        '00': .00,
        '10': .01,
        '20': .02,
        '30': .03,
        '40': .04,
        '50': .05,
        '60': .06,
        '70': .07
    }
    ps = {
        '000': .00,
        '025': .25,
        '050': .5,
        '100': 1.,
        '150': 1.5
    }
    rs = {
        '10': 10e3,
        '20': 20e3,
        '30': 30e3,
        '40': 40e3,
        '50': 50e3,
        '60': 60e3
    }
    cols = ['Height', 'Pitch', 'ReynoldsTh', 'Velocity', 'Viscosity', 'Temperature', 'HeatFlux', 'PressureLoss']


    @staticmethod
    def file_eval(path):
        vals = []
        with open(path, 'r') as file:
            for line in file.readlines():
                for x in line.split():
                    try:
                        vals.append(float(x))
                    except ValueError:
                        continue
        return vals


    @staticmethod
    def rough_filt(vals):
        return vals[3], vals[5], vals[7], vals[10], vals[11] - vals[12]


    @staticmethod
    def flat_filt(vals):
        return vals[1], vals[3], vals[5], vals[7], vals[8] - vals[9]


    def path_parse(self, path):
        name = self.name.search(path).group(0)
        _, h_code, p_code, r_code = name.split('-')
        h = self.hs[h_code]
        p = self.ps[p_code]
        r = self.rs[r_code]
        return h, p, r


    def file_to_sample(self, path, filt):
        vals = filt(self.file_eval(path))
        name = self.path_parse(path)
        return pd.Series(name + vals, self.cols)


    def files_to_df(self, path, filt):
        df = pd.DataFrame(columns=self.cols)
        for file in glob(path + '*.txt'):
            df = df.append(self.file_to_sample(file, filt), ignore_index=True)
        df.set_index(['Height', 'Pitch', 'ReynoldsTh'], inplace=True)
        return df


class Evaluator():


    RAD = .005
    LEN = .3
    AREA = 2 * np.pi * RAD * LEN

    RHO = 1.225
    LAM = .0242
    PR = .744
    TWALL = 1000


    def Reynolds(self, velo, visc):
        return velo * self.RHO * 2 * self.RAD / visc



    def Nusselt(self, heat, temp):
        return heat / self.AREA / (self.TWALL - temp) * 2 * self.RAD / self.LAM


    def Nusselt0_Petukhov(self, re, cf):
        return cf * re * self.PR / 8 / (1 + 900 / re + 12.7 * (cf / 8) ** .5 * (self.PR ** .6667 - 1))


    def Nusselt0_Kraussold(self, re):
        return .023 * re ** .8 * self.PR ** .4


    def Cf(self, ploss, velo):
        return ploss * 4 * self.RAD / self.LEN / self.RHO / velo ** 2


    def Cf0(self, re):
        return 0.3164 / re ** .25


    def Performance(self, nu, cf):
        return cf ** .4 / nu ** 1.4


class FlatEvaluator(Evaluator):


    def __init__(self):
        super().__init__()


    def fit_transform(self, df):
        df['ReynoldsAc'] = Reynolds(df['Velocity'], df['Viscosity'])
        df['Nusselt'] = Nusselt(df['HeatFlux'], df['Temperature'])
        df['Cf'] = Cf(df['PressureLoss'], df['Velocity'])

        df['NusseltError'] = df['Nusselt'] / Nusselt0_Petukhov(df['ReynoldsAc'], df['Cf'])
        df['CfError'] = df['Cf'] / Cf0(df['ReynoldsAc'])
        return df


class RoughEvaluator(Evaluator):


    def __init__(self):
        super().__init__()


    def fit_transform(self, df, df0):
        df['ReynoldsAc'] = self.Reynolds(df['Velocity'], df['Viscosity'])

        Nu0 = self.Nusselt0_Kraussold(df['ReynoldsAc']) * np.broadcast_to(df0['NusseltError'].values.reshape(1, -1), (len(df) // len(df0), len(df0))).reshape(-1,)
        Cf0 = self.Cf0(df['ReynoldsAc']) * np.broadcast_to(df0['CfError'].values.reshape(1, -1), (len(df) // len(df0), len(df0))).reshape(-1,)

        df['Nusselt'] = self.Nusselt(df['HeatFlux'], df['Temperature']) / Nu0
        df['Cf'] = self.Cf(df['PressureLoss'], df['Velocity']) / Cf0
        df['Performance'] = self.Performance(df['Nusselt'], df['Cf'])
        return df


''' 
================================================================= '''
 
ROOT = 'C:/Users/frenc/YandexDisk/cfd/out/'

collector = Collector()
df = collector.files_to_df(ROOT, collector.rough_filt)

evaluator = RoughEvaluator()

df0 = pd.read_csv(ROOT + '2F.csv', 
                  index_col=['Height', 'Pitch', 'ReynoldsTh'])

df = evaluator.fit_transform(df, df0)

df.to_csv(ROOT + '2R.csv')

''' 
================================================================= '''
