import sys
import time
import datetime
import pytz
import random
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.config import Config
from typing import Optional, Tuple


# ===================== 配置常量 =====================
CONFIG = {
    "timezone": "Asia/Shanghai",
    "target_task_count": 5,  # 达标任务数
    "max_continuous_unmet": 3,  # 最大连续不达标次数
    "experience_per_task": 10,  # 每个任务的经验值
    "experience_penalty": 30,  # 连续不达标惩罚经验
    "file_paths": {
        "task_list": "list.txt",
        "unmet_record": "record.txt",
        "experience": "experience.txt"
    }
}

# ========== 自律鼓励语库 ==========
ENCOURAGEMENT_MESSAGES = [
    "自律的苦轻如鸿毛，后悔的痛重如泰山 ⛰️",
    "今天的坚持，是明天的底气 ✊",
    "不必万丈光芒，但请始终温暖有光 ✨",
    "自律不是咬牙坚持，而是习惯成自然 🧩",
    "你多一份自律，生活就多一份自由 🎈",
    "慢慢来，谁还没有一个努力的过程 🚶",
    "坚持的意义，在于让平凡的日子闪着光 ✨",
    "当下的每一次努力，都是未来的伏笔 📝",
    "自律的最高境界：忙而不慌，累而不丧 💪",
    "你想要的，都藏在你的坚持里 🌟"
]

# ========== 创意骂人话术库 ==========
CURSE_MESSAGES = {
    "light": [
        "😅 兄弟，经验都负了还摆烂？生产队的驴都没你能歇！",
        "🤡 就这？就这？经验都干成负数了，还好意思摸鱼？",
        "💤 建议你直接把自律管理器卸了，反正也不做任务~",
        "🍵 哟，经验负数的“摆烂大师”，今日功德-10086！",
        "🚶 跑起来啊！经验都倒欠了，还搁这儿散步呢？"
    ],
    "medium": [
        "💥 完了完了，经验负几百了，你是反向自律是吧？",
        "🔥 别人涨经验你掉经验，你这是在给自律界拖后腿啊！",
        "🤑 经验都负成这样了，是不是得给系统交“摆烂税”？",
        "👊 再摆烂下去，你的称号都要变成“入土级”了！",
        "🎮 打游戏都知道刷经验，自律咋就不学学？负成这样了！"
    ],
    "heavy": [
        "💀 逆天！经验负上千了，你是要创个“反向自律吉尼斯”？",
        "🌋 火山喷发级摆烂！经验负成这样，系统都想拉黑你！",
        "🚀 别人自律升级，你自律降级，直接负到外太空了？",
        "👻 建议改名叫“摆烂鬼”，经验负数比阎王爷的账本还离谱！",
        "🤯 我服了！经验负成这样，你是不是和自律有仇？！"
    ]
}


# ===================== 工具函数 =====================
def get_beijing_time() -> datetime.datetime:
    """获取当前北京时间"""
    beijing_tz = pytz.timezone(CONFIG["timezone"])
    return datetime.datetime.now(beijing_tz)


def read_file(file_path: str, default: str = "") -> str:
    """安全读取文件，处理文件不存在/读取异常"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return default
    except Exception as e:
        show_popup("文件错误", f"读取文件出错：{e}")
        sys.exit(1)


def write_file(file_path: str, content: str):
    """安全写入文件，处理写入异常"""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        show_popup("文件错误", f"写入文件出错：{e}")
        sys.exit(1)


def split_task_input(input_str: str) -> list:
    """分割任务输入（兼容中文逗号和英文逗号）"""
    unified_input = input_str.replace("，", ",")
    task_list = [item.strip() for item in unified_input.split(',') if item.strip()]
    return task_list


def get_task_list() -> Tuple[list, int]:
    """获取今日任务列表和任务总数"""
    content = read_file(CONFIG["file_paths"]["task_list"])
    task_list = [item.strip() for item in content.split("\n") if item.strip()]
    return task_list, len(task_list)


def get_continuous_unmet_count() -> int:
    """获取当前连续不达标次数"""
    count_str = read_file(CONFIG["file_paths"]["unmet_record"], "0")
    return int(count_str) if count_str.isdigit() else 0


def get_total_experience() -> int:
    """获取当前总经验值"""
    exp_str = read_file(CONFIG["file_paths"]["experience"], "0")
    return int(exp_str) if exp_str.isdigit() else 0


def get_title_by_experience(total_exp: int) -> Tuple[str, str]:
    """根据经验值获取对应的称号和鼓励语"""
    level_rules = [
        (300000, "Goat", "你简直就是自律界的Faker!!!"),
        (150000, "顶尖职业", "太强辣！你正在迈向自律界的山巅！！"),
        (100000, "职业", "顶中顶！你是自律界中0.001%的强者！"),
        (60000, "王者", "how new bee，你已经达到了普通自律者的极限！"),
        (35000, "宗师", "不要停下，你即将叩响自律界的王者大门！"),
        (20000, "大师", "自律超神！但在自律界的Faker眼里还是菜鸟哦！"),
        (10000, "钻石", "继续加油！你是自律界数一数二的佼佼者！"),
        (5000, "翡翠", "厉害厉害！你离自律界的天堑仅有一步之遥！"),
        (2000, "铂金", "你是极其出色的自律者！继续保持这份毅力哦！"),
        (1200, "黄金", "太优秀了！自律已经成为你的好习惯啦！"),
        (500, "白银", "很棒！你的自律性已经超过不少人了~"),
        (100, "黄铜", "已经入门啦，继续积累经验向更高等级前进！"),
        (0, "黑铁", "刚开始没关系，坚持完成任务就能升级！"),
    ]
    for exp_threshold, title, encouragement in level_rules:
        if total_exp >= exp_threshold:
            return title, encouragement
    return "黑铁", "刚开始没关系，坚持完成任务就能升级！"


def show_popup(title, content):
    """显示弹窗（替代tkinter的messagebox）"""
    popup = Popup(title=title,
                  content=Label(text=content, font_size=16),
                  size_hint=(0.8, 0.4))
    popup.open()


# ===================== 主界面类 =====================
class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = 20
        self.spacing = 15

        # 初始化必要文件
        for file_path in CONFIG["file_paths"].values():
            if not read_file(file_path):
                write_file(file_path, "0")

        # 1. 顶部时间和鼓励语
        top_layout = BoxLayout(orientation="vertical", spacing=10)
        # 当前时间
        now = get_beijing_time()
        current_time_str = now.strftime('%Y-%m-%d %H:%M')
        today_end = now.replace(hour=23, minute=59, second=59, microsecond=0)
        time_left = today_end - now
        hours = int(time_left.total_seconds() // 3600)
        minutes = int((time_left.total_seconds() % 3600) // 60)
        time_label = Label(
            text=f"当前北京时间：{current_time_str}\n距离今天结束还有：{hours} 小时 {minutes} 分钟",
            font_size=14
        )
        top_layout.add_widget(time_label)
        # 随机鼓励语
        random_encouragement = random.choice(ENCOURAGEMENT_MESSAGES)
        encourage_label = Label(
            text=random_encouragement,
            font_size=16,
            color=(0.9, 0.2, 0.2, 1)  # 红色
        )
        top_layout.add_widget(encourage_label)
        self.add_widget(top_layout)

        # 2. 使用说明（滚动文本）
        intro_scroll = ScrollView(size_hint=(1, 0.3))
        intro_content = f"""【使用方法】
1. 设定/重置今日任务：输入需要完成的任务（中文/英文逗号分隔均可），例如：看书，跑步，学习
2. 今日打卡：输入当日完成的任务数量（0-总任务数），系统会自动计算经验值
3. 查看经验值：查看当前总经验和对应的自律称号，经验为负时会触发趣味提醒
4. 查看连续不达标次数：查看近期未完成足量任务的连续次数

【惩罚规则】
1. 达标任务数：{CONFIG['target_task_count']}个（每日完成任务数≥此数即为达标）
2. 连续不达标计数：每日完成任务数＜{CONFIG['target_task_count']}个时，连续不达标次数+1
3. 最大连续不达标次数：{CONFIG['max_continuous_unmet']}次
   - 连续不达标＜{CONFIG['max_continuous_unmet']}次：仅提示当前连续次数
   - 连续不达标≥{CONFIG['max_continuous_unmet']}次：扣除{CONFIG['experience_penalty']}点经验/天
4. 经验计算规则：
   - 基础经验：完成任务数 × {CONFIG['experience_per_task']}点/个
   - 惩罚扣减：连续不达标超限时，每日扣除{CONFIG['experience_penalty']}点经验
   - 经验为负：触发不同等级的趣味提醒，督促你恢复自律！"""
        intro_label = Label(
            text=intro_content,
            font_size=12,
            color=(0.16, 0.6, 0.58, 1),  # 青绿色
            text_size=(Window.width * 0.9, None),
            size_hint_y=None,
            height=400
        )
        intro_scroll.add_widget(intro_label)
        self.add_widget(intro_scroll)

        # 3. 功能按钮
        btn_layout = GridLayout(cols=2, spacing=15, size_hint=(1, 0.4))
        # 设定任务按钮
        task_set_btn = Button(
            text="设定/重置今日任务",
            font_size=16,
            on_press=self.create_task_set_page
        )
        btn_layout.add_widget(task_set_btn)
        # 打卡按钮
        check_in_btn = Button(
            text="今日打卡",
            font_size=16,
            on_press=self.create_check_in_page
        )
        btn_layout.add_widget(check_in_btn)
        # 查看经验按钮
        view_exp_btn = Button(
            text="查看经验值",
            font_size=16,
            on_press=self.view_experience
        )
        btn_layout.add_widget(view_exp_btn)
        # 查看连续不达标次数按钮
        view_unmet_btn = Button(
            text="查看连续不达标次数",
            font_size=16,
            on_press=self.view_unmet_count
        )
        btn_layout.add_widget(view_unmet_btn)
        self.add_widget(btn_layout)

    def create_task_set_page(self, *args):
        """任务设定页面"""
        self.clear_widgets()
        layout = BoxLayout(orientation="vertical", padding=20, spacing=15)

        # 标题
        title = Label(text="设定/重置今日任务", font_size=20, bold=True)
        layout.add_widget(title)

        # 当前任务展示
        task_list, _ = get_task_list()
        if task_list:
            task_text = "当前今日任务：\n" + "\n".join([f"{idx}. {task}" for idx, task in enumerate(task_list, 1)])
        else:
            task_text = "当前无今日任务"
        task_label = Label(text=task_text, font_size=14)
        layout.add_widget(task_label)

        # 任务输入框
        self.task_input = TextInput(hint_text="输入任务（中文/英文逗号分隔）", font_size=16, size_hint=(1, 0.2))
        layout.add_widget(self.task_input)

        # 按钮
        btn_layout = GridLayout(cols=2, spacing=15)
        save_btn = Button(text="保存任务", font_size=16, on_press=self.save_task_list)
        back_btn = Button(text="返回首页", font_size=16, on_press=self.back_to_home)
        btn_layout.add_widget(save_btn)
        btn_layout.add_widget(back_btn)
        layout.add_widget(btn_layout)

        self.add_widget(layout)

    def save_task_list(self, *args):
        """保存任务列表"""
        user_input = self.task_input.text.strip()
        task_list = split_task_input(user_input)
        if not task_list:
            show_popup("输入错误", "任务不能为空！")
            return

        write_file(CONFIG["file_paths"]["task_list"], "\n".join(task_list))
        task_msg = "今日任务已更新，任务如下：\n" + "\n".join([f"{idx}. {task}" for idx, task in enumerate(task_list, 1)])
        show_popup("任务保存成功", task_msg)
        self.back_to_home()

    def create_check_in_page(self, *args):
        """打卡页面"""
        self.clear_widgets()
        layout = BoxLayout(orientation="vertical", padding=20, spacing=15)

        # 标题
        title = Label(text="今日打卡", font_size=20, bold=True)
        layout.add_widget(title)

        # 获取任务列表
        task_list, task_count = get_task_list()
        if not task_list:
            show_popup("无任务", "今日无任务，请先设定任务再打卡！")
            self.back_to_home()
            return

        # 展示任务
        task_text = f"今日共要完成{task_count}项任务：\n" + "\n".join([f"{idx}. {task}" for idx, task in enumerate(task_list, 1)])
        task_label = Label(text=task_text, font_size=14)
        layout.add_widget(task_label)

        # 打卡输入框
        self.check_input = TextInput(hint_text=f"输入完成的任务数（0-{task_count}）", font_size=16, size_hint=(1, 0.2))
        layout.add_widget(self.check_input)

        # 按钮
        btn_layout = GridLayout(cols=2, spacing=15)
        submit_btn = Button(text="提交打卡", font_size=16, on_press=self.process_check_in)
        back_btn = Button(text="返回首页", font_size=16, on_press=self.back_to_home)
        btn_layout.add_widget(submit_btn)
        btn_layout.add_widget(back_btn)
        layout.add_widget(btn_layout)

        self.add_widget(layout)

    def process_check_in(self, *args):
        """处理打卡逻辑"""
        task_list, task_count = get_task_list()
        try:
            completed = int(self.check_input.text.strip())
            if not (0 <= completed <= task_count):
                raise ValueError
        except ValueError:
            show_popup("输入错误", f"请输入0到{task_count}之间的整数！")
            return

        # 更新连续不达标次数
        continuous_unmet = get_continuous_unmet_count()
        if completed < CONFIG["target_task_count"]:  # 原代码是<=，修正为<（达标是≥）
            continuous_unmet += 1
            if continuous_unmet < CONFIG["max_continuous_unmet"]:
                show_popup("提示", f"任务数小于{CONFIG['target_task_count']}，连续次数：{continuous_unmet}/{CONFIG['max_continuous_unmet']}")
            else:
                show_popup("警告", f"任务数小于{CONFIG['target_task_count']}，当前连续不达标次数：{continuous_unmet}\n🚨 警告！你已连续{continuous_unmet}天每日完成任务数不足{CONFIG['target_task_count']}个，要加油啦！🚨")
        else:
            continuous_unmet = 0
            show_popup("恭喜", "✅ 任务数达标，当前连续未达标次数已重置为 0")

        # 保存连续不达标次数
        write_file(CONFIG["file_paths"]["unmet_record"], str(continuous_unmet))

        # 计算经验值
        base_experience = completed * CONFIG["experience_per_task"]
        total_experience = get_total_experience()

        # 经验惩罚
        if continuous_unmet >= CONFIG["max_continuous_unmet"]:
            base_experience -= CONFIG["experience_penalty"]
            show_popup("经验扣除", f"由于您多次未完成足量任务，扣除{CONFIG['experience_penalty']}点经验！")

        # 展示经验结果
        if base_experience < 0:
            show_popup("经验提醒", f"您今日获得的经验为负数：{base_experience}点，请好好反省！")
        elif base_experience == 0:
            show_popup("经验提醒", "您今天没有获得任何经验。请于明日继续努力！")
        else:
            show_popup("恭喜", f"恭喜您，您今天获得{base_experience}点经验！")

        # 更新总经验
        new_total_exp = total_experience + base_experience
        write_file(CONFIG["file_paths"]["experience"], str(new_total_exp))

        # 展示称号和总经验
        if new_total_exp < 0:
            # 按严重程度选话术
            if new_total_exp >= -200:
                curse_list = CURSE_MESSAGES["light"]
            elif new_total_exp >= -1000:
                curse_list = CURSE_MESSAGES["medium"]
            else:
                curse_list = CURSE_MESSAGES["heavy"]

            random_curse = random.choice(curse_list)
            curse_msg = (
                f"⚠️ 打卡警告！⚠️\n"
                f"打卡后经验值：{new_total_exp}点（负麻了！）\n\n"
                f"{random_curse}\n\n"
                "👉 明天再不完成任务，系统就要给你发“摆烂证书”了！"
            )
            show_popup(f"摆烂警告 | 经验负数{new_total_exp}点", curse_msg)

            # 彩蛋：极重度负数
            if new_total_exp < -2000:
                easter_egg = "🐣 彩蛋：建议你直接摆到底，反正已经负到没朋友了！"
                show_popup("摆烂彩蛋", easter_egg)
        else:
            title, encouragement = get_title_by_experience(new_total_exp)
            show_popup("称号生成", f'您当前的称号是："{title}级"自律者！\n{encouragement}\n当前总经验：{new_total_exp}点')

        self.back_to_home()

    def view_experience(self, *args):
        """查看经验值"""
        total_exp = get_total_experience()
        if total_exp < 0:
            if total_exp >= -200:
                curse_list = CURSE_MESSAGES["light"]
            elif total_exp >= -1000:
                curse_list = CURSE_MESSAGES["medium"]
            else:
                curse_list = CURSE_MESSAGES["heavy"]

            random_curse = random.choice(curse_list)
            curse_msg = (
                f"⚠️ 紧急警告！⚠️\n"
                f"你的经验值：{total_exp}点（负得离谱！）\n\n"
                f"{random_curse}\n\n"
                "👉 赶紧去完成任务把经验涨回来，不然系统要拉黑你了！"
            )
            show_popup(f"摆烂警告 | 经验负数{total_exp}点", curse_msg)

            if total_exp < -2000:
                easter_egg = "🐣 彩蛋：建议你改名为“摆烂之王”，申请专利算了！"
                show_popup("摆烂彩蛋", easter_egg)
            return

        title, encouragement = get_title_by_experience(total_exp)
        msg = f"当前经验值：{total_exp}点\n当前称号：{title}级自律者\n{encouragement}"
        show_popup("经验信息", msg)

    def view_unmet_count(self, *args):
        """查看连续不达标次数"""
        count = get_continuous_unmet_count()
        show_popup("连续不达标次数", f"您当前的连续不达标次数为：{count}次")

    def back_to_home(self, *args):
        """返回首页"""
        self.clear_widgets()
        self.__init__()


# ===================== APP入口 =====================
class SelfDisciplineApp(App):
    def build(self):
        # 设置窗口大小（适配安卓）
        Window.size = (400, 700)
        Config.set('graphics', 'resizable', False)
        self.title = "自律管理器 1.2"
        return MainLayout()


if __name__ == "__main__":

    SelfDisciplineApp().run()
