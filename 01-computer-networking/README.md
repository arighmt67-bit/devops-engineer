# Building a Web Server — Dicoding Jarkom Final Project

A web server project built as the final submission for the **Belajar Jaringan Komputer untuk Pemula** course on Dicoding.

## Project Overview

This project demonstrates the ability to set up a Node.js web server, configure NGINX as a reverse proxy, implement rate limiting, and apply the same configuration using Apache2 — all running on a local Linux environment (WSL/Ubuntu on macOS).

## Live Deployment

🚀 **[building-a-web-server-production.up.railway.app](https://building-a-web-server-production.up.railway.app/)**

The application is deployed on Railway with live endpoints:
- **GET /** → "Hello world!"
- **GET /me** → "arijhmtr"

## Tech Stack

- **Node.js** (v25.9.0) + **Express** — web server on port 8000
- **NGINX** — reverse proxy on port 80 and 3000
- **Apache2** — alternative reverse proxy on port 8080

## Features Implemented

- Node.js Express server with routes `/` and `/me`
- NGINX configured as reverse proxy forwarding to Node.js
- NGINX rate limiting: 6 requests per minute (1 request every 10 seconds)
- NGINX listening on both port 80 and port 3000
- Apache2 configured on port 8080 as alternative reverse proxy
- `/me` endpoint returns Dicoding username: `arijhmtr`

## Project Structure
