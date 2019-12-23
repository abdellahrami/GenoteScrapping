import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup as bs
import requests
import winsound
import time
import email
import smtplib
import getpass


usrname_genote = input('Genote username : ')
pswd_genote = getpass.getpass('Genote password :')

hotmail_email = input('hotmail : ')
hotmail_password = getpass.getpass('hotmail password : ')
mail_cible = input('mail cible : ')
s = smtplib.SMTP("smtp.live.com", 587)
# Hostname to send for this command defaults to the fully qualified domain name of the local host.
s.ehlo()
s.starttls()  # Puts connection to SMTP server in TLS mode
s.ehlo()
while True:
    try:
        s.login(hotmail_email, hotmail_password)
        break
    except:
        print("password of email is incorrect, please retry")
        hotmail_email = input('hotmail : ')
        hotmail_password = getpass.getpass('hotmail password : ')
s.quit()


with requests.Session() as s:
    home_page = s.get(
        'https://www.usherbrooke.ca/genote/application/etudiant/cours.php')
    if(str(home_page.content).count("coursetudiant") == 0):
        bs_content = bs(home_page.content, "html.parser")
        lt_token = bs_content.find("input", {"name": "lt"})["value"]
        exec_token = bs_content.find("input", {"name": "execution"})["value"]
        login_data = {"username": usrname_genote, "password": pswd_genote, "lt": lt_token,
                      "execution": exec_token, "_eventId": "submit", "submit": ""}
        s.post("https://cas.usherbrooke.ca/login?service=https%3A%2F%2Fwww.usherbrooke.ca%2Fgenote%2Fpublic%2Findex.php", login_data)
        print("Authentification was required")
    # print(table)
    # new_table = pd.DataFrame(columns=range(0,5)) # I know the size
    nb_evals_old = None
    minutes = 0
    while True:
        home_page = s.get(
                "https://www.usherbrooke.ca/genote/application/etudiant/cours.php")
        page_content = bs(home_page.content, "lxml")
        table = page_content.find_all('tbody')[0]
        nb_evals_total = 0
        for row in table.find_all('tr'):
            column_marker = 0
            columns = row.find_all('td')
            for column in columns:
                if(column_marker == 4):
                    nb_evals_total += int(column.get_text())
                column_marker += 1
        if nb_evals_old == None:
            nb_evals_old = nb_evals_total
            print( "nbr_evals est de : ",nb_evals_old)
        if nb_evals_total != nb_evals_old:
            frequency = 2500  # Set Frequency To 2500 Hertz
            duration = 1000  # Set Duration To 1000 ms == 1 second
            winsound.Beep(frequency, duration)
            print("NB_Evals a changé !!!!!!!!!")
            msg = email.message_from_string('Il y a eu un changement sur votre espace GeNote')
            msg['From'] = hotmail_email
            msg['To'] = mail_cible
            msg['Subject'] = "Genote à changé"

            s = smtplib.SMTP("smtp.live.com", 587)
            # Hostname to send for this command defaults to the fully qualified domain name of the local host.
            s.ehlo()
            s.starttls()  # Puts connection to SMTP server in TLS mode
            s.ehlo()
            s.login(hotmail_email, hotmail_password)

            s.sendmail(hotmail_email,
                       mail_cible, msg.as_string())

            s.quit()
        time.sleep(30)
        minutes += 0.5
        if( minutes%10 == 0 ):
            print("nbr_evals est de : ", nb_evals_old)


