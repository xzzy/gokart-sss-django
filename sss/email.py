from wagov_utils.components.utils.email import (
    TemplateEmailBase as WAGovUtilsTemplateEmailBase,
)


class TemplateEmailBase(WAGovUtilsTemplateEmailBase):
    subject = ""
    html_template = "emails/base_email.html"
    # txt_template can be None, in this case a 'tag-stripped' version of the html will be sent. (see send)
    txt_template = "emails/base_email.txt"

    def send_to_user(self, users, context=None):
        filtered_emails = {u.email for u in users if hasattr(u, "email")}
        # Loop through users
        print("filtered email")
        for email in filtered_emails:
            # Send the email!
            self.send(email, context=context)

class SpatialCalculationSuccessEmail(TemplateEmailBase):
    subject = 'Spatial Calculation Completed'
    html_template = 'emails/success_email.html'
    txt_template = 'emails/success_email.txt'

def send_success_email(spatialData):

    email = SpatialCalculationSuccessEmail()
    email.subject = f'Spatial Calculation Completed {spatialData.bfrs}'
    context = {
        'first_name': spatialData.user.first_name, 
        'bfrs': spatialData.bfrs,
        'uploaded_date': spatialData.created
    }
    msg = email.send([spatialData.user.email], context=context)

    
class SpatialCalculationFailureEmail(TemplateEmailBase):
    subject = 'Spatial Calculation Failed'
    html_template = 'emails/failure_email.html'
    txt_template = 'emails/failure_email.txt'

def send_failure_email(spatialData):

    email = SpatialCalculationFailureEmail()
    email.subject = f'Spatial Calculation Failed {spatialData.bfrs}'
    context = {
        'first_name': spatialData.user.first_name, 
        'bfrs': spatialData.bfrs,
        'uploaded_date': spatialData.created,
        'error': spatialData.error
    }
    msg = email.send([spatialData.user.email], context=context)