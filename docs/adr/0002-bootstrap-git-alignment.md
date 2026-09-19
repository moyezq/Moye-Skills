# 开场对齐只快进，不自动 commit

会话索引从「开场零 Shell」改为每条新对话 `git fetch` 一次。落后且工作区干净则 `pull --ff-only`；超前则问过再 push；分叉或 dirty 只报告。不自动 merge / rebase / commit。按日历日缓存会拿到过期 skill；自动合并会把未审视的分叉写进工作树。
