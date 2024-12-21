# IP Information Fetcher (ipinfo)

## Introduction

The IP Information Fetcher is a Django-based application that handles background tasks, performance considerations, and notifications. The main functionality is to fetch information about a list of IP addresses asynchronously and provide real-time updates to the user.

## Features

- User input for multiple IP addresses.
- Validation of IP addresses.
- Fetching information from [ipinfo.io](https://ipinfo.io).
- Submitting IPs one by one asynchronously.
- Real-time updates to the frontend using Server-Sent Events (SSE) with Redis.
- Error handling and logging.

## Requirements

- Docker
- Docker Compose

## Installation

- Clone and run the docker-compose file
   ```bash
   git clone <repository_url>
   cd ipinfo/ipinfo_project/
   docker-compose up --build

## Flow Diagram

![HFywRK3sRBUjsNUSUmVtKP](https://github.com/user-attachments/assets/3e8a5e76-f119-4605-899d-3ecb2c3861af)

## Component Diagram

![component drawio](https://github.com/user-attachments/assets/43207720-2a68-4757-9c26-509dafbba29e)


