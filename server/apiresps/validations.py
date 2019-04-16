# coding=utf-8
from __future__ import absolute_import

import re
from sys import getsizeof
from bson import ObjectId

from .errors import ValidationError


class ValidationParameterInvalid(ValidationError):
    response_code = 200001
    status_message = 'PARAMETER_INVALID'


class ValidationParameterBlank(ValidationError):
    response_code = 200002
    status_message = 'PARAMETER_MUST_NOT_BE_BLANK'


class ValidationParameterMaxLimit(ValidationError):
    response_code = 200003
    status_message = 'PARAMETER_REACHES_THE_MAX_LENGTH'


class ValidationParameterMinLimit(ValidationError):
    response_code = 200004
    status_message = 'PARAMETER_REACHES_THE_MIN_LENGTH'


class ValidationParameterInvalidObjectType(ValidationError):
    response_code = 200006
    status_message = 'INVALID_OBJECT_TYPE'


class ValidationParameterValueMin(ValidationError):
    response_code = 200008
    status_message = 'PARAMETER_VALUE_TOO_SMALL'


class ValidationParameterValueMax(ValidationError):
    response_code = 200009
    status_message = 'PARAMETER_VALUE_TOO_LARGE'


class ValidationParameterSize(ValidationError):
    response_code = 200010
    status_message = 'PARAMETER_SIZE_TOO_LARGE'


class ParamStructure(object):
    name = None
    value_type = None
    non_empty = True
    len_min = None
    len_max = None
    value_min = None
    value_max = None
    sizeof = 1024 * 120

    def __init__(self, value, name=None, non_empty=None):
        self.value = value
        if name is not None:
            self.name = name
        if non_empty is not None:
            self.non_empty = bool(non_empty)
        self._validate()
        return

    def _validate(self):
        if self.non_empty is True:
            self._validate_non_empty()
        elif not self.value and self.value not in [0, False]:
            return

        if self.value_type is not None:
            self._validate_type()

        self.value = self.pre_handler()

        if self.len_min is not None:
            self._validate_len_min()

        if self.len_max is not None:
            self._validate_len_max()

        if self.value_min is not None:
            self._validate_value_min()

        if self.value_max is not None:
            self._validate_value_max()

        if self.sizeof is not None:
            self._validate_sizeof()

        if self.validator() is False:
            raise ValidationParameterInvalid(self.name)

        return

    def _validate_type(self):
        if not isinstance(self.value, self.value_type):
            raise ValidationParameterInvalidObjectType(self.name)

    def _validate_non_empty(self):
        if not bool(self.value) and self.value not in [0, False]:
            raise ValidationParameterBlank(self.name)

    def _validate_len_min(self):
        if len(self.value) < self.len_min:
            raise ValidationParameterMinLimit(self.name)

    def _validate_len_max(self):
        if len(self.value) > self.len_max:
            raise ValidationParameterMaxLimit(self.name)

    def _validate_value_min(self):
        if self.value < self.value_min:
            raise ValidationParameterValueMin(self.name)

    def _validate_value_max(self):
        if self.value > self.value_max:
            raise ValidationParameterValueMax(self.name)

    def _validate_sizeof(self):
        if getsizeof(self.value) > self.sizeof:
            raise ValidationParameterSize(self.name)

    def validator(self):
        pass

    def pre_handler(self):
        return self.value


# Parameter structure preset
class ObjectIdStructure(ParamStructure):
    def validator(self):
        return self.value and ObjectId.is_valid(self.value)


class DateStructure(ParamStructure):
    len_max = 12
    value_type = unicode

    def validator(self):
        try:
            matched = re.match(r'^\d{4}-\d{2}-\d{2}$', self.value)
        except Exception:
            matched = False
        return self.value and bool(matched)


class CodeStructure(ParamStructure):
    len_max = 600
    value_type = basestring


class SidStructure(ParamStructure):
    len_max = 600
    value_type = basestring


class MD5Structure(ParamStructure):
    len_max = 32
    value_type = basestring


class TokenStructure(ParamStructure):
    len_max = 600
    value_type = basestring


class AttrStructure(ParamStructure):
    len_max = 120
    value_type = unicode


class DescStructure(ParamStructure):
    len_max = 600
    value_type = unicode


class TextStructure(ParamStructure):
    len_max = 60000
    value_type = unicode


class DictStructure(ParamStructure):
    sizeof = 1024 * 12
    value_type = dict


class DevDictStructure(DictStructure):
    sizeof = None


class ListStructure(ParamStructure):
    sizeof = 1024 * 12
    value_type = list


class DevListStructure(ListStructure):
    sizeof = None


class FilenameStructure(ParamStructure):
    len_max = 240
    value_type = None


class FileStructure(ParamStructure):
    value_type = None


class IntegerStructure(ParamStructure):
    value_type = int


class BoolStructure(ParamStructure):
    value_type = bool


class UrlStructure(ParamStructure):
    len_max = 600
    value_type = unicode


class ProtocolStructure(ParamStructure):
    len_max = 12
    value_type = unicode


class DomainStructure(ParamStructure):
    len_max = 100
    value_type = unicode


class EmailStructure(ParamStructure):
    len_max = 120
    value_type = unicode

    def validator(self):
        return self.value and '@' in self.value


class FlagBitStructure(ParamStructure):
    value_min = 0
    value_max = 100
    value_type = int


class LoginStructure(ParamStructure):
    len_max = 120
    value_type = unicode


class PasswordStructure(ParamStructure):
    len_max = 60
    value_type = unicode


# structure object
class Struct(object):

    Pwd = PasswordStructure
    Login = LoginStructure
    Email = EmailStructure
    Domain = DomainStructure
    Protocol = ProtocolStructure
    Url = UrlStructure
    Text = TextStructure
    Desc = DescStructure
    Attr = AttrStructure
    Date = DateStructure
    Token = TokenStructure
    Sid = SidStructure
    Code = CodeStructure
    MD5 = MD5Structure
    ObjectId = ObjectIdStructure

    Dict = DictStructure
    dDict = DevDictStructure
    List = ListStructure
    dList = DevListStructure
    Bool = BoolStructure
    Flag = FlagBitStructure
    Int = IntegerStructure

    File = FileStructure
    Filename = FilenameStructure

    @staticmethod
    def OR(*structs):
        def _validate(value, name, non_empty):
            curr_except = None
            for struct in structs:
                try:
                    struct(value, name, non_empty)
                    return True
                except Exception as e:
                    curr_except = e
            if curr_except:
                raise curr_except
            return True
        return _validate
