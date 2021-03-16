class Lesson:
    def __init__(self, number: int, start_time: str, end_time: str, classroom: str, title: str,
                 is_remote: bool = False) -> None:
        self.number = number
        self.start_time = start_time
        self.end_time = end_time
        self.classroom = classroom
        self.title = title
        self.is_remote = is_remote

    def __str__(self):
        return f"{self.number} | {self.start_time} - {self.end_time} | {self.classroom:6} | {self.title}"
