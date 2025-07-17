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

    # elements: List[str] = list(cfg.elements)

    # make the directories
    for dir_name in ["logs", "results", "batches"]:
        (P.cwd() / dir_name).mkdir()

    for nucleus in cfg.nuclei:
        # Z: int = 0
        # try:
        #     Z = elements.index(nucleus.Z)
        # except ValueError:
        #     raise ValueError(f"{nucleus.Z} is not an element!")

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

                jobname = f"{cfg.args.valence_space}_{cfg.args.LECs}_{cfg.args.method}_{args["reference"]}_e{args["emax"]}_E{args["e3max"]}_s{cfg.args.smax}_hw{args["hw"]}_A{A}"

                args["flowfile"] = f"results/BCH_{jobname}.dat"
                args["intfile"] = f"results/{jobname}"

                cmd_args = " ".join(f"{key}={value}" for key, value in args.items())

                cmd_args = f"{cfg.bin} {cmd_args}"

                DefFile = f"""#!/bin/bash
#SBATCH --account=rrg-holt
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task={cfg.num_threads}
#SBATCH --output={P.cwd()}/logs/{jobname}.%j.out
#SBATCH --error={P.cwd()}/logs/{jobname}.%j.err
#SBATCH --time={time_request}
#SBATCH --mail-user={cfg.email}
#SBATCH --mail-type=END
#SBATCH --mem=187G



cd $SLURM_SUBMIT_DIR
echo SLURM_SUBMIT_DIR = $SLURM_SUBMIT_DIR
echo NTHREADS = {cfg.num_threads}
export OMP_NUM_THREADS={cfg.num_threads}

time srun {cmd_args}
                """

                print("==========================================")

                print(DefFile)

                print("==========================================")

                with open(f"batches/{jobname}.def", "w") as sfile:

                    sfile.write(DefFile)

                call(["sbatch", f"batches/{jobname}.def"])


if __name__ == "__main__":
    main()

"""

"""
