#!/usr/bin/env python3

import paths
import yaml
from copy import copy
from os import chdir
from os.path import abspath, dirname, join


def generate():
    report = "diagnostics-burden-report"
    subject = "VIMC diagnostic report: {touchstone} - {group} - {disease}"
    timeout = 7200

    vimc_recipients = [
        "k.gaythorpe@imperial.ac.uk",
        "x.li@imperial.ac.uk",
        "a.hartner@imperial.ac.uk",
        "m.shankar@imperial.ac.uk",
        "e.russell@imperial.ac.uk",
        "montagu-help@imperial.ac.uk"
    ]

    vimc_assignees = {
        "Cholera": "k.gaythorpe",
        "HepB": "x.li",
        "HPV": "k.gaythorpe",
        "Measles": "x.li",
        "MenA": "a.hartner",
        "Rubella": "k.gaythorpe",
        "Typhoid": "k.gaythorpe",
        "YF": "a.hartner"
    }

    group_diseases = {
        "Cambridge-Trotter": ["MenA"],
        "Harvard-Sweet": ["HPV"],
        "IC-Garske": ["YF"],
        "IC-Hallett": ["HepB"],
        "IVI-Kim": ["Cholera", "Typhoid"],
        "JHU-Lee": ["Cholera", "Typhoid"],
        "JHU-Lessler": ["Rubella"],
        "Li": ["HepB"],
        "LSHTM-Jit": ["HPV", "Measles"],
        "PHE-Vynnycky": ["Rubella"],
        "PSU-Ferrari": ["Measles"],
        "UND-Perkins": ["YF"],
        "Yale-Pitzer": ["Typhoid"],
        "VIMC": ["Typhoid", "Cholera"]
    }

    group_PIs = {
        "Cambridge-Trotter": ["clt56@cam.ac.uk", "ak889@cam.ac.uk"],
        "Harvard-Sweet": ["ssweet@hsph.harvard.edu", "aportnoy@mail.harvard.edu"],
        "IC-Garske": ["k.gaythorpe@imperial.ac.uk", "keith.fraser@imperial.ac.uk"],
        "IC-Hallett": ["timothy.hallett@imperial.ac.uk", "m.de-villiers@imperial.ac.uk"],
        "IVI-Kim": ["jonghoon.kim@ivi.int", "Chaelin.Kim@ivi.int"],
        "JHU-Lee": ["elizabeth.c.lee@jhu.edu", "kzou7@jhu.edu", "azman@jhu.edu", "hxu70@jhmi.edu"],
        "JHU-Lessler": ["jlessler@unc.edu", "awinter@uga.edu", "shauntruelove@jhu.edu"],
        "Li": "xi.cira.li@gmail.com",
        "LSHTM-Jit": ["Mark.Jit@lshtm.ac.uk", "Kaja.Abbas@lshtm.ac.uk", "Han.Fu@lshtm.ac.uk", "simon.procter@lshtm.ac.uk"],
        "PHE-Vynnycky": ["Emilia.Vynnycky@ukhsa.gov.uk", "Timos.Papadopoulos@ukhsa.gov.uk"],
        "PSU-Ferrari": ["mjf283@psu.edu", "sah5761@psu.edu", "bwl1@psu.edu"],
        "UND-Perkins": ["taperkins@nd.edu", "qtran4@nd.edu"],
        "Yale-Pitzer": "virginia.pitzer@yale.edu",
        "VIMC": "montagu-help@imperial.ac.uk"
    }

    config = {}
    for group in group_diseases.keys():
        pi_email = group_PIs[group]
        if not isinstance(pi_email, list):
            pi_email = [pi_email]
        config[group] = {}
        for disease in group_diseases[group]:
            parameters = {"disease": disease, "modelling_group": group}
            config[group][disease] = [{
                "report_name": report,
                "parameters": parameters,
                "assignee": vimc_assignees[disease],
                "success_email": {
                    "recipients": copy(vimc_recipients),  # TODO: add pi_email
                    "subject": subject
                },
                "timeout": timeout
            }]

    file_path = join(paths.container_config, "task_queue",
                     "real_diagnostic_reports.yml")
    with open(file_path, "w") as file:
        file.write(
            '# This file was generated using ./src/generate_real_diagnostic_reports_config.py\n')
        file.write('# Do not edit this file manually.\n')
        yaml.dump(config, file)
    print("Wrote config to: " + file_path)


if __name__ == "__main__":
    abspath = abspath(__file__)
    chdir(dirname(abspath))
    generate()
