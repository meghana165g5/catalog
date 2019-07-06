## Item Catalog
###  Overview of Project
Mobile Market is a platform for marketing that could be done among vendors and customers. Different types of mobiles in different brands are being provided and authentication, user registration were also provided by google oAuth2 .Vendors who have registered in the store can add, edit and delete their mobiles  and brands from the store.
### Why This Project?
The present day web applications have been providing easy to use features to their customers; if we go thoroughly, creating, reading, updating and deleting  are the operations performed on data. In this project, you're developing a website with adequate data storage that imparts a enthralling service to users.
### Files Included
1.database_setup.py
2.catalog.py
3.templates folder
4.client_secrets.json
5.Database File
6.requirements.txt
### Some things you might need 
* Python3
* Vagrant 
* VirtualBox 
* Git
### How to Get Started
#### step1: software configuration
1.To install python 3 ,go to  [this](https://realpython.com/installing-python/)
 2.To install Vagrant and VirtualBox ,go to  [this](https://github.com/udacity/fullstack-nanodegree-vm)
 3.clone [this](https://github.com/udacity/fullstack-nanodegree-vm)
 4.Save the Mobile_Market project folder in vagrant folder 
 5.Now open the command prompt in the project location as adminstrator and run  `pip  install  -r  requirements.txt`
#### step2:project configuration
1.From the vagrant folder Open the git bash and give  command  `vagrant up`
2.`vagrant ssh`
3.`cd /vagrant`
4.`cd Mobile_Market`
5.`python3 catalog.py`
#### Important Urls:
Mobile Marketing [home](http://localhost:5000/)
Mobiles [json](http://localhost:5000/category/items.json)
Specific Category Mobiles [json](http://localhost:5000/category/1/items.json)