# delphis_cows
A project to analyze cows tagdata 

To use this script, simply:
1) Create a virtual nevironment and run: pip install -r requirements.txt
2) Add a file called "creds.py" that has the following lines:
    API_KEY = <your_key>
    TENANT_ID = <tenant_id>
    (You get those from your pozyx account)
   
4) Run the file reporting_tool.py

The tool will receieve information from your pozyx tags and will output to the screen average sucessful signals rate every X seconds (as defined in the variable TIMESPANS_FOR_CALC_IN_SEC)
