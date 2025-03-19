#!/bin/bash

# 克隆前端代码
git clone -b frontend git@github.com:3401797899/itstudio-web-publish.git frontend
cd frontend
npm install
npm run build
cd ..

# 克隆后端代码
git clone -b backend git@github.com:3401797899/itstudio-web-publish.git backend
cd backend

# 构建Docker镜像
docker compose up -d --build