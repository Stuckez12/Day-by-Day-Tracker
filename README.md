# Day By Day Tracker

<div style="display: flex; flex-direction: row;">
    <a style="margin-left: 6px; margin-right: 6px;" href="https://jakestuckey46.atlassian.net/jira/software/projects/KAN/boards/2">
        <img src="https://img.shields.io/badge/Jira-0052CC?logo=jira&logoColor=white">
    </a>
    <a style="margin-left: 6px; margin-right: 6px;" href="https://www.figma.com/design/emjUSauyy4WNG0yfSUC6qJ/Day-By-Day-Tracker">
        <img src="https://img.shields.io/badge/Figma-F24E1E?logo=figma&logoColor=white">
    </a>
</div>

Day by Day Tracker is a web-based app for recording, ranking, and reflecting on your days. It helps users track daily progress, manage tasks, and keep notes over time. It was built to be run locally on a Raspberry Pi 5, connected to an external storage device (SSD or USB stick).

## Features

- Self hosted web application
- Ranking and recording of ones day
- Background data backup tasks and retrieval

## Tech Stack

<table>
    <tr>
        <td><strong>Frontend</strong></td>
        <td align="center">
            <img src="https://cdn.simpleicons.org/typescript/3178C6" width="50" /><br>
            TypeScript
        </td>
        <td align="center">
            <img src="https://cdn.simpleicons.org/nextdotjs/000000" width="50" /><br>
            Next.js
        </td>
        <td align="center">
            <img src="https://cdn.simpleicons.org/tailwindcss/06B6D4" width="50" /><br>
            Tailwind CSS
        </td>
    </tr>
    <tr>
        <td><strong>Backend</strong></td>
        <td align="center">
            <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" width="50" /><br>
            Python
        </td>
        <td align="center">
            <img src="https://cdn.simpleicons.org/fastapi/009688" width="50" /><br>
            FastAPI
        </td>
        <td align="center">
            <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/redis/redis-original.svg" width="50" /><br>
            Redis
        </td>
        <td align="center">
            <img src="https://cdn.simpleicons.org/celery/37814A" width="50" /><br>
            Celery
        </td>
    </tr>
</table>

## Outcome of Building this Application

The outcomes for me are learning how to code a frontend framework from scratch and understanding how all the pieces fit together. I also want to learn how to design, manage, maintain, and grow a single project long term. 

The reason I'm building this is to keep track of how I feel each day, week, and month, while also recording what I've done during that time. Over the long term, I want to be able to look back and see what I have accomplished and how I've changed over time.

## Deployment

The application was built to be locally hosted on a Raspberry Pi 5 so you have full control over your data.

### Prerequisites

- Terminal access
- External storage (SSD or USB stick)
- Docker Engine
- Make (optional)

### Installation steps

Install the repo
```
git clone https://github.com/Stuckez12/Day-by-Day-Tracker.git
```
Create the .env.prod file
```
cp .env.example .env.prod
```
Modify the .env file to match your production environment

Finally start up the web application
```
make start-prod
```

## Roadmap

See Jira for full roadmap breakdown

- UI/UX design improvements
- User set tasks to complete
- RAG functionality (optional)
