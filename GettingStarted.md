# Getting Started

## Setup
  ### Setup virtual environment
  You'll need a virtual python environment to run the project.  

  You can follow one of theses guides to install virtualenv :
  https://virtualenv.pypa.io/en/stable/installation/
  http://sourabhbajaj.com/mac-setup/Python/virtualenv.html

  Once installed, using command line go to the cloned repository folder  
  ```$ cd myFolder/playground```  
    
  Setup the virtual environment for this specific project  
  ```$ virtualenv venv```  
    
  Activate the virtual environment  
  ```$ source venv/bin/activate```  

  Now you want to install Pommerman dependancies, before doing so make sure the virtual environment is started  
  you should see a (venv) at the beginning of terminal prompt.
  ```pip install -r requirements.txt```

  Once everything is installed, you can start a basic simulation using theses command :
  ``` 
  $ cd games
  $ python run_battle.py --agents=test::a.pommerman.agents.SimpleAgent,test::a.pommerman.agents.SimpleAgent,test::a.pommerman.agents.SimpleAgent,test::a.pommerman.agents.SimpleAgent --config=ffa_v0

  ```

  ### Closing the environement
  You can close the virtual environment using this command
  ```$ deactivate```


## Research
  Proximal Policy Optimization (PPO) [https://arxiv.org/abs/1707.06347](https://arxiv.org/abs/1707.06347)

  Multi-Agent DDPG [https://github.com/openai/maddpg](https://github.com/openai/maddpg)

  Monte Carlo Tree Search [https://gnunet.org/sites/default/files/Browne%20et%20al%20-%20A%20survey%20of%20MCTS%20methods.pdf](https://gnunet.org/sites/default/files/Browne%20et%20al%20-%20A%20survey%20of%20MCTS%20methods.pdf)

  Monte Carlo Tree Search and Reinforcement Learning [https://www.jair.org/media/5507/live-5507-10333-jair.pdf](https://www.jair.org/media/5507/live-5507-10333-jair.pdf)

  Cooperative Multi-Agent Learning [https://link.springer.com/article/10.1007/s10458-005-2631-2](https://link.springer.com/article/10.1007/s10458-005-2631-2)

  Opponent Modeling in Deep Reinforcement Learning [http://www.umiacs.umd.edu/~hal/docs/daume16opponent.pdf](http://www.umiacs.umd.edu/~hal/docs/daume16opponent.pdf)

  Machine Theory of Mind [https://arxiv.org/pdf/1802.07740.pdf](https://arxiv.org/pdf/1802.07740.pdf)

  Coordinated Multi-Agent Imitation Learning [https://arxiv.org/pdf/1703.03121.pdf](https://arxiv.org/pdf/1703.03121.pdf)

  Deep Reinforcement Learning from Self-Play in
  Imperfect-Information Games [https://arxiv.org/pdf/1603.01121.pdf%20and%20http://proceedings.mlr.press/v37/heinrich15.pdf](https://arxiv.org/pdf/1603.01121.pdf%20and%20http://proceedings.mlr.press/v37/heinrich15.pdf)

  Autonomous Agents Modelling Other Agents [http://www.cs.utexas.edu/~pstone/Papers/bib2html-links/AIJ18-Albrecht.pdf](http://www.cs.utexas.edu/~pstone/Papers/bib2html-links/AIJ18-Albrecht.pdf)