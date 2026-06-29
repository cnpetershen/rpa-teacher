import re


class IntentRecognizer:

    WINDOW_INTENT_MAP = {
        "login": "user_login",
        "signin": "user_login",
        "sign-in": "user_login",
        "sign in": "user_login",
        "chrome": "web_browsing",
        "edge": "web_browsing",
        "firefox": "web_browsing",
        "notepad": "text_editing",
        "记事本": "text_editing",
        "excel": "spreadsheet_operation",
        "word": "document_editing",
        "outlook": "email_management",
        "搜索": "web_search",
        "百度": "web_search",
        "设置": "system_configuration",
        "settings": "system_configuration",
    }

    LOGIN_KEYWORDS = [
        "登录", "login", "sign in", "密码", "password",
        "username", "账号", "submit",
    ]

    def analyze(self, steps):
        if not steps:
            return [], {"overall_intent": "none", "phases": [], "phase_count": 0}

        enriched = [dict(s) for s in steps]

        overall_intent = self._detect_overall_intent(enriched)
        phases = self._detect_phases(enriched)
        self._assign_step_intents(enriched, phases)

        intent_info = {
            "overall_intent": overall_intent,
            "phases": [p["name"] for p in phases],
            "phase_count": len(phases),
        }

        return enriched, intent_info

    # ----------------------------------------------------------------
    # overall intent
    # ----------------------------------------------------------------
    def _detect_overall_intent(self, steps):
        windows = []
        for s in steps:
            if s.get("action") == "click" and s.get("window"):
                windows.append(s["window"].lower())

        for title in windows:
            for keyword, intent in self.WINDOW_INTENT_MAP.items():
                if keyword in title:
                    return intent

        if self._match_login_pattern(steps):
            return "user_login"

        if self._match_search_pattern(steps):
            return "web_search"

        all_text = " ".join([
            s.get("value", "") for s in steps if s.get("action") == "type"
        ])
        if re.search(r'https?://', all_text):
            return "web_navigation"
        if self._contains_any(all_text.lower(), self.LOGIN_KEYWORDS):
            return "user_login"

        return "general_automation"

    @staticmethod
    def _contains_any(text, keywords):
        return any(k in text for k in keywords)

    @staticmethod
    def _match_login_pattern(steps):
        actions = [s["action"] for s in steps]
        if len(actions) >= 5:
            return actions[:5] == ["click", "type", "click", "type", "click"]
        return False

    @staticmethod
    def _match_search_pattern(steps):
        actions = [s["action"] for s in steps]
        if len(actions) >= 2:
            return actions[:2] == ["click", "type"]
        return False

    # ----------------------------------------------------------------
    # phase detection
    # ----------------------------------------------------------------
    def _detect_phases(self, steps):
        phases = []
        if not steps:
            return phases

        current_phase_start = 0
        current_action = steps[0].get("action", "")

        for i, step in enumerate(steps[1:], start=1):
            action = step.get("action", "")
            if action != current_action:
                phases.append(self._make_phase(
                    steps[current_phase_start:i],
                    current_phase_start,
                    i - 1,
                ))
                current_phase_start = i
                current_action = action

        phases.append(self._make_phase(
            steps[current_phase_start:],
            current_phase_start,
            len(steps) - 1,
        ))

        return phases

    def _make_phase(self, steps_in_phase, start, end):
        return {
            "name": self._name_phase(steps_in_phase),
            "start": start,
            "end": end,
            "action_type": steps_in_phase[0].get("action", ""),
        }

    def _name_phase(self, steps_in_phase):
        if not steps_in_phase:
            return "unknown"

        action = steps_in_phase[0].get("action", "")
        window = steps_in_phase[0].get("window", "")

        if action == "click":
            if self._contains_any(window.lower(), self.LOGIN_KEYWORDS):
                return "login_operation"
            if window:
                return f"navigate_to_{window}"
            return "click_operation"

        if action == "type":
            value = steps_in_phase[0].get("value", "")
            if self._contains_any(value.lower(), self.LOGIN_KEYWORDS):
                return "credential_input"
            if re.search(r'https?://', value):
                return "url_input"
            if value:
                display = value[:10] + "..." if len(value) > 10 else value
                return f"input_{display}"
            return "text_input"

        return f"{action}_operation"

    # ----------------------------------------------------------------
    # per-step intent
    # ----------------------------------------------------------------
    def _assign_step_intents(self, steps, phases):
        for i, step in enumerate(steps):
            phase = self._find_phase(i, phases)
            action = step.get("action", "")
            window = step.get("window", "") if action == "click" else ""
            value = step.get("value", "") if action == "type" else ""

            if action == "click":
                step["intent"] = self._classify_click(window, phase, value)
            elif action == "type":
                step["intent"] = self._classify_type(value, phase)

    @staticmethod
    def _find_phase(step_index, phases):
        for p in phases:
            if p["start"] <= step_index <= p["end"]:
                return p
        return None

    @staticmethod
    def _classify_click(window, phase, value):
        w = window.lower()
        if IntentRecognizer._contains_any(w, ["login", "signin", "sign-in", "登录"]):
            return "goto_login_page"
        if IntentRecognizer._contains_any(w, ["submit", "confirm", "确定"]):
            return "click_submit"
        if IntentRecognizer._contains_any(w, ["search", "搜索", "查找"]):
            return "click_search_box"
        if IntentRecognizer._contains_any(w, ["close", "关闭", "exit"]):
            return "click_close"
        if IntentRecognizer._contains_any(w, ["save", "保存", "存储"]):
            return "click_save"
        if phase and phase.get("action_type") == "type":
            return "focus_input_field"
        return "click_operation"

    @staticmethod
    def _classify_type(value, phase):
        v = value.lower()
        if IntentRecognizer._contains_any(v, ["password", "密码"]):
            return "enter_password"
        if IntentRecognizer._contains_any(v, ["admin", "username", "账号", "用户"]):
            return "enter_username"
        if re.search(r'https?://', v):
            return "enter_url"
        if IntentRecognizer._contains_any(v, IntentRecognizer.LOGIN_KEYWORDS):
            return "enter_credential"
        return "text_input"
