class Line:
    def __init__(
        self,
        name=None,
        full_line=None,
        tz_name=None,
        line_number=None,
        cron_expression=None,
        command_to_run=None,
        code=None,
        run_as=None,
        mon=None,
    ):
        self.tz_name = tz_name
        self.name = name
        self.full_line = full_line
        self.line_number = line_number
        self.cron_expression = cron_expression
        self.command_to_run = command_to_run
        self.code = code
        self.run_as = run_as
        self.mon = mon

    def __str__(self):
        return (
            f"Name: {self.name}\n"
            f"Full Line: {self.full_line}\n"
            f"Line Number: {self.line_number}\n"
            f"Cron Expression: {self.cron_expression}\n"
            f"Command to Run: {self.command_to_run}\n"
            f"Code: {self.code}\n"
            f"Run As: {self.run_as}\n"
            f"Monitor: {self.mon}\n"
        )
