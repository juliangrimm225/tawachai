tawachai
============

tawachai is a project of Julian Grimm. The goal is a web application that combines graph theory with a calendar.

The design is based on the [Flask Mega-Tutorial][1] by Miguel Grinberg.

Features:
---------

* User Registration and Login ![](https://github.com/juliangrimm225/tawachai/blob/master/Pictures/user_registration.png)
* Creation of new Projects as container for Nodes ![](https://github.com/juliangrimm225/tawachai/blob/master/Pictures/project_index.png)
* Creation of Nodes in Projects ![](https://github.com/juliangrimm225/tawachai/blob/master/Pictures/project_overview.png)
* Addition, Removal and Creation of Sub Nodes ![](https://github.com/juliangrimm225/tawachai/blob/master/Pictures/node_overview.png)
** Insertion of ID of unconnected Node in text field: New Node becomes a Sub Node
** Insertion of ID of connected Node in text field: Removes connection between the Nodes
** Insertion of text in text field: Creates a new Node with text as description as Sub Node

[1]: https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world
