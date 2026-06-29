class Interpreter:

    def convert(self, events):

        steps = []
        buffer = ""

        for e in events:

            # -------------------
            # click -> flush buffer
            # -------------------
            if e["type"] == "click":

                if buffer:
                    steps.append({
                        "action": "type",
                        "value": buffer
                    })
                    buffer = ""

                steps.append({
                    "action": "click",
                    "x": e["x"],
                    "y": e["y"],
                    "rel_x": e.get("rel_x", 0),
                    "rel_y": e.get("rel_y", 0),
                    "window": e["window"]
                })

            # -------------------
            # merge consecutive key events
            # -------------------
            elif e["type"] == "key":

                k = e["key"]

                if k == "Key.space":
                    buffer += " "
                elif k == "Key.backspace":
                    buffer = buffer[:-1]
                elif k.startswith("Key."):
                    continue
                else:
                    buffer += k

        # flush remaining input
        if buffer:
            steps.append({
                "action": "type",
                "value": buffer
            })

        return steps