class CorrectionEngine:

    INTENT_PATTERNS = {
        "user_login": {
            "expected_actions": [
                "click", "type", "click", "type", "click",
            ],
            "min_steps": 5,
            "must_have": ["click", "type"],
        },
        "web_search": {
            "expected_actions": ["click", "type"],
            "min_steps": 2,
            "must_have": ["click", "type"],
        },
        "web_navigation": {
            "expected_actions": ["click", "type"],
            "min_steps": 2,
            "must_have": ["click", "type"],
        },
        "text_editing": {
            "expected_actions": ["click", "type"],
            "min_steps": 2,
            "must_have": ["click", "type"],
        },
        "spreadsheet_operation": {
            "expected_actions": ["click", "type"],
            "min_steps": 2,
            "must_have": ["click", "type"],
        },
        "document_editing": {
            "expected_actions": ["click", "type"],
            "min_steps": 2,
            "must_have": ["click", "type"],
        },
        "email_management": {
            "expected_actions": ["click", "type"],
            "min_steps": 2,
            "must_have": ["click", "type"],
        },
        "system_configuration": {
            "expected_actions": ["click"],
            "min_steps": 1,
            "must_have": ["click"],
        },
        "web_browsing": {
            "expected_actions": None,
            "min_steps": 1,
            "must_have": [],
        },
        "general_automation": {
            "expected_actions": None,
            "min_steps": 1,
            "must_have": [],
        },
    }

    def correct(self, steps, intent_info):
        if not steps:
            return []

        corrections = []

        overall_intent = intent_info.get(
            "overall_intent", "general_automation"
        )
        pattern = self.INTENT_PATTERNS.get(
            overall_intent,
            self.INTENT_PATTERNS["general_automation"],
        )

        actions = [s["action"] for s in steps]

        corrections += self._check_min_steps(
            steps, pattern, actions
        )
        corrections += self._check_must_have(
            steps, pattern, actions
        )
        corrections += self._check_expected_sequence(
            steps, pattern, actions, overall_intent
        )
        corrections += self._check_unpaired_input(
            steps, actions
        )
        corrections += self._check_empty_input(steps)
        corrections += self._check_window_jumps(steps)

        return corrections

    # --------------------------------------------------------
    # 检查1: 最少步骤数
    # --------------------------------------------------------
    @staticmethod
    def _check_min_steps(steps, pattern, actions):
        corrections = []
        min_steps = pattern["min_steps"]
        if len(steps) < min_steps:
            corrections.append({
                "type": "MISSING_STEP",
                "severity": "error",
                "step_index": None,
                "message": (
                    f"步骤数不足：当前 {len(steps)} 步，"
                    f"意图需要至少 {min_steps} 步"
                ),
                "suggestion": "请补全遗漏的操作步骤",
            })
        return corrections

    # --------------------------------------------------------
    # 检查2: 必须包含的动作类型
    # --------------------------------------------------------
    @staticmethod
    def _check_must_have(steps, pattern, actions):
        corrections = []
        for required in pattern["must_have"]:
            if required not in actions:
                msg = (
                    f"缺少必要动作：'{required}'。"
                    f"当前意图需要该类型操作"
                )
                corrections.append({
                    "type": "MISSING_ACTION",
                    "severity": "error",
                    "step_index": None,
                    "message": msg,
                    "suggestion": (
                        f"请在合适位置添加 '{required}' 操作"
                    ),
                })
        return corrections

    # --------------------------------------------------------
    # 检查3: 动作顺序与期望序列对比
    # --------------------------------------------------------
    @staticmethod
    def _check_expected_sequence(
        steps, pattern, actions, overall_intent
    ):
        corrections = []
        expected = pattern.get("expected_actions")
        if expected is None:
            return corrections

        # 检查 type 是否出现在第一个 click 之前
        first_click_idx = None
        first_type_idx = None
        for i, a in enumerate(actions):
            if a == "click" and first_click_idx is None:
                first_click_idx = i
            if a == "type" and first_type_idx is None:
                first_type_idx = i

        if (
            first_type_idx is not None
            and first_click_idx is not None
            and first_type_idx < first_click_idx
        ):
            corrections.append({
                "type": "WRONG_ORDER",
                "severity": "warning",
                "step_index": first_type_idx,
                "message": "输入操作出现在点击之前："
                           "可能未聚焦目标就键入内容",
                "suggestion": "请在输入前添加点击操作"
                              "来聚焦目标控件",
            })

        # 对于登录意图，检查三击结构
        login_check = (
            overall_intent == "user_login"
            and len(actions) >= 5
        )
        if login_check:
            bad = (
                actions[0] != "click"
                or actions[2] != "click"
                or actions[4] != "click"
            )
            if bad:
                corrections.append({
                    "type": "WRONG_ORDER",
                    "severity": "warning",
                    "step_index": None,
                    "message": "登录流程结构异常：期望 "
                               "点击→输入→点击→输入"
                               "→点击 的顺序",
                    "suggestion": (
                        "请检查操作顺序是否对应："
                        "聚焦用户名→输入→"
                        "聚焦密码→输入→点击登录"
                    ),
                })

        # 对于 search/navigation 意图，检查多余步骤
        search_intents = (
            "web_search", "web_navigation", "text_editing"
        )
        if overall_intent in search_intents:
            if len(actions) > 2:
                extra_count = len(actions) - 2
                msg = (
                    f"检测到 {extra_count} 个多余步骤："
                    "该意图通常只需 点击→输入 两步"
                )
                corrections.append({
                    "type": "EXTRA_STEP",
                    "severity": "info",
                    "step_index": 2,
                    "message": msg,
                    "suggestion": "检查这些步骤是否必要，"
                                  "可考虑删除",
                })

        return corrections

    # --------------------------------------------------------
    # 检查4: type 前缺少对应的 click
    # --------------------------------------------------------
    @staticmethod
    def _check_unpaired_input(steps, actions):
        corrections = []
        consecutive_types = 0
        for i, a in enumerate(actions):
            if a == "type":
                consecutive_types += 1
                if consecutive_types > 1:
                    msg = (
                        f"连续第 {consecutive_types} "
                        f"次输入：中间没有点击切换目标"
                    )
                    corrections.append({
                        "type": "UNPAIRED_INPUT",
                        "severity": "warning",
                        "step_index": i,
                        "message": msg,
                        "suggestion": "在连续输入之间添加"
                                      "点击操作来切换输入焦点",
                    })
            else:
                consecutive_types = 0
        return corrections

    # --------------------------------------------------------
    # 检查5: 空输入
    # --------------------------------------------------------
    @staticmethod
    def _check_empty_input(steps):
        corrections = []
        for i, s in enumerate(steps):
            action = s.get("action") == "type"
            empty = not s.get("value", "").strip()
            if action and empty:
                corrections.append({
                    "type": "EMPTY_INPUT",
                    "severity": "error",
                    "step_index": i,
                    "message": f"第 {i} 步输入内容为空",
                    "suggestion": "请检查是否遗漏了输入内容，"
                                  "或删除不必要的输入步骤",
                })
        return corrections

    # --------------------------------------------------------
    # 检查6: 窗口不必要跳跃
    # --------------------------------------------------------
    @staticmethod
    def _check_window_jumps(steps):
        corrections = []
        last_window = None
        for i, s in enumerate(steps):
            if s.get("action") == "click":
                current = s.get("window", "")
                if last_window and current != last_window:
                    pass
                if current:
                    last_window = current
        return corrections
