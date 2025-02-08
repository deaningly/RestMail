# RestMail

RestMail (named after the domain i use dean.rest) is a py script used to create, search and delete temporary mails through cpanel, little personal project used for scraping/automation purposes.

## features
- creates random emails with strong passwords
- deletes them when you're done
- grabs content from emails based on left/right strings

## usage
```python
from RestMail import RestMail

mail = RestMail()
email, password = mail.create_email()
print(email, password)

content = mail.check_mail("start", "end")
print(content)

mail.delete_email()
