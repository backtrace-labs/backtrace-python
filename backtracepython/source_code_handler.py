import os


class SourceCodeHandler:
    def __init__(self, tab_width, context_line_count):
        self.tab_width = tab_width
        self.context_line_count = context_line_count

    def collect(self, report):
        if not "threads" in report:
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
            new_min_line = max(frame["line"] - self.context_line_count - 1, 0)
            new_max_line = frame["line"] + self.context_line_count + 1

            if not frame["sourceCode"] in source_code:
                source_code[frame["sourceCode"]] = {
                    "startLine": new_min_line + 1,
                    "startColumn": 1,
                    "maxLine": new_max_line,
                    "path": frame["sourceCode"],
                    "tabWidth": self.tab_width,
                }
            else:
                source = source_code[frame["sourceCode"]]
                if new_min_line < source["startLine"]:
                    source["startLine"] = new_min_line + 1
                if new_max_line > source["maxLine"]:
                    source["maxLine"] = new_max_line

        for source_code_path in source_code:
            source = source_code[source_code_path]
            source_code_content = self.read_source(
                source_code_path, source["startLine"] - 1, source["maxLine"]
            )
            if source_code_content is None:
                source_code.pop(source_code_path)
                continue
            source["text"] = source_code_content
            # clean up the source code integration
            source.pop("maxLine")

        report["sourceCode"] = source_code
        return report

    def read_source(self, source_code_path, start, end):
        extension = os.path.splitext(source_code_path)[1]
        if extension == ".pyc":
            return

        file_content = self.read_file_or_none(source_code_path)
        if file_content is None:
            return

        lines = file_content.split("\n")

        max_line = min(end, len(lines))
        return "\n".join(lines[start:max_line])

    def read_file_or_none(self, file_path):
        try:
            with open(file_path) as f:
                return f.read()
        except:
            return None
