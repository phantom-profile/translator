class CustomException:
    RED_COLOR = '\033[1;31m'

    def __init__(self, exit_code, message):
        self.message = message
        self.exit_code = exit_code

    def __call__(self, *args, **kwargs):
        return f'{self.RED_COLOR}invalid operation. {self.message}. finished with code {self.exit_code}'


def custom_raise(exception: CustomException):
    print(exception())
    exit(exception.exit_code)
