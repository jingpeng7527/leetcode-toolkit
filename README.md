# leetcode-toolkit

刷了几百道题，过几个月就忘了。这个工具读取你完整的 LeetCode 提交记录，用记忆曲线算出**今天最值得重做的题**，优先推荐 NeetCode 250、Top 100、Top Interview 150、Google / Apple 等题单里反复出现的题，并同步到 Notion、生成本地仪表盘。

## 快速开始

```bash
git clone https://github.com/jingpeng7527/leetcode-toolkit.git
cd leetcode-toolkit
pip3 install -r requirements.txt
cp .env.example .env      # 然后填入你的 LeetCode Cookie，见下
python3 scripts/review.py
```

**获取 Cookie**：浏览器登录 leetcode.com → 开发者工具 → Application → Cookies，复制 `LEETCODE_SESSION` 和 `csrftoken` 填进 `.env`。它们等同于你的登录凭证，不要发给别人或提交到 git（`.env` 已被忽略）。

## 能做什么

| 命令 | 作用 |
|---|---|
| `python3 scripts/review.py` | 在终端列出今天该复习的题（`--all` 看全部，`--export out.csv` 导出） |
| `python3 scripts/dashboard.py` | 生成并打开本地网页仪表盘：复习队列、遗忘曲线、做题热力图、题单覆盖进度 |
| `python3 scripts/sync.py` | 把最该复习的前 50 题同步到 Notion（`--limit N` 调整数量） |
| `python3 scripts/explain.py two-sum` | 让 Claude 给这道题分层提示（不直接给答案） |
| `python3 scripts/daily.py` | 今日每日一题 |

## 推荐是怎么排出来的

- 每次成功重做，下次复习的间隔变长：1、3、7、16、35、75、160 天。
- 难题间隔更短，评分（zerotrac 周赛难度分）超过 2000 的超难题则往后放。
- 出现在越多题单（NeetCode、Top 100、公司题单……）里的题，间隔越短、排位越靠前。
- 距离上次 AC 超过一个间隔，就视为"到期"。

具体数值都在 [review/spaced_repetition.py](review/spaced_repetition.py) 顶部，可以自己调。

## 可选配置

在 `.env` 里按需填写：

- **公司题单**（`COMPANIES=google,apple`）：需要 LeetCode Premium 的 Cookie，拉不到会自动跳过。
- **Notion 同步**：填 `NOTION_API_KEY` 和 `NOTION_DATABASE_ID`。数据库需要这些列：`Name`（标题）、`Slug`（文本）、`Difficulty`（单选）、`Rating`、`AC Count`、`Overdue Days`（数字）、`Last AC`（日期）、`Lists`（多选）、`URL`（网址），并把数据库分享给你的 integration。
- **关联你已有的笔记**：再加 `Notes`（网址）和 `Topic`（单选）两列，填 `NOTION_NOTES_PAGE_ID`（笔记根页面，也要分享给 integration）。笔记页标题里带题号，比如 `76. Minimum Window Substring`，就会自动对应上。
- **Claude 讲题**：填 `ANTHROPIC_API_KEY`。

## 注意

- 只支持 leetcode.com，不支持 leetcode.cn。
- 提交历史用的是 LeetCode 没有公开文档的接口，将来可能失效。
- 周赛难度分只覆盖上过周赛的约 2600 道题，其余按 Easy / Medium / Hard 估算。
- Cookie 会过期，报认证错误时重新复制一份即可。

## 致谢

难度分来自 [zerotrac/leetcode_problem_rating](https://github.com/zerotrac/leetcode_problem_rating)，NeetCode 题单来自 [neetcode-gh/leetcode](https://github.com/neetcode-gh/leetcode)。

MIT License
