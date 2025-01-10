import json
from wagov_utils.components.utils.email import (
    TemplateEmailBase as WAGovUtilsTemplateEmailBase,
)
from sss.models import SpatialDataCalculation

def get_tasks_progress(spatialData):
    status_mapping = {
        -1: "Failed",
        -2: "Fail Confirmed",
        1: "Waiting",
        2: "Running",
        3: "Succeed",
        4: "Warning",
        5: "Ignored",
        6: "Merged"
    }
    tasks_list = []
    
    spatial_data = json.loads(spatialData.tasks)
    
    for task in spatial_data:
        if task['taskId'] == 'tenure_area':
            task_description = task['description']
            if spatialData.calculation_status == SpatialDataCalculation.CALCULATION_STATUS[2][0] or spatialData.calculation_status == SpatialDataCalculation.CALCULATION_STATUS[4][0]:
                task_message = ''
                task_status = 'Succeed'
            else:
                task_message = spatialData.error
                task_status = 'Failed'
            tasks_list.append({'description': task_description, 'status': task_status, 'message': task_message})
        else:
            task_description = task['description']
            task_status = status_mapping[task['status']]
            task_message = task['message']
            tasks_list.append({'description': task_description, 'status': task_status, 'message': task_message})
    return tasks_list


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
    tasks_list = json.loads(spatialData.tasks)
    tasks_list = get_tasks_progress(spatialData)
    context = {
        'first_name': spatialData.user.first_name, 
        'bfrs': spatialData.bfrs,
        'uploaded_date': spatialData.created,
        'tasks': tasks_list,
    }
    msg = email.send([spatialData.user.email], context=context)

    
class SpatialCalculationFailureEmail(TemplateEmailBase):
    subject = 'Spatial Calculation Failed'
    html_template = 'emails/failure_email.html'
    txt_template = 'emails/failure_email.txt'

def send_failure_email(spatialData):

    email = SpatialCalculationFailureEmail()
    email.subject = f'Spatial Calculation Failed {spatialData.bfrs}'
    tasks_list = get_tasks_progress(spatialData)
    context = {
        'first_name': spatialData.user.first_name, 
        'bfrs': spatialData.bfrs,
        'uploaded_date': spatialData.created,
        'tasks': tasks_list,
    }
    msg = email.send([spatialData.user.email], context=context)