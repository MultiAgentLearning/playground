# Pommerman

This directory contains all of the code for Pommerman. This includes:

* agents.py: Baseline agents will reside here in addition to being available in the Docker directory. 
* characters.py: Here lies the actors in the game. This includes Agent, Bomb, and Flame.
* configs.py: This configs module contains the setup. Feel free to edit this in your local directory for easy game loading.
* envs (module):
  * utility.py has shared Enums, constants, and common functions to the different environments.
  * v0.py: This environment is the base one that we use. 
  * v1.py: This is a modification of v0.py that collapses the walls in order to end the game more quickly.
