import a
from flask import render_template
from . import mixins


message_types = {
    'validate_email':0, # sending to person to validate their email address
    'new_user':1, # sending to admin to notify of a new user
    }

class EmailValidation(a.db.Model, mixins.BaseModelMixin):
    id = a.db.Column(a.db.Integer, primary_key=True)
    email = a.db.Column(a.db.Text)
    code = a.db.Column(a.db.String(20), index=True)
    is_validated = a.db.Column(a.db.Boolean, default=False)
    is_deleted = a.db.Column(a.db.Boolean, default=False)
    user_id = a.db.Column(a.db.Integer, a.db.ForeignKey('user.id'), index=True)

    @a.utils.sql.commit_decorator
    def validate(self):
        self.is_validated = True
        self.user.is_email_validated = True

    def get_validation_info(self):
        if self.is_validated:
            return None, "This code was already validated."
        elif self.is_deleted:
            return None, "This code is invalid."
        elif not self.user:
            return None, "This user is invalid."
        return self.user, "Success!"


#######
# EmailTemplate is an object (not in the db) holding the different templates
#######

class EmailTemplate(object):
    @staticmethod
    def get_message_type_value(message_type):
        """
        Given the message_type, this gets the numeric value associated with it
        """
        if type(message_type) is str:
            message_type_value = message_types.get(message_type)
            if message_type_value:
                return message_type_value
        elif type(message_type) is int and message_type in message_types.values():
            return message_type
        return None

    @staticmethod
    def get_message_type_key(message_type):
        """
        Given the message_type, this gets the string key associated with it
        """
        if type(message_type) is str and message_type in message_types:
            return message_type
        elif type(message_type) is int:
            for k,v in message_types.iteritems():
                if v == message_type:
                    return k
        return None

    def render(self, message_type, **kwargs):
        """
        message_type wants to be a string like '_validate_email_template',
        but can be the numeric value.
        """
        message_type_key = self.get_message_type_key(message_type)
        if not message_type_key:
            return None

        template = getattr(self, '_'.join(['', message_type_key, 'template']))()
        return render_template(template, **kwargs)

    @staticmethod
    def _validate_email_template():
        return 'email/validate_email.html'

    @staticmethod
    def _new_user_template():
        return 'email/new_user.html'

