#Imports
import smtplib

from string import Template

import json

import random

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#Function to read the credentials file
def parse_json(filename):
    with open(filename, mode='r') as json_file:
        data = json.load(json_file)
        SMTP_SERVER = data['SMTPserver']
        EMAIL = data['email']
        PASS = data['pass']

    return SMTP_SERVER, EMAIL, PASS

#Function to read the emails from a file
def get_contacts(filename):
    names = []
    players = {}

    with open(filename, mode='r', encoding='utf-8') as contacts_file:
        for contact in contacts_file:
            names.append(contact.split()[0])
            players[contact.split()[0]] = contact.split()[1]

    return names, players

#Function to read a template file and return a template object made from its contents
def read_template(filename):
    with open(filename, mode='r', encoding='utf8') as template_file:
        template_file_conten = template_file.read()

    return Template(template_file_conten)

#Setting up the SMTP server
def smtp_setup(SMTP_SERVER, EMAIL, PASS):
    s = smtplib.SMTP(host=SMTP_SERVER, port='587')
    s.starttls()
    s.login(EMAIL, PASS)

    return s

#Write the message
def write_messages(players, result, EMAIL, s):
    message_template = read_template('message.txt')
    r_keys = list(result.keys())
    r_values = list(result.values())

    for rk, rv in zip(r_keys, r_values):
        #Cretae a message
        msg = MIMEMultipart()

        #Person name for the message template
        message = message_template.substitute(RECEIVER = rk.title(), SENDER = rv.title())

        #Setup the parameters of the message
        msg['From'] = players.get(rk)
        msg['To'] = players.get(rv)
        msg['Subject'] = 'Prueba Amigo Invisible Save The Polar Beers 2020'

        #Message body
        msg.attach(MIMEText(message, 'plain'))
        
        #Send the message via the server
        s.send_message(msg)

        del msg

#Function that shuffles the players and assigns secret santas
def shuffle_players(names):
    assigned_players = dict()
    sender_taken_names = names.copy()
    receiver_taken_names = names.copy()
    n = 0

    while n < len(names):
        sender = random.choice(sender_taken_names)
        receiver = random.choice(receiver_taken_names)
        if sender in sender_taken_names and receiver in receiver_taken_names and sender != receiver:
            assigned_players[sender] = receiver
            sender_taken_names.remove(sender)
            receiver_taken_names.remove(receiver)
            n += 1
    
    return assigned_players


#############
# MAIN CODE #
#############

def main():
    #Get JSON information
    SMTP_SERVER, EMAIL, PASS = parse_json('credentials.json')

    #Setting up the SMTP server
    s = smtp_setup(SMTP_SERVER, EMAIL, PASS)

    #Read contact
    names, players = get_contacts('emails.txt')

    result = shuffle_players(names)

    #Write and send the messages
    write_messages(players, result, EMAIL, s)

    #Terminate the SMTP connection and close it
    s.quit()

    print("Secret Santas has been sent. Good luck!")

if __name__ == '__main__':
    main()
