[app]
title = SelfDisciplineManager
package.name = selfdiscipline
package.domain = org.example
version = 1.2

icon.filename = %(source.dir)s/icon.png

source.dir = .
source.include_exts = py,png,jpg,kv,atlas
source.main.py = main.py

android.ndk = 25b
android.api = 33
android.ndk_api = 21
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.add_assets = experience.txt,record.txt
android.orientation = portrait
android.minapi = 24
android.proguard = yes
android.proguard_config = proguard-rules.pro

requirements = python3,kivy,pytz

[buildozer]
log_leverl = 2

android.sdk_repository = https://mirrors.tuna.tsinghua.edu.cn/android/repository
android.pip_repository = https://pypi.tuna.tsinghua.edu.cn/simple
