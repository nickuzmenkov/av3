from datetime import datetime
from glob import glob
import subprocess
import time
import re


class Log():

    WARN = [
        'Warning: An error or interrupt occurred while reading the journal file.\n',
        'Some commands may not have been completed.\n',
        '>>> host : Exiting...\n'
    ]
    name = re.compile('[0-9][A-Z]-[0-9][0-9]-[0-9][0-9][0-9]')
    last = re.compile('Reading "\.\./msh/.{9}\.msh"\.\.\.\n')


    def __init__(self, partition):
        self.partition = partition
        with open('log.out', 'w') as file:
            file.write(f'Py Log\n{self.clock()}')

    
    @staticmethod
    def clock():
        now = datetime.now()
        return now.strftime("%d/%m/%Y %H:%M:%S\n")


    @property
    def job_id(self):
        return glob('*.out')[-1]
    

    @property
    def log(self):
        with open(f'slurm-{self.job_id}.out', encoding='UTF8') as f:
            log = f.readlines()
            log.reverse()
            return log


    @property    
    def jou(self):
        with open('cmd.jou') as f:
            jou = f.readlines()
            jou.reverse()
            return jou


    @jou.setter
    def jou(self, cmd):
        with open('cmd.jou') as f:
            f.writelines(cmd)


    def note(self):
        with open('log.out', 'a') as f:
            file.write(f'Failed job {self.last_call}\n')


    def watch(self, check_delay=60):
        time.sleep(300)
        while 1:
            time.sleep(check_delay)
            if any([x for x in self.log if x in self.WARN]):
                self.note()
                self.checkpoint()
                break


    def last_call(self):
        for line in self.log:
            if self.last.fullmatch(line):
                return self.name.search(line)


    def trunc(self):
        jou = self.jou
        last_call = self.last_call()
        for i in range(len(jou)):
            if jou[i] == f'; {last_call} END\n':
                break
        try:
            self.jou = jou[i + 1:]
            return 0
        except IndexError:
            return None


    def cancel_job(self):
        subprocess.run(f'scancel {self.job_id}')


    def submit_job(self):
        subprocess.run(f'sbatch --partition={self.partition} cmd.sh',
                       shell=True)


    def checkpoint(self):
        self.cancel_job()
        if self.trunc():
            self.submit_job()
            self.watch()


#---------------

log = Log('skylake')
log.submit_job()
log.watch()