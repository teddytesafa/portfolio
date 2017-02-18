IP Address: 52.24.9.201
URL: http://ec2-52-24-9-201.us-west-2.compute.amazonaws.com/

---SUMMARY OF CONFIGURATION CHANGES—

Created user “grader” and added to sudoers
Updated currently installed packages and upgraded the os
Checked that the time zone is set to UTC
Changed SSH port from 22 to 2200
Generated ssh keys and configured key based authentication
Configured to deny all incoming connections
Configured to allow all outgoing connections
Configured to open ssh( 2200/tcp), http (www port 80), and NTP (123/udp) 
Installed apache webserver
Installed mod_wsgi for python
Installed pip
installed Flask
installed Sql Alchemy
Created a catalog directory in /var/www/ inside grader
Created a catalog directory in /var/www/catalog
Created and configured catalog.wsgi in /var/www/catalog
Renamed project.py to __init__.py and put it in /var/www/catalog/catalog
Stored static and template folders in /var/www/catalog/catalog
Installed postgres
Checkd postgres not to accept remote connections from outside
Created the catalog user with necessary permissions on postgres
Changed the starting engine in __init__.py and database_setup.py create_engine() function to have the catalog user id and password
Change the client_secrets.son file path
Installed the relevant OAuth library from google api 
Changed java script origins to reflect the new address and put the new client_secrets.son in the /var/www/catalog/catalog folder
Gave chmod 750 on client_secrets.json to grader
Run database_setup.py to create the relevant tables
Restarted apache server
Configured sudo to require password
Disabled ssh root login and included user grader and backup user ted as AllowedUsers
Passwords are updated to meet best practice 
Enabled automatic updates
Installed and configured fail2ban
Installed glance for monitoring

-- SUMMARY OF USING THE CATALOG APP--
The category application enables creating new category of items, creating items, editing items in a category, deleting items, and viewing categories and latest items.

--CONTENTS OF catalogapp.zip--
database_setup.py
project.py
static folder (contains all style sheets used): containing style.css, grid.css, normalize.css,
template folder (contains all tempates used): index.html (main), categories.html (page right after login), addcategory.html, newitem.html, itemedit.html, itemdelete.html, login.html, categoryitem.html
      

--SUCCESSFULLY RUNNING THE PROGRAM--
To successfully run the program, follow the following steps:
(1) Setup the database
Please follow the following steps to setup the catalogwithusers database:
  (a) Download the catalog folder to the working directory
  (b) Switch to the working directory 
  (c) In command line terminal, type python
  (d) Then on the => prompt type python database_setup.py
  (e) Now you can exit the database with exit() command
  
 (2) Using the catalogApp 
   (a) To just have read access, go to http:/localhost:5000
   (b) To add category, click login and provide your gplus credentials. If all goes well, you will be redirected to the categories page.
   (c) To add a category, click Add, put the name of the category, and hit submit
   (d) To add item within a category, click a category from the categories list and follow the next page loaded to fill out the name and description of the item to be created.
   (e) To delete an item, click delete in the category item page and cofirm.
   (f) To logout, click logout
   

