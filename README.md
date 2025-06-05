# 🤖 Discord Bot Tutorial

Welcome to the **Discord Bot Tutorial**!  
In this guide, you'll learn how to build a clean, scalable, and production-ready Discord bot using modern tools and best practices.

Youtube Tutorial: https://www.youtube.com/watch?v=C56XHkhqv0g&t=800s
---

## 📦 Tech Stack

- **Python 3.11**
- **Disnake** (or compatible fork)
- **Poetry** – for dependency and environment management
- **Docker** – containerized development & deployment
- **PostgreSQL** – for persistent data storage

---

## 🚀 What You'll Learn

- How to set up a Python Discord bot from scratch
- How to manage dependencies with Poetry
- How to containerize your bot with Docker
- How to connect and interact with a PostgreSQL database
- Best practices for structure, memory usage, and data handling

---

## 🛠️ Getting Started

To get started, clone the repository and follow the setup instructions in [`docs/setup.md`](docs/setup.md) *(coming soon)*.
  ```bash
    git clone https://github.com/xl-spooky/discord-bot-tutorial.git
  ```

Install dependencies using Poetry:
  ```bash
    poetry install
  ```
Run the bot thru poetry or docker:
  ```bash
    poetry run python -m tutorialbot.bot
  ```

  ```bash
    docker compose up --force-recreate --build -d bot
  ```
---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

---

Craft bots with confidence. Clean code, smart structure, modern tools.
