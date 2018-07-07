class Validatable:
    def validate(self, instance, raise_exception=True):
        return self.validate_value(
            self.fget(instance),
            raise_exception,
            instance)

    def preprocess_value_for_validator(self, value):
        return value

    def validate_value(self, value, raise_exception=False, instance='unknown'):
        """
        Given a value (not an instance), run the appropriate validators on it.
        """
        if self.validator is None:
            return True
        if not self.validator(self.preprocess_value_for_validator(value)):
            message = \
                'Field "%s" failed validation (value "%s", instance %s)' % (
                    self.field_name if hasattr(self, 'field_name') else self,
                    value,
                    instance)
            if not raise_exception:
                return False
            raise ValueError(message)
        return True
