class Validatable:
    def validate(self, instance, raise_exception=True):
        return self.validate_value(
            self.get(instance),
            raise_exception,
            instance)

    def validate_value(self, value, raise_exception=False, instance='unknown'):
        """
        Given a value (not an instance), run the appropriate validators on it.
        """
        if value is None or (
                self.validator is not None and not self.validator(value)):
            message = \
                'Field "%s" failed validation (value "%s", instance %s)' % (
                    self.field_name if hasattr(self, 'field_name') else self,
                    value,
                    instance)
            if not raise_exception:
                return False
            raise ValueError(message)
        return True
