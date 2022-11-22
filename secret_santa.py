import smtplib
from string import Template
import json
import random
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


CREDENTIALS = 'credentials.json'
CONTACTS = 'emails.txt'
MESSAGE_TEMPLATE_FILE = 'message.txt'
MESSAGE_SUBJECT = 'Test'


# Function to read the credentials file
def parse_json(filename):
    with open(filename, mode='r') as json_file:
        data = json.load(json_file)
        SMTP_SERVER = data['SMTPserver']
        EMAIL = data['email']
        PASS = data['pass']

    return SMTP_SERVER, EMAIL, PASS


# Function to read the emails from a file
def get_contacts(filename):
    names = []
    players = {}

    with open(filename, mode='r', encoding='utf-8') as contacts_file:
        # Iterate over the lines of the file and split each one by a whitespace
        for contact in contacts_file:
            name, email = contact.split()

            # Store the data
            names.append(name)
            players[name] = email

    return names, players


# Function to read a template file and return a template object made from its contents
def read_template(filename):
    with open(filename, mode='r', encoding='utf8') as template_file:
        template_file_content = template_file.read()

    return Template(template_file_content)


# Setting up the SMTP server
def smtp_setup(SMTP_SERVER, EMAIL, PASS):
    s = smtplib.SMTP(host=SMTP_SERVER, port='587')
    s.starttls()
    s.login(EMAIL, PASS)

    return s


# Write the message
def write_send_messages(players, result, subject, smtp):
    message_template = read_template(MESSAGE_TEMPLATE_FILE)

    # Write and send the messages
    for buyer, receiver in result.items():
        # Cretae a message
        msg = MIMEMultipart()

        # Person name for the message template
        message = message_template.substitute(PERSON_BUYING_GIFT=buyer, PERSON_RECEIVING_GIFT=receiver)

        # Set up the parameters of the message
        msg['From'] = players.get(receiver)
        msg['To'] = players.get(buyer)
        msg['Subject'] = subject

        # Message body
        msg.attach(MIMEText(message, 'plain'))
        
        # Send the message via the server
        smtp.send_message(msg)

        del msg


# Function that shuffles the players and assigns secret santas
def shuffle_players(names):
    return {names[i]:names[(i+1) % len(names)] for i in range(len(names))}


def main():
    # Get JSON information
    SMTP_SERVER, EMAIL, PASS = parse_json(CREDENTIALS)

    # Setting up the SMTP server
    smtp = smtp_setup(SMTP_SERVER, EMAIL, PASS)

    # Obtain names and emails
    names, players = get_contacts(CONTACTS)

    # Shuffle players
    result = shuffle_players(names)

    print(result)

    # Write and send the messages
    write_send_messages(players, result, MESSAGE_SUBJECT, smtp)

    # Terminate the SMTP connection and close it
    smtp.quit()

    print("Secret Santas has been sent. Good luck!")


if __name__ == '__main__':
    main()
