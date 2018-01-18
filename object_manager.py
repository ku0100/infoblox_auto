#! /usr/bin/env python3.6
import requests
import urllib3

#to initialize, do x = object_manager.InfobloxManager()

class InfobloxManager(object):

    def __init__(self):
        # can alter below to prompt users for sensitive information
        self.wapi_url = "https://url_of_appliance/wapi/v2.3.1/"
        self.username = "username"
        self.password = "password"

    def create_a_record(self, ip, name, dns_view="External",
                        auth_zone=".test.zone"):
        name = name + auth_zone
        req_params = {"ipv4addr": ip, "name": name, "view": dns_view}
        print(req_params)
        new_record = requests.post(self.wapi_url + "record:a",
                                   data=req_params,
                                   auth=(self.username,
                                         self.password),
                                   verify=False)
        print(self.username)
        print(self.password)
        return(new_record)

    def delete_a_record(self, ip, name, dns_view="External",
                        auth_zone=".test.zone"):
        name = name + auth_zone
        req_params = {"ipv4addr": ip, "name": name, "view": dns_view}
        record_delete = requests.get(self.wapi_url + "record:a",
                                        data=req_params,
                                        auth=(self.username,
                                              self.password),
                                        verify=False)
        record_delete = record_delete.json()
        # below is to get the _ref value for record deletion
        record_ref = (record_delete[0]["_ref"])
        deletion = requests.delete(self.wapi_url + record_ref,
                                   auth=(self.username,
                                         self.password),
                                   verify=False)
        return(deletion)

    def create_ptr_record(self, ip, name, dns_view="External",
                          auth_zone=".1.1.in-addr-arpa"):
        req_params = {"ipv4addr": ip, "ptrdname": name, "view": dns_view}
        new_record = requests.post(self.wapi_url + "record:ptr",
                                   data=req_params,
                                   auth=(self.username,
                                         self.password),
                                   verify=False)
        return(print(new_record))

    def delete_ptr_record(self, ip, dns_view="External",
                          auth_zone=".1.1.in-addr-arpa"):
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
            return("Pointer record: %s deleted" % (ptr_record[1]))
        except:
            return(True)

requests.packages.urllib3.disable_warnings()