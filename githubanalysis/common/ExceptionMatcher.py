
import re
re_timestamp = r"^\s*(?:(?:\d{4}-)?\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}:?\s*)?"
re_pids_w_spaces = r"(?:\s\d{3,5}\s\d{3,5}(?:\s\d{3,5})?\s)"
re_pids_w_dashes = r"(?:\s\d{3,5}-\d{3,5}(?:-\d{3,5})?(?:/(?:\?|(?:\w+\.)+\w+))?\s)"
re_pids = r"(?:" + re_pids_w_spaces + r"|" + re_pids_w_dashes + r")?" # (?P<pids>(?:\s\d{3,5}\s\d{3,5}(?:\s\d{3,5})?\s)|(?:\s\d{3,5}-\d{3,5}(?:-\d{3,5})?/(?:\?|(?:\w+\.)+\w+)\s))?
re_log_origin = r"(?:(?:E|I|W|D)(?:\s|/)\w+(?:\(\s*\d+\))?:\s)"
re_logcat_line = re_timestamp + re_pids + re_log_origin


re_exception_class_name = r"(?:\w+\.)+\w+(?:Exception|Error)"
re_logging_error_line = r"(?:^.*(?:E/|Player)+.*(?:Error|Exception|Failed).*$\n)"

re_exception_info_message = r"^.*(?=: " + re_exception_class_name + ")|Crashed"

re_exception_line = r"(?:^.*(?:" + re_exception_class_name + r"|Crashed:).*$\n)"    # (?:^\s*(?:(?:\w+\.)+\w+(?:Exception|Error)|Crashed:).*$\n)
re_at_line_block = r"(?:(?:^\s*at (?:\w+\.)+\w+.*\(.*\)\s*$)\n)+"

re_caused_by_line = r"(?:^\s*Caused by: " + re_exception_class_name + r".*$\n)"  # (?:^\s*Caused by: (?:\w+\.)+\w+(?:Exception|Error).*$\n)

re_stack_trace = re_logging_error_line + r"?(?:" + re_exception_line + re_at_line_block + r")+"

rec_stacktrace = re.compile(re_stack_trace, re.IGNORECASE | re.MULTILINE)
rec_exception_class_name = re.compile(re_exception_class_name, re.IGNORECASE | re.MULTILINE)
rec_exception_line = re.compile(re_exception_line, re.IGNORECASE | re.MULTILINE)
rec_exception_info = re.compile(re_exception_info_message, re.IGNORECASE | re.MULTILINE)
rec_logging_error_line = re.compile(re_logging_error_line, re.IGNORECASE | re.MULTILINE)

rec_logcat_prefix = re.compile(re_logcat_line, re.IGNORECASE | re.MULTILINE)

class ExceptionMatcher:
    def __init__(self, message):
        self.message = message#.replace("\u00a0", "").replace("\r","")
        self.stack_traces = self.__find_all_traces()
        self.mentioned_exceptions = rec_exception_class_name.findall(message)

    def __find_all_traces(self):
        traces = rec_stacktrace.findall(self.message)
        if not traces or traces.count("\n"):
            traces.extend(rec_stacktrace.findall(rec_logcat_prefix.sub("", self.message)))
        return traces

    def get_all_exceptions(self):
        exceptions = []
        for stack_trace in self.stack_traces:
            exceptions.append(self.__get_exception(stack_trace))
        return exceptions

    def __get_exception(self, stack_trace):
        exception = {"logger": self.__extract_logging_error_line(stack_trace), "infos": []}
        lines = rec_exception_line.findall(stack_trace)
        for line in lines:
            exception["infos"].append(self.__extract_exception_info(line))
        return exception

    def __extract_exception_info(self, c_exception_line):
        exception_info = {"info": "", "exception": ""}
        info = rec_exception_info.search(c_exception_line)
        if info:
            exception_info["info"] = info.group().lstrip()
        class_name = rec_exception_class_name.search(c_exception_line.replace(exception_info["info"], ""))
        if class_name:
            exception_info["exception"] = class_name.group()
        return exception_info

    def __extract_logging_error_line(self, stack_trace):
        log = rec_logging_error_line.search(stack_trace)
        if (log):
            return rec_logcat_prefix.sub("", log.group().rstrip())
        else:
            return ""

    def contains_stacktrace(self):
        return self.stack_traces.__len__() > 0

    def get_pretty_list_all_mentioned_exceptions(self):
        return " ".join(self.mentioned_exceptions)

    def contains_exception_class_name(self):
        return self.mentioned_exceptions.__len__() > 0

    def get_pretty_exceptions(self):
        pretty = []
        for exception in self.get_all_exceptions():
            pretty.append("EXCEPTION")
            pretty.append(exception["logger"])
            for inf in exception["infos"]:
                pretty.append(inf["info"] + " - " + inf["exception"])
        return " | ".join(pretty).replace(",", ";")
