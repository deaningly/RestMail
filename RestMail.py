import requests
import random
import string
import imaplib
import email
from email.header import decode_header
import time

class RestMail:
    def __init__(self):
        # cPanel credentials and domain information
        self.cpanel_url = "website.tld:2083"
        self.api_token = "APITOKEN"
        self.cpanel_user = "CPANELUSER"
        self.domains = ["domain@tld", "domain@tld"] # 0,1, etc
        self.imap_server = "mail.website.tld"
        self.imap_port = 993
        
        # Store current email details
        self.email = None
        self.password = None
        self.domain = None
        self.username = None

    def create_email(self, domain_index=0):
        if not 0 <= domain_index < len(self.domains):
            raise ValueError("Invalid domain index")

        # Generate random username (5 letters + 5 numbers)
        letters = ''.join(random.choices(string.ascii_lowercase, k=5))
        numbers = ''.join(random.choices(string.digits, k=5))
        username = f"{letters}{numbers}"
        
        # Generate random password
        password = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=12))
        domain = self.domains[domain_index]

        data = {
            "cpanel_jsonapi_user": self._cpanel_user,
            "cpanel_jsonapi_apiversion": "2",
            "cpanel_jsonapi_module": "Email",
            "cpanel_jsonapi_func": "addpop",
            "domain": domain,
            "email": username,
            "password": password,
            "quota": 1,
        }

        headers = {
            "Authorization": f"cpanel {self._cpanel_user}:{self._api_token}"
        }

        try:
            response = requests.post(f"{self._cpanel_url}/json-api/cpanel", data=data, headers=headers, verify=True)
            response.raise_for_status()
            result = response.json()
            
            if result['cpanelresult']['data'][0]['result'] == 1:
                self.email = f"{username}@{domain}"
                self.password = password
                self.domain = domain
                self.username = username
                return self.email, password
            return None
        except:
            return None

    def check_mail(self, left_string, right_string, timeout=30):
        if not all([self.email, self.password]):
            raise ValueError("No email account created")

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                mail = imaplib.IMAP4_SSL(self._imap_server, self._imap_port)
                mail.login(self.email, self.password)
                mail.select("inbox")

                _, messages = mail.search(None, "ALL")
                for num in messages[0].split():
                    _, msg_data = mail.fetch(num, "(RFC822)")
                    email_body = msg_data[0][1]
                    email_message = email.message_from_bytes(email_body)
                    
                    # Get body content
                    if email_message.is_multipart():
                        for part in email_message.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode()
                                break
                    else:
                        body = email_message.get_payload(decode=True).decode()

                    # Search for content between strings
                    start = body.find(left_string)
                    if start != -1:
                        start += len(left_string)
                        end = body.find(right_string, start)
                        if end != -1:
                            mail.logout()
                            return body[start:end].strip()

                mail.logout()
                time.sleep(2)  # Wait before checking again
            except:
                time.sleep(2)
                continue

        return None

    def delete_email(self):
        if not all([self.username, self.domain]):
            raise ValueError("No email account to delete")

        data = {
            "cpanel_jsonapi_user": self._cpanel_user,
            "cpanel_jsonapi_apiversion": "2",
            "cpanel_jsonapi_module": "Email",
            "cpanel_jsonapi_func": "delpop",
            "domain": self.domain,
            "email": self.username,
        }

        headers = {
            "Authorization": f"cpanel {self._cpanel_user}:{self._api_token}"
        }

        try:
            response = requests.post(f"{self._cpanel_url}/json-api/cpanel", data=data, headers=headers, verify=True)
            response.raise_for_status()
            result = response.json()
            
            if result['cpanelresult']['data'][0]['result'] == 1:
                self.email = None
                self.password = None
                self.domain = None
                self.username = None
                return True
            return False
        except:
            return False
