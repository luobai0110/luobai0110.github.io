#!/usr/bin/env python3
"""一条命令发布：把当前改动提交并推送到 GitHub。

用法：
    python publish.py                  # 提交信息 = 时间 + 本次变更的文件列表
    python publish.py "post: 新文章"    # 第一行用你写的说明，时间和文件列表放正文
    python publish.py --dry-run        # 只打印将要使用的提交信息，不提交、不推送
                                       # （仍会执行 git add -A，否则无法列出「本次变更」）

推送后由 GitHub Actions 自动构建并发布到 https://doomer.dpdns.org/

几点实现说明：
  - 先 `git add -A`（遵守 .gitignore，所以 public/ 不会被带进来），
    再用 `git diff --cached` 取「本次真正要提交的文件」，列出的就是这次提交的内容，
    而不是工作区里所有脏文件。
  - 关掉 core.quotePath，否则中文文件名在 git 输出里会变成 \\344\\270\\255 这种八进制转义。
  - git 输出优先按 UTF-8 解码，失败再按系统编码解码：Git for Windows 的提示语是本地化的
    （中文系统下是 GBK），而路径是 UTF-8，两种都得能读。
  - 没有改动但存在未推送的提交时，仍然会执行 push。
"""

import locale
import subprocess
import sys
from datetime import datetime

MAX_LISTED_FILES = 50  # 一次变更太多文件时，列表只列前 N 个

GIT = ["git", "-c", "core.quotePath=false"]


def decode(raw):
    """git 输出优先按 UTF-8 解码，失败则退回系统编码。"""
    if not raw:
        return ""
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode(locale.getpreferredencoding(False), errors="replace")


def git(*args, check=True):
    """执行 git 命令，返回 (退出码, 输出)。"""
    proc = subprocess.run(GIT + list(args), capture_output=True)
    output = (decode(proc.stdout) + decode(proc.stderr)).strip()
    if check and proc.returncode != 0:
        die("git {} 执行失败：\n{}".format(" ".join(args), output))
    return proc.returncode, output


def die(message):
    print(message, file=sys.stderr)
    sys.exit(1)


def staged_changes():
    """解析 `git diff --cached --name-status`，返回 [(状态, 路径), ...]。"""
    _, out = git("diff", "--cached", "--name-status")
    changes = []
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        status = parts[0].strip()
        # 重命名/复制是 "R100\t旧路径\t新路径" 三段
        path = " -> ".join(p.strip() for p in parts[1:])
        changes.append((status, path))
    return changes


def build_message(timestamp, changes, custom=None):
    """构造 (标题, 正文)。正文含时间和本次变更的文件列表。"""
    lines = ["时间：{}".format(timestamp), "本次变更 {} 个文件：".format(len(changes))]
    for status, path in changes[:MAX_LISTED_FILES]:
        lines.append("  {:<4} {}".format(status, path))
    if len(changes) > MAX_LISTED_FILES:
        lines.append("  …… 另有 {} 个文件未列出".format(len(changes) - MAX_LISTED_FILES))
    body = "\n".join(lines)
    subject = custom if custom else "publish: {}".format(timestamp)
    return subject, body


def actions_url():
    """尽力从 origin 推算出仓库的 Actions 页面地址。"""
    code, url = git("remote", "get-url", "origin", check=False)
    if code != 0 or not url:
        return None
    url = url.strip()
    if url.endswith(".git"):
        url = url[:-4]
    if url.startswith("git@"):  # git@github.com:user/repo
        url = "https://" + url[4:].replace(":", "/", 1)
    return url + "/actions" if "github.com" in url else None


def main():
    argv = sys.argv[1:]
    dry_run = "--dry-run" in argv
    rest = [a for a in argv if a != "--dry-run"]
    custom = rest[0] if rest else None

    # 控制台/管道统一按 UTF-8 输出，避免中文提示在重定向时崩掉或乱码
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    if git("rev-parse", "--git-dir", check=False)[0] != 0:
        die("当前目录不是 git 仓库")

    git("add", "-A")
    changes = staged_changes()
    timestamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
    subject, body = build_message(timestamp, changes, custom)

    if dry_run:
        print("== 将要提交的信息 ==" if changes else "== 没有需要提交的改动 ==")
        if changes:
            print(subject)
            print()
            print(body)
            print("== 以上内容不会真的提交（--dry-run）==")
        return 0

    if changes:
        git("commit", "-m", subject, "-m", body)
        print("已提交 {} 个文件：{}".format(len(changes), subject))
    else:
        print("没有需要提交的改动")

    code, output = git("push", check=False)
    if code != 0:
        print("推送失败（提交已保存在本地，修好后直接 git push）:", file=sys.stderr)
        print(output, file=sys.stderr)
        return 1

    print(output)
    print("已推送，GitHub Actions 会自动构建并发布。")
    url = actions_url()
    if url:
        print("运行情况：{}".format(url))
    return 0


if __name__ == "__main__":
    sys.exit(main())
