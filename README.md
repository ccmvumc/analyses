# analyses
Dax analysis processors and related resources



Processors

The dax processors in .yaml files specify the requirements for each processing pipeline.
These requirements include inputs from xnat, containers to run, and cluster settings to be used for processing.

A processor specifies a main command to be run.  Optionally, a processor can have a pre command and/or a post command for setup/teardown of the main command. Each of the pre/main/post commands is run in a singularity container as specified.

Inputs are files stored in XNAT and can pulled from subject assessors, session assessors, or session scans. Outputs are files uploaded back to XNAT. Any files found in the OUTPUTS folder are uploaded to the Analysis folder at the project level in XNAT.

To enable a processor on a project, we add a record in the DAX Project Settings project on REDCap. We set the path to the repository in REDCap. The format must be "user/repo:version" where version is in the format "vX.Y.Z". This version must be a tag on github.



Creating a release

Each analysis is linked to a release of the analysis repository. To create a release, we click Create New Release, enter the new version, click Auto-Generate notes and click release. The version you enter should follow semver. Briefly, a major change increments X, a minor change increments Y, and a patch increments Z.


Processors must either be the top level processor named processor.yaml or in a subdirectory of the subdirectory processors. The subdirectory is used to identify the processor which is in a file named processor.yaml.



To summarize, using this repo:
  - Clone
  - PR
  - Determine version
  - Merge
  - Release
  - Update REDCap analysis record(s)

