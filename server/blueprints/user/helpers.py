# coding=utf-8
from __future__ import absolute_import

from flask import current_app
from jinja2 import Template

from mail_context import (RegisterMail, RecoveryMail)

from .errors import (UserNotFound,
                     UserNotActivated,
                     UserBlocked,
                     UserSendMailError,
                     UserCreateMailError,
                     AssistantNotFound,
                     AssistantOccupied,
                     AssistantReachedLimit)


def helper_get_user_by_login(login):
    User = current_app.mongodb.User
    user = User.find_one_by_login(login.lower())
    if user is None:
        raise UserNotFound
    elif user['status'] == User.STATUS_BANNED:
        raise UserBlocked
    elif user['status'] != User.STATUS_ACTIVATED:
        raise UserNotActivated
    return user


def helper_send_register_email(login, captcha, expires_in, locale):
    recipients = [login]
    reg_matter = RegisterMail(locale)
    template = reg_matter.output().get('template')
    subject = reg_matter.output().get('subject')

    context = {
        'captcha': captcha or '',
        'expires_in': expires_in or 0,
        'login': login
    }

    try:
        content = Template(template).render(**context)
    except Exception as e:
        raise UserCreateMailError(str(e))

    # send mail
    _send_mail(recipients, subject, content)
    return


def helper_send_recovery_email(user, captcha, expires_in, locale):
    recipients = [user['login']]
    rec_matter = RecoveryMail(locale)
    template = rec_matter.output().get('template')
    subject = rec_matter.output().get('subject')

    context = {
        'captcha': captcha or '',
        'expires_in': expires_in or 0,
        'meta': user['meta'],
        'login': user['login']
    }

    try:
        content = Template(template).render(**context)
    except Exception as e:
        raise UserCreateMailError(str(e))

    # send mail
    _send_mail(recipients, subject, content)
    return


def _send_mail(recipients, subject, content):
    # send mail
    if not current_app.config.get('SEND_MAIL'):
        return
    try:
        current_app.mail_sender.send(recipients, subject, content)
    except Exception as e:
        current_app.logger.warn(UserSendMailError(e))
        raise UserSendMailError(str(e))
    return True


# assistant
def helper_get_assistant(user_id, ass_id):
    assistant = current_app.mongodb.\
        Assistant.find_one_by_uid_id(user_id, ass_id)
    if not assistant:
        raise AssistantNotFound
    return assistant


def helper_check_assistant_passcode(user_id, passcode, assistant=None):
    if assistant and assistant['passcode'] == passcode:
        return True
    Assistant = current_app.mongodb.Assistant
    if Assistant.find_one_by_uid_passcode(user_id, passcode):
        raise AssistantOccupied
    return True


def helper_check_assistant_storage(user_id):
    Assistant = current_app.mongodb.Assistant
    if Assistant.count_used(user_id) >= Assistant.MAX_STORAGE:
        raise AssistantReachedLimit
    return True
