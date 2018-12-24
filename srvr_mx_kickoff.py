#-------------------------------------------------------------------------------
# Name:        Pre-Database Sync & Publiction Script Run
# Purpose:  This scripts is designed to run and pull connections data connections
#           used to prepare the database for updates prior to syncing.  The script
#           id's who is attached to the database, e-mails them that there is a 15
#           minute window before maintenance is to begin.  Stop new connections
#           from being made and eventually killing all connections to the database.
#           At some point in the future the script will allow for different flows.
#
# Author:      John Spence, Spatial Data Administrator, City of Bellevue
#
# Created:     6/5/2018
# Modified:
# Modification Purpose:
#
#
#-------------------------------------------------------------------------------

# 888888888888888888888888888888888888888888888888888888888888888888888888888888
# ------------------------------- Configuration --------------------------------
# Pretty simple setup.  Just change your settings/configuration below.  Do not
# go below the "DO NOT UPDATE...." line.
#
#
# 888888888888888888888888888888888888888888888888888888888888888888888888888888

# Configure only hard coded db connection here.
db_connection = r'Database Connections\\Connection to WebGIS.sde'

# Configure Database Name Here.
db_name = 'WebGIS'

# Configure Database Type Here (Production, Staging, Test).
db_type = 'Test'

# Configure the e-mail server and other info here.
mail_server = 'smtprelay.domain.gov'
mail_from = 'GIS DBA <gisdba@domain.gov>'

# ------------------------------------------------------------------------------
# DO NOT UPDATE BELOW THIS LINE OR RISK DOOM AND DISPAIR!  Have a nice day!
# ------------------------------------------------------------------------------

# Import Python libraries
import arcpy, time, smtplib, string, re

# List Users in Database
arcpy.env.workspace = db_connection
db_connection = arcpy.env.workspace

userList = arcpy.ListUsers(db_connection)

# Form User Account Listing
emaillist = [user.Name for user in arcpy.ListUsers(db_connection)]
emaillist = [i for i in set(emaillist)]

# Count users in array
listcount = len(emaillist)

# Set how many e-mails have been sent
emailed_count = 0
sent_msg = 0

# Begin Individual E-mail Delivery Process
# Check count against array.  If <= continue.  Else, end.
if emailed_count <= listcount:
    for emailed_count in range(listcount):

        # Set SMTP Server.
        server = smtplib.SMTP(mail_server)

        # Begin array data draw
        # Set e-mail_id -1 as arrays start at 0 and count upwards.  +1 is added later to cycle.

        email_id = emailed_count-1
        email_target = emaillist[email_id]

        #Process string and remove garbage that will malform e-mail address.
        email_target = string.replace(email_target, '"', '')
        email_target = string.replace(email_target, 'DOMAIN\\', '')


        email_target_avoid = [email_target<>'DBO', email_target<>'!mainangmentaccount', email_target<>'named_schema']
        if all(email_target_avoid):
            email_target = email_target + '@domain.gov'
            mail_priority = '2'
            # Double commented out code hides how to send a BCC as well.
            mail_subject = 'WARNING:  Database Maintenance Pending For ' + db_name + ' on ' + db_type
            mail_msg = ('Database server maintenance will be performed in 15 minutes ' + db_name + ' on ' + db_type +
            '! Please save your work and close any ArcGIS or ArcCatalog sessions you may have open.\n\n[SYSTEM AUTO GENERATED MESSAGE]')

            print email_target

            send_mail = 'To: {0}\nFrom: {1}\nX-Priority: {2}\nSubject: {3}\n\n{4}'.format(email_target, mail_from, mail_priority, mail_subject, mail_msg)
            # Double commented out code hides how to send a BCC as well.
            ##send_mail = 'To: {0}\nFrom: {1}\nBCC: {2}\nX-Priority: {3}\nSubject: {4}\n\n{5}'.format(email_target, mail_from, mail_bcc, mail_priority, mail_subject, mail_msg)

            print "Sending message to user."

            server.sendmail(mail_from, email_target, send_mail)
            # Double commented out code hides how to send a BCC as well.
            ##server.sendmail(mail_from, [email_target, mail_bcc], send_mail)
            server.quit()
            sent_msg = sent_msg+1


        emailed_count = emailed_count+1

# Pause for existing warned Users only if e-mail sent.
if sent_msg > 0:

    print 'Notified {0} users about upcoming maintenance.\nStarting 15 minute pause.'.format(sent_msg)
    time.sleep(900)
    print 'Resuming maintenance after 15 minute warning.'

    # Refuse new connections to database.
    print 'Refusing new connections'
    arcpy.AcceptConnections(db_connection, False)

else:
    print 'Refusing new connections'
    arcpy.AcceptConnections(db_connection, False)

# Disconnect all users from database.
print 'Disconnecting all users'
arcpy.DisconnectUser(db_connection, "ALL")

# Enable for testing mode only.
### Allow new connections to start database data sync processing
##print 'Allowing new connections'
##arcpy.AcceptConnections(db_connection, True)



