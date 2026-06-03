def seconds_to_time(seconds):

    hours = int(seconds // 3600)

    minutes = int((seconds % 3600) // 60)

    seconds = int(seconds % 60)

    return (
        f"{hours:02}:"
        f"{minutes:02}:"
        f"{seconds:02}"
    )