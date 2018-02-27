# Mac setup

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



