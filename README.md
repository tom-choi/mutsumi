# Python Discord Bot Template

<p align="center">
  <a href="https://discord.gg/xj6y5ZaTMr"><img src="https://img.shields.io/discord/1358456011316396295?logo=discord"></a>
  <a href="https://github.com/kkrypt0nn/Python-Discord-Bot-Template/releases"><img src="https://img.shields.io/github/v/release/kkrypt0nn/Python-Discord-Bot-Template"></a>
  <a href="https://github.com/kkrypt0nn/Python-Discord-Bot-Template/commits/main"><img src="https://img.shields.io/github/last-commit/kkrypt0nn/Python-Discord-Bot-Template"></a>
  <a href="https://github.com/kkrypt0nn/Python-Discord-Bot-Template/blob/main/LICENSE.md"><img src="https://img.shields.io/github/license/kkrypt0nn/Python-Discord-Bot-Template"></a>
  <a href="https://github.com/kkrypt0nn/Python-Discord-Bot-Template"><img src="https://img.shields.io/github/languages/code-size/kkrypt0nn/Python-Discord-Bot-Template"></a>
  <a href="https://conventionalcommits.org/en/v1.0.0/"><img src="https://img.shields.io/badge/Conventional%20Commits-1.0.0-%23FE5196?logo=conventionalcommits&logoColor=white"></a>
  <a href="https://github.com/psf/black"><img src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
</p>

![](./mutsumi.jpg)

這...給想寫bot的人...就像新人偶像第一次登台...（小聲）
我剛開始寫bot時...很辛苦...所以做了這個模板...

重要的事...

用我的代碼...要留名字和連結...

許可證不能改...

不然...（突然睜大眼睛）會像忘詞的偶像一樣...被請下台哦...

# [手指戳戳免責聲明部分]
斜線指令...註冊要等很久...測試時用@app_commands.guilds()...放伺服器ID...馬上就能用...

# 下載方法...三種

- 點"Use this template"按鈕...最方便...

- 用git clone...會魔法的人...

- 去這裡申請bot...然後按這個格式邀請：
  - https://discord.com/oauth2/authorize?&client_id=你的ID&scope=bot+applications.commands&permissions=權限數字
## How to set up

To set up the token you will have to make use of the [`.env.example`](.env.example) file; you should rename it to `.env` and replace the `YOUR_BOT...` content with your actual values that match for your bot.

Alternatively you can simply create a system environment variable with the same names and their respective value.

## How to start

### The _"usual"_ way

To start the bot you simply need to launch, either your terminal (Linux, Mac & Windows), or your Command Prompt (
Windows)
.

Before running the bot you will need to install all the requirements with this command:

```
python -m pip install -r requirements.txt
```

After that you can start it with

```
python bot.py
```

> **Note**: You may need to replace `python` with `py`, `python3`, `python3.11`, etc. depending on what Python versions you have installed on the machine.

### Docker

Support to start the bot in a Docker container has been added. After having [Docker](https://docker.com) installed on your machine, you can simply execute:

```
docker compose up -d --build
```

> **Note**: `-d` will make the container run in detached mode, so in the background.

## Issues or Questions

If you have any issues or questions of how to code a specific command, you can:

- Join my Discord server [here](https://discord.gg/xj6y5ZaTMr)
- Post them [here](https://github.com/kkrypt0nn/Python-Discord-Bot-Template/issues)

Me or other people will take their time to answer and help you.

## Versioning

We use [SemVer](http://semver.org) for versioning. For the versions available, see
the [tags on this repository](https://github.com/kkrypt0nn/Python-Discord-Bot-Template/tags).

## Built With

- [Python 3.12.9](https://www.python.org/)

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE.md](LICENSE.md) file for details
