from django.core import mail
from django.core.mail import EmailMessage
from django.template.loader import get_template

class Mailer:
    """
    Send email messages helper class
    """
    def __init__(self, from_email='admin102@gmail.com'): # source email address
        # setup the default from email
        self.connection = mail.get_connection()  # initial set_up
        self.from_email = from_email # from_mail

    def send_messages(self, subject, template, context, to_emails):
        messages = self.__generate_messages(subject, template, context, to_emails)
        self.__send_mail(messages)

    def __send_mail(self, mail_messages):
        """
        Send email messages
        """
        self.connection.open() #connection open
        self.connection.send_messages(mail_messages) # send messages
        self.connection.close() # close connection

    def __generate_messages(self, subject, template, context, to_emails):
        """
        Generate email message from Django template
        """
        messages = [] 
        message_template = get_template(template)
        for recipient in to_emails:
            message_content = message_template.render(context)
            message = EmailMessage(subject, message_content, to=[recipient], from_email=self.from_email)
            message.content_subtype = 'html'
            messages.append(message)

        return messages  # return the message
