import os
import pymsteams


# Function to read last N lines of the file 
# https://www.geeksforgeeks.org/python-reading-last-n-lines-of-a-file/
def last_n_lines(fname, N):
    # opening file using with() method
    # so that file get closed
    # after completing work
    lines = ""
    with open(fname) as file:
         
        # loop to read iterate 
        # last n lines and print it
        for line in (file.readlines() [-N:]):
            lines += line + "\n"

    return lines


# You must create the connectorcard object with the Microsoft Webhook URL
ms_teams_webhook_url = "{{ MS_TEAMS_WEBHOOK_URL }}"
myTeamsMessage = pymsteams.connectorcard(ms_teams_webhook_url)

# Color Theme
myTeamsMessage.color("CCE2EA")

# Add a title
myTeamsMessage.title("System Error: Backing Up Logs to S3 Failed.")
myTeamsMessage.text(
    "We had an issue backing up logs to S3 after logrotate. Please check production to " \
    "make sure that the 'logrotate-s3' service is running properly."
    )

# Error from logfile
myMessageSectionError = pymsteams.cardsection()
myMessageSectionError.title("Log Output for {{ S3_AWS_LOGFILE }}")
myMessageSectionError.text(
    last_n_lines("{{ S3_AWS_LOGFILE }}", {{ MS_TEAMS_ERROR_LINES }})
)
myTeamsMessage.addSection(myMessageSectionError)

# Create EC2 section
myMessageSectionEC2 = pymsteams.cardsection()
myMessageSectionEC2.title("EC2 Instance")
myMessageSectionEC2.addFact("Instance Id:", str(os.environ.get('AWS_INSTANCE_ID')))
myMessageSectionEC2.addFact("Private IPv4:", str(os.environ.get('AWS_LOCAL_IPV4')))
myMessageSectionEC2.addFact("Region:", str(os.environ.get('AWS_REGION')))
myTeamsMessage.addSection(myMessageSectionEC2)

# Create S3 section
myMessageSectionS3 = pymsteams.cardsection()
myMessageSectionS3.title("S3 Service")
myMessageSectionS3.addFact("Bucket Name:", "{{ S3_UTILS_S3CMD_BUCKET }}")
myMessageSectionS3.addFact("Bucket Location:", "{{ S3_UTILS_S3CMD_BUCKET_LOCATION }}")
myTeamsMessage.addSection(myMessageSectionS3)

# send the message.
myTeamsMessage.send()
