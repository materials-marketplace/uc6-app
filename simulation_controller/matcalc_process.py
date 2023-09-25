"""Defines the basic functions to run MatCalc calculations."""

import os
import string
import subprocess
import zipfile
from enum import Enum
from multiprocessing import Process
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from models.transformation import TransformationInput

matplotlib.use("Agg")


MATCALC_PATH = Path("/opt/matcalc/")
TEMPLATES_FOLDER_PATH = "/root/app/simulation_controller/templates"


class Calculation(Enum):
    def __str__(self):
        return str(self.value)

    EQUILIBRIUM = "equilibrium"
    SCHEIL = "scheil"


class MatCalcProcess(Process):
    def __init__(self, process_input: TransformationInput, output_path: Path):
        os.chdir(str(output_path))
        super().__init__()
        self.elements = process_input.elements
        self.exit_code = None
        self.phases = [
            "LIQUID",
            "FCC_A1",
            "BCC_A2",
            "CEMENTITE",
            "M23C6",
            "M7C3",
            "M6C",
            "LAVES_PHASE",
        ]
        self.output_path = output_path
        self.substitutes = {
            "third": self.elements[2].element.value,
            "c_third": self.elements[2].weightPercentage,
            "c_C": self.elements[1].weightPercentage,
        }

    def run(self):
        files_equilibrium = self.equilibrium_calculation()
        files_scheil = self.scheil_calculation()

        # Write all files to a zip archive and delete them
        with zipfile.ZipFile(self.output_path / "results.zip", mode="w") as zf:
            for file in (*files_equilibrium, *files_scheil):
                zf.write(file)
                os.remove(file)
        return subprocess.CompletedProcess(args=self.elements, returncode=0)

    def equilibrium_calculation(self):
        with open(
            os.path.join(TEMPLATES_FOLDER_PATH, "equilibrium.mcs"), "r"
        ) as file:
            template = file.read()

        # TODO: set phases
        script = string.Template(template).safe_substitute(self.substitutes)

        # Write the MatCalc script for the stepped equilibrium calculation
        with open("equilibrium.mcs", "w") as file:
            file.write(script)

        # Run the stepped equilibrium calculation in MatCalc
        subprocess.run(
            [MATCALC_PATH / "mcc", "equilibrium.mcs"],
            check=True,
            stdout=open(os.devnull, "wb"),
        )  # 'mcc' calls the MatCalc console

        # Read the MatCalc results
        results = (np.loadtxt("T_C.dat"),)
        header = "T$C".ljust(12, " ")
        fmt = ["%.6e"]
        for phase in self.phases:
            results += (np.loadtxt("f_{}.dat".format(phase)),)
            label = "f$" + phase
            header += "\t" + label.ljust(12, " ")
            fmt += ["%.{0:d}e".format(max(len(label) - 6, 6))]

        # Write the results to one file

        data_file = self.output_path / "equilibrium.dat"
        np.savetxt(
            data_file,
            np.c_[results],
            fmt=fmt,
            delimiter="\t",
            header=header,
            comments="",
        )

        # Plot the results and save the figure

        plot_file = self.output_path / "equilibrium.png"
        legend = []
        plt.figure(figsize=(4.0, 3.0))
        for i in range(1, len(results)):
            if (results[i] > 0.0).any():
                plt.semilogy(results[0], results[i])
                legend += [self.phases[i - 1]]
        plt.xlabel("Temperature in °C")
        plt.ylabel("Phase Fraction")
        plt.ylim((1e-4, 1.5))
        plt.legend(legend)
        plt.tight_layout()
        plt.savefig(plot_file, dpi=600)
        plt.close()

        # Remove the MatCalc files
        os.remove("equilibrium.mcs")
        os.remove("T_C.dat")
        for phase in self.phases:
            os.remove(f"f_{phase}.dat")

        return (data_file, plot_file)

    def scheil_calculation(self):
        """_summary_

        Raises:
            RuntimeError: _description_
        """
        with open(
            os.path.join(TEMPLATES_FOLDER_PATH, "Scheil.mcs"), "r"
        ) as file:
            template = file.read()

        # TODO: send phases to MatCalc
        script = string.Template(template).safe_substitute(self.substitutes)

        # Write the MatCalc script for the Scheil calculation
        with open("Scheil.mcs", "w") as file:
            file.write(script)

        # Run the Scheil calculation in MatCalc
        subprocess.run(
            [MATCALC_PATH / "mcc", "Scheil.mcs"], check=True
        )  # 'mcc' calls the MatCalc console

        # Read the MatCalc results
        results = (np.loadtxt("T_C.dat"),)
        header = "T$C".ljust(12, " ")
        fmt = ["%.6e"]
        for phase in self.phases:
            results += (np.loadtxt("f_{}_S.dat".format(phase)),)
            label = "f$" + phase
            header += "\t" + label.ljust(12, " ")
            fmt += ["%.{0:d}e".format(max(len(label) - 6, 6))]

        # Write the results to one file

        data_file = self.output_path / "Scheil.dat"
        np.savetxt(
            data_file,
            np.c_[results],
            fmt=fmt,
            delimiter="\t",
            header=header,
            comments="",
        )

        # Plot the results and save the figure

        plot_file = self.output_path / "Scheil.png"
        legend = []
        plt.figure(figsize=(4.0, 3.0))
        for i in range(1, len(results)):
            if (results[i] > 0.0).any():
                plt.semilogy(results[0], results[i])
                legend += [self.phases[i - 1]]
        plt.xlabel("Temperature in °C")
        plt.ylabel("Phase Fraction")
        plt.ylim((1e-4, 1.5))
        plt.legend(legend)
        plt.tight_layout()
        plt.savefig(plot_file, dpi=600)
        plt.close()

        # Remove the MatCalc files
        os.remove("Scheil.mcs")
        os.remove("T_C.dat")
        for phase in self.phases:
            os.remove("f_{}_S.dat".format(phase))

        return (data_file, plot_file)
