import cmdstanpy
import os

if os.name == 'nt':
    cmdstanpy.install_cmdstan(compiler=True)
else:
    cmdstanpy.install_cmdstan()