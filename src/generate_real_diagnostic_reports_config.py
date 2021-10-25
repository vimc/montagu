#!/usr/bin/env python3

import paths
import yaml
from copy import copy
from os import chdir
from os.path import abspath, dirname, join


def generate():
    report = "diagnostics-burden-report"
    subject = "VIMC diagnostic report: {touchstone} - {group} - {disease}"
    timeout = 1800

    vimc_recipients = [
        "k.gaythorpe@imperial.ac.uk",
        "susy.echeverria-londono@imperial.ac.uk",
        "x.li@imperial.ac.uk",
        "j.toor@imperial.ac.uk",
        "j.roth@imperial.ac.uk",
        "a.hartner@imperial.ac.uk",
        "e.russell@imperial.ac.uk",
        "montagu-help@imperial.ac.uk"
    ]

    group_diseases = {
        "Cambridge-Trotter": ["MenA"],
        "CDA-Razavi": ["HepB"],
        "Emory-Lopman": ["Rota"],
        "Harvard-Sweet": ["HPV"],
        "IC-Garske": ["YF"],
        "IC-Hallett": ["HepB"],
        "ICDDRB-Qadri": ["Typhoid"],
        "IVI-Kim": ["Cholera", "Typhoid"],
        "JHU-Lee": ["Cholera", "Typhoid"],
        "JHU-Lessler": ["Rubella"],
        "JHU-Lessler-WHO": ["Rubella"],
        "JHU-Tam":	["Hib", "PCV", "Rota"],
        "KPW-Jackson": ["MenA"],
        "Li": ["HepB"],
        "LSHTM-Clark": ["Hib", "PCV", "Rota"],
        "LSHTM-Jit": ["HPV", "Measles"],
        "LSHTM-Jit-WHO": ["Measles"],
        "NUS-Chen": ["PCV"],
        "OUCRU-Clapham": ["JE"],
        "PHE-Vynnycky": ["Rubella"],
        "PHE-Vynnycky-WHO": ["Rubella"],
        "PSU-Ferrari":	["Measles"],
        "PSU-Ferrari-WHO": ["Measles"],
        "UND-Moore": ["JE"],
        "UND-Perkins": ["YF"],
        "Yale-Pitzer": ["Typhoid"],
        "VIMC": ["Typhoid", "Cholera"]
    }

    group_PIs = {
        "Cambridge-Trotter": ["clt56@cam.ac.uk","ak889@cam.ac.uk"],
        "CDA-Razavi": "homie.razavi@centerforda.com",
        "Emory-Lopman": ["benjamin.alan.lopman@emory.edu","alicia.nicole.mullis.kraay@emory.edu"],
        "Harvard-Sweet": ["ssweet@hsph.harvard.edu","aportnoy@mail.harvard.edu","jkim@hsph.harvard.edu"],
        "IC-Garske": ["k.gaythorpe@imperial.ac.uk","keith.fraser@imperial.ac.uk"],
        "IC-Hallett": ["timothy.hallett@imperial.ac.uk","m.de-villiers@imperial.ac.uk"],
        "ICDDRB-Qadri": "fqadri@icddrb.org",
        "IVI-Kim": "jonghoon.kim@ivi.int",
        "JHU-Lee": ["elizabeth.c.lee@jhu.edu","kzou7@jhu.edu","azman@jhu.edu"],
        "JHU-Lessler": ["justin@jhu.edu","akwinter@jhu.edu","shauntruelove@jhu.edu"],
        "JHU-Lessler-WHO": "justin@jhu.edu",
        "JHU-Tam":  ["yvonneyotam@jhu.edu","ecarter@jhu.edu"],
        "KPW-Jackson": "Eric.Johnson@kp.org",
        "Li": "xi.cira.li@gmail.com",
        "LSHTM-Clark": ["Kaja.Abbas@lshtm.ac.uk","Mark.Jit@lshtm.ac.uk","Petra.Klepac@lshtm.ac.uk","Hira.Tanvir@lshtm.ac.uk","Kiesha.Prem@lshtm.ac.uk"],
        "LSHTM-Jit": ["Mark.Jit@lshtm.ac.uk","Kaja.Abbas@lshtm.ac.uk","Han.Fu@lshtm.ac.uk","Megan.Auzenbergs@lshtm.ac.uk"],
        "LSHTM-Jit-WHO": "Mark.Jit@lshtm.ac.uk",
        "NUS-Chen": ["ephchc@nus.edu.sg","ephjkje@nus.edu.sg","Mark.Jit@lshtm.ac.uk"],
        "OUCRU-Clapham": ["hannah.clapham@nus.edu.sg","shreya@nus.edu.sg"],
        "PHE-Vynnycky": ["emilia.vynnycky@phe.gov.uk","timos.papadopoulos@phe.gov.uk"],
        "PHE-Vynnycky-WHO": "emilia.vynnycky@phe.gov.uk",
        "PSU-Ferrari": "mjf283@psu.edu",
        "PSU-Ferrari-WHO": "mjf283@psu.edu",
        "UND-Moore": ["smoore15@nd.edu","qtran4@nd.edu"],
        "UND-Perkins": ["taperkins@nd.edu","John.H.Huber.24@nd.edu"],
        "Yale-Pitzer": ["virginia.pitzer@yale.edu","holly.burrows@yale.edu"],
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
                "success_email": {
                    "recipients": copy(vimc_recipients),  # TODO: add pi_email
                    "subject": subject
                },
                "timeout": timeout
            }]

    file_path = join(paths.container_config, "task_queue", "real_diagnostic_reports.yml")
    with open(file_path, "w") as file:
        file.write('# This file was generated using ./src/generate_real_diagnostic_reports_config.py\n')
        file.write('# Do not edit this file manually.\n')
        yaml.dump(config, file)
    print("Wrote config to: " + file_path)


if __name__ == "__main__":
    abspath = abspath(__file__)
    chdir(dirname(abspath))
    generate()
