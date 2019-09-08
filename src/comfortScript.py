import csv
import sys
import os
from os import path
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

url = 'https://www.w3cp2.com/njcp2/login.jsp'
csv_input = 'mailinglist.csv'
csv_output = 'output_mailinglist.csv'
current_year = int(datetime.today().year)

def doLookup(first_name, last_name, city_name, row_input, browser):
    browser.get('https://www.w3cp2.com/njcp2/doLookup.do')

    last_input = browser.find_element_by_name('lastname')
    last_input.send_keys(last_name)
    first_input = browser.find_element_by_name('firstname')
    first_input.send_keys(first_name)
    city_input = browser.find_element_by_name('zipcode')
    city_input.send_keys(city_name)
    city_input.send_keys(Keys.ENTER)

    try:
    #Applicant not found
        if browser.find_element_by_xpath('/html/body/h1').text == "No Customers/Jobs Found.":
            new_row = row_input
            new_row.insert(0,'')
            #csv_writer.writerow(new_row)
            return new_row
    #Applicant found
    except NoSuchElementException:
        app_link = browser.find_element_by_xpath('//*[@id="commontable"]/tbody/tr[3]/td[1]/a')
        browser.get(app_link.get_attribute('href'))

    #Determine year of application and status
    finish_date = browser.find_element_by_xpath('//*[@id="jobtable"]/tbody/tr[21]/td[2]').text
    cancel_date = browser.find_element_by_xpath('//*[@id="jobtable"]/tbody/tr[20]/td[2]').text
    init_date = browser.find_element_by_xpath('//*[@id="jobtable"]/tbody/tr[19]/td[2]').text

    if len(cancel_date) > 0:
        input_date = int(cancel_date[6:])
        input_string = str(input_date) + ' - cancel'

    elif len(finish_date) > 0:
        input_date = int(finish_date[6:])
        if input_date <= (current_year-5):
            input_string = str(input_date) + ' - finish'
        else:
            input_string = str(input_date) + ' - done'
    else:
        input_date = int(init_date[6:])
        input_string = str(input_date) + ' - going'

    new_row = row_input
    new_row.insert(0,input_string)
    return new_row

def split_name_njng(str):
    full_name = ['none','none']
    flag = str.find(',')
    if flag == -1:
        flag = str.find(' ')
        if flag > -1:
            full_name[0] = str[:str.find(' ')]
            full_name[1] = str[(str.find(' ')+1):]
        else:
            full_name[0] = 'none'
            full_name[1] = 'none'

    else:
        flag = str.find('&') #location of target
        if flag > -1:
            full_name[0] = str[:(str.find(','))]
            full_name[1] = str[(str.find(',')+1):flag-1]
        else:
            full_name = str.split(',')
            flag = full_name[1].find(' ')
            if flag > -1:
                full_name[1] = full_name[1][:flag]
            flag = full_name[0].find(' ')
            if flag > -1:
                if len(full_name[0][:flag]) < 2:
                    full_name[0] = full_name[0][(flag+1):]
                else:
                    full_name[0] = full_name[0][:flag]

    full_name[0].replace('0','o')
    full_name[1].replace('0','o')
    return full_name

def split_name_ace(str):
    full_name = ['none','none']
    raw_split = str.split(' ')
    flag = len(raw_split)
    if flag > 2:
        full_name[0] = raw_split[0]
        counter = 0
        for target in raw_split:
            if counter==0:
                counter+=1
                continue

            if len(target) >= 2:
                full_name[1] = target
                break;

    elif flag == 2:
        full_name[0] = raw_split[0]
        full_name[1] = raw_split[1]

    full_name[0].replace('0','o')
    full_name[1].replace('0','o')
    return full_name

def split_name_jcpl(str):
    full_name = ['none','none']
    raw_split = str.split(' ')
    flag = len(raw_split)
    if flag > 1:
        full_name[0] = raw_split[0]

    elif flag == 1:
        full_name[0] = raw_split[0]
        full_name[1] = 'none'

    full_name[0].replace('0','o')
    full_name[1].replace('0','o')
    return full_name

def split_name_pseg(str):
    full_name = ['none','none']
    raw_split = str.split(' ')
    flag = len(raw_split)
    if flag > 1:
        for name in raw_split:
            if len(name)<2:
                full_name[0]='none'
            else:
                full_name[0] = name
                break

    elif flag == 1:
        full_name[0] = raw_split[0]
        if len(full_name[0]) < 2:
            full_name[0] = 'none'
        full_name[1] = 'none'

    #full_name[0].replace('0','o')
    #full_name[1].replace('0','o')
    return full_name

def find_zip(str):
    cutup = str.split(' ')
    raw_zip = cutup[len(cutup)-1]
    return (raw_zip[:5])


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.stderr.write('Incorrect input arguments!\n')
        sys.stdout.write('\tThe correct format is:\n\tpython3 comfortScript.py <CSV file name> <Utility>\n\n')
        sys.exit()

    if path.exists(sys.argv[1]) == False:
        sys.exit('File with name \"'+sys.argv[1]+'\" does not exist\n')
    else:
        csv_input = sys.argv[1]
        csv_output = 'output_'+csv_input

    utility = sys.argv[2].lower()
    if utility == "njng" or utility == "ace" or utility == "jcpl" or utility == "pseg":
        pass
    else:
        sys.stderr.write('Incorrect utility name\n')
        sys.exit('\tPlease specify "ace", "jcpl", "njng", or "pseg" as selected utility\n\n')

    if os.name == 'nt':
        browser = webdriver.Chrome(os.getcwd()+'\chromedriver.exe')
    else:
        browser = webdriver.Chrome(os.getcwd()+'/chromedriver')
    browser.get(url)

    #Login with username and password
    try:
        user_sys = os.environ.get('COMFORT_USER')
        pass_sys = os.environ.get('COMFORT_PASS')

        user_id_bar = browser.find_element_by_name('user_id')
        user_id_bar.send_keys(user_sys)

        pass_bar = browser.find_element_by_name('pass_word')
        pass_bar.send_keys(pass_sys)
        pass_bar.send_keys(Keys.ENTER)

    except:
        print("Incorrect username and/or password\n")
        print("Please refer to the installation document to change your username/password")
        sys.exit("Installation document is located in the Comfort Partners Package\n")


    try:
        login_text = browser.find_element_by_xpath('//*[@id="bannerhome"]/tbody/tr/td[4]')
        if login_text.text.strip() == "Log In Failed":
            print("Incorrect username and/or password\n")
            print("Please refer to the installation document to change your username/password")
            sys.exit("Installation document is located in the Comfort Partners Package\n")

    except NoSuchElementException:
        pass

    #Read CSV
    firstline = True
    with open(csv_input,'r') as csv_file:
        csv_reader = csv.reader(csv_file)

        with open(csv_output,'w') as csv_out_file:
            csv_writer = csv.writer(csv_out_file)

            for row in csv_reader:
                #Check if current row is title row
                if firstline:
                    new_row = row
                    new_row.insert(0,'Status')
                    csv_writer.writerow(new_row)
                    firstline = False
                    continue

                first_name = 'none'
                last_name = 'none'
                city = '00000'
                #Get info from CSV
                if utility == "njng":
                    full_name = split_name_njng(row[1])
                    last_name = full_name[0]
                    first_name = full_name[1]
                    city = row[7].strip()
                elif utility == "ace":
                    full_name = split_name_ace(row[4])
                    last_name = full_name[1]
                    first_name = full_name[0]
                    city = find_zip(row[6])
                elif utility == "jcpl":
                    last_name = row[2]
                    first_name = split_name_jcpl(row[1])[0]
                    city = find_zip(row[4])
                elif utility == "pseg":
                    first_name=split_name_pseg(row[2].strip())[0]
                    last_name = split_name_pseg(row[3].strip())[0]
                    city = find_zip(row[10])

                new_row = doLookup(first_name, last_name, city, row, browser)
                csv_writer.writerow(new_row)
