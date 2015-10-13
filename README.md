Asana to Wunderlist task converter
==================================

Quick and dirty script to transfer your tasks from Asana to Wunderlist.

Usage
-----
- Export your tasks from Asana to a JSON file by going to a project and choosing "Export > JSON".
- Register an app in Wunderlist at https://developer.wunderlist.com/apps.
- Grab the client id and generate a new access token.
- Call this script: `python convert.py <access_token> <client_id> <json_file>` to have all the tasks and subtasks added to Wunderlist.

Prerequisites
-------------
The only prerequesite is the 'requests' library, which can be installed with `pip install requests`.
