# Findings

## 当前已确认事实

1. 当前 loop 已有 pull / push / sync recovery，但没有真正的 `commit` phase。
2. `loop_result` 已有 `commit_created` / `commit_message` 字段，但大多数路径还只是占位。
3. 当前最合适的增强是：
- 只在 case 成功后做最小自动 commit
- 不在这一轮扩展复杂 git 编排
4. 自动 commit 必须在 case 状态和 `loop_cases.json` 写回之后执行，否则提交后仍会残留业务脏改动。
5. runtime/state/runs 这类运行态产物必须默认忽略，否则自动 commit 虽然成功，工作树仍会被运行时文件污染。
6. 目前这轮的最佳实践已经验证成立：
- 在 scaffold 阶段写入 `.gitignore`
- 在成功 case 后进入 `committing`
- 统一执行 `git add -A` + `git commit`
- 把 commit 信息写回结构化 result
