#TODO: Wouldn't hurt to add some error trapping

import requests
from base64 import b64encode
import math
import csv
import credentials

email_api_key = credentials.email + ":" + credentials.api_key
bytes_literal = email_api_key.encode("utf-8")

def get_toggl_clients():
    # status=active only works on a premium plan
    data = requests.get(f'https://api.track.toggl.com/api/v9/workspaces/{credentials.workspace}/clients?status=active', headers={'content-type': 'application/json', 'Authorization' : 'Basic %s' %  b64encode(bytes_literal).decode("ascii")})
    apiResponse = data.json()
    return apiResponse;

def get_time_entries(params):
    # meta=true is needed to get client name, that's the only thing that will match back to client list
    data = requests.get('https://api.track.toggl.com/api/v9/me/time_entries?meta=true', params=params, headers={'content-type': 'application/json', 'Authorization' : 'Basic %s' %  b64encode(b"bosuch@gmail.com:ZutTpTS9cfQrAQL").decode("ascii")})
    apiResponse = data.json()
    return apiResponse;

def round_up_to_05(number):
    return math.ceil(number * 20) / 20

print("Toggl clients:")
client_list = get_toggl_clients()

for index,item in enumerate(client_list):
    # Note, adding a ZZ to the beginning of a client name is my way of archiving, since I'm on the free plan
    if item["name"][0:2].upper() != "ZZ":
        print(str(index +1), "-", item["name"])
        
print("")
client_selection = int(input("Select a client: "))

client_name = client_list[client_selection-1]["name"]

print("")
start_date = input("Enter start date in form YYYY-MM-DD: ")
end_date = input("Enter end date in form YYYY-MM-DD: ")

# rate is not needed since I can't upload an invoice directly to Square
# if using a different system that allows uploads then the ouput will need to be modified
#rate = int(input("Enter the current billing rate: $"))

report_dictionary = {}

date_params = {'start_date': start_date, 'end_date': end_date}
time_entry_list = get_time_entries(date_params)
for item in time_entry_list:
    if item["client_name"] == client_name:
        #amount_earned = round(item["duration"] * (rate/3600), 2)
        hours = item["duration"] / 3600
        #For debugging:
        #print(item["description"],"-",item["duration"],"- Earned: $",str(amount_earned),"- Hours:",hours,"- Hours rounded:",str(round_up_to_05(hours)))
        #See if the item exists in the dictionary
        if item["description"] in report_dictionary:
            #If so, sum the hours
            current_hours = report_dictionary[item["description"]] + round_up_to_05(hours)
            report_dictionary[item["description"]] = current_hours
        else:
            #If not, do the initial add
            report_dictionary[item["description"]] = round_up_to_05(hours)
        
print("-------------------------------")

sorted_report_dictionary = dict(sorted(report_dictionary.items()))

#Output to CSV
filename = client_name + " timesheet " + start_date + " to " + end_date + ".csv"
with open(filename, 'w', newline='') as f:
    w = csv.writer(f)
    w.writerows(sorted_report_dictionary.items())
    
print(f"File '{filename}' saved")

