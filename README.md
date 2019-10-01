# active-learning-doccano
active learning for NLP with doccano annotation-tool 

### setup

    pip install -r requirements.txt
    
#### 1. [doccano](git@github.com:dertilo/doccano.git)
    
    git clone git@github.com:dertilo/doccano.git
    cd doccano
    docker-compose up -d
    
#### 2. postgres+pgadmin docker-compose

    set -a
    source database_variables.sh
    docker-compose up -d
    
##### pgadmin  
    login: `pgadmin4@pgadmin.org`  
    password: `admin`  
 
