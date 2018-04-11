#! /usr/bin/env python3.6
import requests
import urllib3
import sys
import validators

#to initialize, do x = object_manager.InfobloxManager()

class InfobloxManager(object):

    def __init__(self):

        """ for other users, can alter username/password to take input
        instead of hard-coding like below. please ask if needed"""

        self.wapi_url = "https://ip-of-infoblox-appliance/wapi/v2.3.1/"
        self.username = "username"
        self.password = "password"
        # below can be Default/External, whatever view you need
        self.dns_view = "External"

    def create_record(self, primary, secondary, primary_type,
                      secondary_type, wapi_id):
        if secondary_type == "name":
            secondary = name_check(secondary)
        else:
            primary = name_check(primary)
            # need to confirm no cname already exists in database
            req_params = {primary_type: primary, "view": self.dns_view}
            record_search = requests.get(self.wapi_url + "record:cname",
                                         data=req_params,
                                         auth=(self.username,
                                               self.password),
                                         verify=False)
            record_search = record_search.json()
            if record_search:
                return(print("CNAME already exists for: %s" % (primary)))
        req_params = {primary_type: primary, secondary_type: secondary,
                      "view": self.dns_view}

        # need to confirm no cname already exists in database
        
        new_record = requests.post(self.wapi_url + wapi_id,
                                   data=req_params,
                                   auth=(self.username,
                                         self.password),
                                   verify=False)
        return(print("Record: [%s - %s] has been added" % (primary,
                                                           secondary)))

    def create_ptr_record(self, ip, name,
                          auth_zone="reverse-mapping.zone"):
        req_params = {"ipv4addr": ip, "ptrdname": name,
                      "view": self.dns_view}
        new_record = requests.post(self.wapi_url + "record:ptr",
                                   data=req_params,
                                   auth=(self.username,
                                         self.password),
                                   verify=False)
        return(print("PTR \"%s - %s\" has been added" % (name, ip)))

    def delete_ptr_record(self, ip, auth_zone="reverse-mapping.zone"):
        try:
            ptr_record = requests.get(self.wapi_url + "record:ptr",
                                      data={"ipv4addr": ip},
                                      auth=(self.username,
                                            self.password),
                                      verify=False)
            ptr_record = ptr_record.json()
            record_ref = (ptr_record[0]["_ref"])
            record_delete = requests.delete(self.wapi_url + record_ref,
                                            auth=(self.username,
                                                  self.password),
                                            verify=False)
            return(print("PTR \"%s\" has been deleted" % (ptr_record[1])))
        except:
            return(True)

    def pull_info(self, primary):
        records = []
        record_types = ""

        if validators.ipv4(primary):
            primary = primary
            identifier = "ipv4addr"
        else:
            primary = name_check(primary)
            identifier = "name"
        record_types = ["record:cname", "record:txt", "record:a"]
        for option in record_types:
            get_records = requests.get(self.wapi_url + option,
                                      data={identifier:primary},
                                      auth=(self.username,
                                            self.password),
                                      verify=False)
            if get_records:
                records.append(get_records.json())

        if records == []:
            print("No valid record found")
            raise sys.exit()
        list_num = 1

        for record in records:
            x = 0
            while x < len(record):
                if "text" in record:
                    search_value = "text"
                    record_id = "txt record"
                elif "cname" in record:
                    search_value = "cname"
                    record_id = "cname record"
                else:
                    search_value = identifier
                    record_id = "a record"
                print("%s. %s: %s - %s" % (list_num, record_id,
                                           record[x]["name"],
                                           record[x][search_value]))
                list_num+=1
                x+=1
        user_choice = input("> ")
        # use python list rules which start at index 0 NOT 1
        user_choice = int(user_choice) - 1
        del_record = records[0][user_choice]
        record_del = requests.delete(self.wapi_url + del_record["_ref"],
                                     auth=(self.username,
                                           self.password),
                                     verify=False)
        return("DONE")

def name_check(name):

    """ This is to check to determine whether user input already
    contains an owned domain or if one needs to be appended."""

    auth_zone = "user.domain"
    if name.endswith(auth_zone):
        name = name
        return(name)
    else:
        name = name + auth_zone
        return(name)

requests.packages.urllib3.disable_warnings()
# suppress irrelevant messages to end user
