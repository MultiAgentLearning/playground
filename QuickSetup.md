# Mac setup

### Setup virtual environment
You'll need a virtual python environment to run the project.  

You can follow this guide to do so http://sourabhbajaj.com/mac-setup/Python/virtualenv.html

Note that you probably want to install virtual environment as root user using sudo command
```$ sudo -H pip3 install virtualenv```

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



