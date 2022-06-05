class CustomException:
    RED_COLOR = '\033[1;31m'

    __slots__ = 'message', 'exit_code'

    def __init__(self, message='Runtime Error', exit_code=1):
        self.message = message
        self.exit_code = exit_code

    def __call__(self, *args, **kwargs):
        by_hands = self.exit_code == 2
        is_invalid = '' if by_hands else 'invalid operation.'
        return f'{self.RED_COLOR}{is_invalid} {self.message}. finished with code {self.exit_code}'


def custom_raise(exception: CustomException):
    print(exception())
    exit(exception.exit_code)
