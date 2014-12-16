import os
summary_log = "run_summary.log"


def emphasis(str):
    size = 60;  # should be divisable by 2
    caption_pos = size / 2 - len(str) / 2
    border = ""
    caption_line = ""

    for x in range(size):
        border += "*"
    for x in range(caption_pos):
        caption_line += '*'
    caption_line += str
    while len(caption_line) < size:
        caption_line += '*'

    return "%s\n%s\n%s\n" % (border, caption_line, border)

def log(line):
    print emphasis(line)
    with open(summary_log, "a") as myfile:
        myfile.write('%s\n' % line)


def clear_log():
    if os.path.exists(summary_log):
        os.remove(summary_log)

