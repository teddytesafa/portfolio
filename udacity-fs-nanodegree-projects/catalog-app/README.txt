-- SUMMARY --
The tournament application enables creating new category of items, creating items, editing items in a category, deleting items, and viewing categories and latest items.

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
   

