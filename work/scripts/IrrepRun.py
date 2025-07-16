#!/usr/bin/env python

from os import path, environ, mkdir, remove, system
from sys import argv
from subprocess import call, PIPE
from time import time, sleep
from datetime import datetime
from typing import Any, Dict, List
import hydra
from hydra.core.hydra_config import HydraConfig
from omegaconf import ListConfig, OmegaConf as OC, DictConfig as Config
from pathlib import Path as P


@hydra.main(config_path="../config", config_name="parameters", version_base="1.1")
def main(cfg: Config):
    print(OC.to_yaml(cfg))

    elements: List[str] = list(cfg.elements)

    for nucleus in cfg.nuclei:
        Z: int = 0
        try:
            Z = elements.index(nucleus.Z)
        except ValueError:
            raise ValueError(f"{nucleus.Z} is not an element!")

        A: int = nucleus.A

        for e in cfg.batch.e:

            time_request = "00:06:00"

            if e <= 4:
                time_request = "00:06:00"
            elif e <= 6:
                time_request = "01:00:00"
            elif e <= 8:
                time_request = "6:00:00"
            elif e <= 10:
                time_request = "12:00:00"
            elif e <= 12:
                time_request = "24:00:00"
            elif e <= 14:
                time_request = "35:00:00"

            for hw in cfg.batch.hw:

                args: Dict[str, Any] = dict(cfg.args)

                args["reference"] = f"{nucleus.Z}{A}"
                args["emax"] = e
                args["e3max"] = cfg.batch.e3max
                args["hw"] = hw
                args["A"] = A
                args["flowfile"] = f"{P.cwd()}/{args["flowfile"]}"
                args["intfile"] = f"{P.cwd()}/{args["intfile"]}"

                hcfg = HydraConfig.get()

                # print(hcfg.job)

                jobname = hcfg.job.name

                # logname = f"{jobname}_{hcfg.run.dir}"

                cmd_args = " ".join(f"{key}={value}" for key, value in args.items())

                cmd_args = f"{cfg.bin} {cmd_args}"

                DefFile = f"""#!/usr/bin/env bash
#SBATCH --account=rrg-holt
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task={cfg.num_threads}
#SBATCH --output={P.cwd()}/{cfg.out}
#SBATCH --error={P.cwd()}/{cfg.err}
#SBATCH --time={time_request}
#SBATCH --mail-user={cfg.email}
#SBATCH --mail-type=END
#SBATCH --mem=187G



cd $SLURM_SUBMIT_DIR
echo NTHREADS = {cfg.num_threads}
export OMP_NUM_THREADS={cfg.num_threads}

time srun {cmd_args}
                """

                print(DefFile)

                with open(f"{jobname}.def", "w") as sfile:

                    sfile.write(DefFile)

                call(["sbatch", f"{jobname}.def"])


if __name__ == "__main__":
    main()

"""
smax=0 dsmax=0.5 basis=ocsillator omega_norm_max=0.25 file2e1max=18 file2e2max=36 file2lmax=18 file3e1max=18 file3e2max=36 file3e3max=24 method=magnus 2bme=/projects/rrg-holt/shared/TwBME-HO_NN-only_N3LO_EM500_srg1.80_hw16_emax18_e2max36.me2j.gz 3bme=/projects/rrg-holt/shared/NO2B_ThBME_EM1.8_2.0_3NFJmax15_IS_hw16_ms18_36_24.stream.bin LECs=EM1.8_2.0 3bme_type=no2b valence_space=p-shell Operators=M0nu_F_3.54_none,M0nu_GT_3.54_none,M0nu_T_3.54_none reference=Ar36 emax=4 e3max=12 hw=16 A=36

smax=0 dsmax=0.5 basis=oscillator omega_norm_max=0.25 file2e1max=18 file2e2max=36 file2lmax=18 file3e1max=18 file3e2max=36 file3e3max=24 method=magnus reference=Be10 emax=4 e3max=12 2bme=/projects/def-holt/shared/TwBME-HO_NN-only_N3LO_EM500_srg1.80_hw16_emax18_e2max36.me2j.gz 3bme=/projects/def-holt/shared/NO2B_ThBME_EM1.8_2.0_3NFJmax15_IS_hw16_ms18_36_24.stream.bin LECs=EM1.8_2.0 3bme_type=no2b hw=16 A=10 valence_space=p-shell Operators=M0nu_F_3.54_none,M0nu_GT_3.54_none,M0nu_T_3.54_none flowfile=/projects/rrg-holt/k239nguy/results/BCH_p-shell_EM1.8_2.0_magnus_Be10_e4_E12_s0_hw16_A10.dat intfile=/projects/rrg-holt/k239nguy/results/p-shell_EM1.8_2.0_magnus_Be10_e4_E12_s0_hw16_A10
"""
