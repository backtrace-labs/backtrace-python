class SourceCodeHandler:
    def __init__(self, tab_width, context_line_count):
        self.tab_width = tab_width
        self.context_line_count = context_line_count
        self.line_offset = 5

    def collect(self, report):
        if not "threads" in report or not "sourceCode" in report:
            return report
        threads = report["threads"]

        if not "mainThread" in report or not report["mainThread"] in threads:
            return report

        main_thread = threads[report["mainThread"]]

        if not "stack" in main_thread:
            return report

        main_thread_stack = main_thread["stack"]

        source_code = {}

        for frame in main_thread_stack:
            new_min_line = max(frame.line - self.line_offset, 0)
            new_max_line = frame.line + self.line_offset

            if not frame["sourceCode"] in source_code:
                source_code[frame["sourceCode"]] = {
                    "minLine": new_min_line,
                    "maxLine": new_max_line,
                    "path": frame["sourceCode"],
                }
            else:
                source = source_code[frame["sourceCode"]]
                if new_min_line < source["minLine"]:
                    source["minLIne"] = new_min_line
                if new_max_line > source["maxLine"]:
                    source["maxLine"] = new_min_line

        report["sourceCode"] = source_code
        return report
