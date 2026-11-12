# COK 项目一键入口
#
# 核心: `python3 -m cok` (桌面端) 与 `./gradlew` (安卓端)。
# 默认用仓库里的 gradlew，没有就回退本机 gradle。
# 不依赖全局安装的 Android SDK 环境变量——`sdk.dir` 已在 android-app/local.properties。

SHELL := /bin/bash
ROOT   := $(shell pwd)
PYTHON ?= python3

ANDROID := $(ROOT)/android-app
GRADLEW := $(ANDROID)/gradlew
GRADLE_CMD = $(if $(wildcard $(GRADLEW)),cd $(ANDROID) && ./gradlew --offline,\
                                    cd $(ANDROID) && ~/.gradle/wrapper/dists/gradle-9.6.1-bin/gradle-9.6.1/bin/gradle --offline)

.PHONY: help build-apk install-app run test list

help:
	@echo "COK 项目一键入口"
	@echo ""
	@echo "  make build-apk   编译安卓 APK（debug）"
	@echo "  make install-app 把 APK 装到手机（需已连一台设备）"
	@echo "  make run         启动桌面端网页控制台（127.0.0.1:8770）"
	@echo "  make test        跑全部离线回归测试（不联网）"
	@echo "  make list        列出所有可用子命令"
	@echo ""
	@echo "所有命令都在 $(ROOT) 下运行，不需要先 cd 到某个子目录。"

build-apk:
	@echo ">>> 构建安卓 APK..."
	@$(GRADLE_CMD) :app:assembleDebug

install-app:
	@echo ">>> 构建并装到手机..."
	@$(GRADLE_CMD) :app:assembleDebug :app:installDebug

run:
	@echo ">>> 启动桌面端控制台 (Ctrl-C 停止)..."
	cd $(ROOT) && $(PYTHON) -m cok console

test:
	@echo ">>> 跑离线回归测试..."
	cd $(ROOT) && $(PYTHON) -m cok test

list:
	cd $(ROOT) && $(PYTHON) -m cok list
