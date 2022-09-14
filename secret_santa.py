import smtplib
from string import Template
import json
import random
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


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
        for contact in contacts_file:
            name = contact.split()[0]
            email = contact.split()[1]

            names.append(name)
            players[name] = email

    return names, players


# Function to read a template file and return a template object made from its contents
def read_template(filename):
    with open(filename, mode='r', encoding='utf8') as template_file:
        template_file_conten = template_file.read()

    return Template(template_file_conten)


# Setting up the SMTP server
def smtp_setup(SMTP_SERVER, EMAIL, PASS):
    s = smtplib.SMTP(host=SMTP_SERVER, port='587')
    s.starttls()
    s.login(EMAIL, PASS)

    return s


# Write the message
def write_send_messages(players, result, subject, s):
    message_template = read_template('message.txt')

    # Write and send the messages
    for sender, receiver in result.items():
        # Cretae a message
        msg = MIMEMultipart()

        # Person name for the message template
        message = message_template.substitute(SENDER=sender, RECEIVER=receiver)

        # Set up the parameters of the message
        msg['From'] = players.get(sender)
        msg['To'] = players.get(receiver)
        msg['Subject'] = subject

        # Message body
        msg.attach(MIMEText(message, 'plain'))
        
        # Send the message via the server
        s.send_message(msg)

        del msg


# Function that shuffles the players and assigns secret santas
def shuffle_players(names):
    result = {}
    receivers = []

    for name in names:
        # Get random receiver from the list (different from the sender) and insert it in the results dictionary
        receiver = random.choice([n for n in names if n != name and n not in receivers])
        result[name] = receiver

        # Mark the name as used, so every person receives one present
        receivers.append(receiver)

    return result


def main():
    # Get JSON information
    SMTP_SERVER, EMAIL, PASS = parse_json('credentials.json')

    # Setting up the SMTP server
    s = smtp_setup(SMTP_SERVER, EMAIL, PASS)

    # Obtain names and emails
    names, players = get_contacts('emails.txt')

    # Shuffle players
    result = shuffle_players(names)

    # Write and send the messages
    write_send_messages(players, result, 'Secret Santa', s)

    # Terminate the SMTP connection and close it
    s.quit()

    print("Secret Santas has been sent. Good luck!")


if __name__ == '__main__':
    main()
