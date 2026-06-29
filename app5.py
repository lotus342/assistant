import hashlib
import json
import random
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

import pandas as pd
import streamlit as st


st.set_page_config(page_title="食愈小助手", layout="wide")

APP_DIR = Path(__file__).resolve().parent
USERS_FILE = APP_DIR / "users.json"
HISTORY_FILE = APP_DIR / "meal_history.json"
FEEDBACK_FILE = APP_DIR / "feedback.json"
FOOD_STYLE_PATH = APP_DIR / "assets" / "food_style.png"

PAGES = ["用户信息填写", "营养计算", "三餐推荐", "食材库", "个人健康报告", "用户反馈", "历史记录"]
MEALS = {"breakfast": "早餐", "lunch": "午餐", "dinner": "晚餐", "snack": "加餐"}
SCENES = ["居家做饭", "食堂简餐", "外卖为主", "办公室带饭", "外出通勤", "便利店/超市", "用户自定义"]
TARGETS = ["减脂减重", "增肌塑形", "维持健康", "控糖降压", "养胃调理"]
TASTES = ["清淡少油", "正常口味", "想吃丰富一点但尽量健康", "重口味但想健康一点", "用户自填"]
DISEASES = [
    "糖尿病", "高血压", "高血脂", "高尿酸/痛风", "慢性胃炎", "胃食管反流", "脂肪肝", "肾病",
    "贫血", "甲状腺疾病", "乳糖不耐受", "海鲜过敏", "坚果过敏", "麸质敏感", "肠易激综合征",
    "孕期/哺乳", "术后恢复", "用户自填"
]


BASE_FOODS = [
    ("鸡蛋", "蛋白质", 143, 13, 1, 10, "早餐/加餐", "鸡蛋过敏"),
    ("鹌鹑蛋", "蛋白质", 160, 13, 2, 11, "早餐/加餐", "蛋类过敏"),
    ("鸡胸肉", "肉类", 118, 23, 0, 2, "减脂/增肌", "无"),
    ("鸡腿肉", "肉类", 181, 18, 0, 11, "食堂/外卖", "去皮更好"),
    ("瘦牛肉", "肉类", 125, 20, 0, 5, "增肌/盖饭", "高尿酸少量"),
    ("猪里脊", "肉类", 155, 20, 0, 8, "家常菜", "控脂少量"),
    ("鸭胸肉", "肉类", 201, 19, 0, 13, "食堂/居家", "控脂少量"),
    ("鸡肉丸", "肉类", 185, 16, 8, 10, "外卖/麻辣烫", "注意钠含量"),
    ("鳕鱼", "水产", 88, 18, 0, 1, "晚餐/清蒸", "海鲜过敏"),
    ("鲈鱼", "水产", 105, 19, 0, 3, "清蒸/食堂", "海鲜过敏"),
    ("三文鱼", "水产", 208, 20, 0, 13, "轻食/增肌", "海鲜过敏"),
    ("虾仁", "水产", 99, 21, 1, 1, "轻食/汤面", "海鲜过敏"),
    ("金枪鱼", "水产", 132, 28, 0, 1, "三明治/轻食", "海鲜过敏"),
    ("北豆腐", "豆制品", 85, 8, 3, 4, "家常菜/汤", "痛风急性期少量"),
    ("嫩豆腐", "豆制品", 55, 5, 2, 3, "汤/麻辣烫", "痛风急性期少量"),
    ("豆干", "豆制品", 140, 16, 8, 5, "食堂/控压", "注意盐分"),
    ("鹰嘴豆", "豆制品", 164, 9, 27, 3, "沙拉/轻食", "痛风少量"),
    ("无糖豆浆", "饮品", 35, 3, 2, 2, "早餐/控糖", "大豆过敏"),
    ("低脂牛奶", "饮品", 45, 3, 5, 2, "早餐/增肌", "乳糖不耐受"),
    ("无糖酸奶", "奶制品", 70, 5, 6, 3, "早餐/加餐", "乳糖不耐受"),
    ("燕麦", "主食", 377, 13, 66, 7, "早餐/控糖", "无"),
    ("全麦面包", "主食", 246, 9, 43, 4, "三明治", "麸质敏感"),
    ("杂粮饭", "主食", 110, 3, 23, 1, "食堂/外卖", "胃病少量"),
    ("糙米饭", "主食", 116, 3, 24, 1, "轻食碗", "胃病少量"),
    ("米饭", "主食", 130, 3, 28, 0, "食堂/外卖", "控糖半份"),
    ("荞麦面", "主食", 115, 5, 24, 1, "面食/控糖", "无"),
    ("意面", "主食", 158, 6, 31, 1, "外卖/居家", "控糖控制量"),
    ("红薯", "主食", 86, 2, 20, 0, "早餐/晚餐", "胃胀少量"),
    ("玉米", "主食", 112, 4, 22, 1, "食堂/便利店", "胃病少量"),
    ("小米粥", "主食", 46, 1, 10, 0, "养胃", "糖尿病控制量"),
    ("南瓜粥", "主食", 52, 2, 11, 0, "养胃/外卖", "糖尿病控制量"),
    ("紫米饭团", "主食", 210, 6, 42, 3, "便利店/早餐", "控糖控制量"),
    ("西兰花", "蔬菜", 36, 4, 5, 1, "减脂餐", "无"),
    ("菠菜", "蔬菜", 28, 3, 4, 0, "控压/汤菜", "肾结石少量"),
    ("番茄", "蔬菜", 20, 1, 4, 0, "炒蛋/汤", "胃酸多少量"),
    ("黄瓜", "蔬菜", 16, 1, 3, 0, "凉拌/轻食", "胃病少生冷"),
    ("生菜", "蔬菜", 15, 1, 3, 0, "沙拉/卷饼", "胃病少生冷"),
    ("胡萝卜", "蔬菜", 41, 1, 10, 0, "配菜/炖菜", "无"),
    ("南瓜", "蔬菜", 26, 1, 6, 0, "养胃/蒸菜", "糖尿病控制量"),
    ("菌菇", "蔬菜", 24, 3, 4, 0, "汤/麻辣烫", "痛风少量"),
    ("娃娃菜", "蔬菜", 13, 1, 3, 0, "蒸菜/外卖", "无"),
    ("油麦菜", "蔬菜", 15, 1, 2, 0, "食堂/居家", "无"),
    ("芹菜", "蔬菜", 16, 1, 4, 0, "控压/食堂", "无"),
    ("海带", "蔬菜", 13, 1, 3, 0, "汤/凉拌", "甲状腺问题谨慎"),
    ("苹果", "水果", 52, 0, 14, 0, "加餐", "控糖半个"),
    ("香蕉", "水果", 89, 1, 23, 0, "运动前后", "糖尿病少量"),
    ("蓝莓", "水果", 57, 1, 14, 0, "早餐/酸奶杯", "无"),
    ("橙子", "水果", 47, 1, 12, 0, "加餐", "胃酸多少量"),
    ("猕猴桃", "水果", 61, 1, 15, 1, "加餐", "胃酸多少量"),
    ("坚果", "坚果", 600, 20, 15, 52, "加餐", "减脂限量"),
    ("牛油果", "水果", 160, 2, 9, 15, "轻食/早餐", "减脂限量"),
]

POPULAR_DISHES = [
    ("鸡胸肉轻食碗", "外卖美食", 620, 45, 65, 18, "外卖为主", "酱料分装"),
    ("照烧鸡肉饭", "外卖美食", 650, 42, 72, 19, "外卖为主", "少酱米饭半份"),
    ("麻辣烫健康版", "外卖美食", 590, 34, 42, 24, "外卖为主", "胃病少吃辣汤"),
    ("蒸菜套餐", "外卖美食", 610, 42, 58, 20, "外卖为主", "少油少盐"),
    ("南瓜小米粥套餐", "外卖美食", 420, 18, 60, 10, "外卖为主/养胃", "控糖少量"),
    ("荞麦牛肉面", "外卖美食", 760, 44, 92, 21, "外卖为主/增肌", "少喝汤"),
    ("鸡肉卷饼", "外卖美食", 560, 36, 70, 14, "外卖为主/早餐", "少沙拉酱"),
    ("全麦三明治", "外卖美食", 440, 27, 46, 16, "外卖为主/早餐", "不加糖饮料"),
    ("砂锅粥", "外卖美食", 520, 26, 72, 12, "外卖为主/养胃", "控糖少量"),
    ("寿司便当", "外卖美食", 620, 26, 90, 15, "外卖为主", "控糖少量"),
    ("烤鸡腿饭", "外卖美食", 700, 45, 80, 22, "外卖为主/食堂", "去皮少酱"),
    ("番茄牛腩饭", "美食", 720, 38, 88, 23, "居家/外卖", "高尿酸少量"),
    ("鱼香肉丝盖饭", "美食", 820, 30, 98, 32, "食堂/外卖", "少油少汁"),
    ("黄焖鸡米饭", "美食", 780, 40, 86, 28, "外卖为主", "少汤汁"),
    ("牛肉沙拉", "外卖美食", 560, 38, 36, 27, "外卖为主/轻食", "高尿酸少量"),
    ("虾仁意面", "美食", 690, 34, 88, 20, "居家/外卖", "海鲜过敏避开"),
    ("豆腐菌菇汤面", "美食", 560, 28, 72, 15, "居家/食堂", "痛风少量"),
    ("番茄鸡蛋面", "美食", 580, 24, 82, 16, "居家/食堂", "鸡蛋过敏避开"),
    ("鸡蛋灌饼健康版", "美食", 520, 22, 58, 22, "外卖为主/早餐", "少酱少油"),
    ("紫菜饭团", "外卖美食", 360, 12, 60, 8, "便利店/早餐", "控糖控制量"),
]


def init_json(path, default):
    if not path.exists():
        path.write_text(json.dumps(default, ensure_ascii=False, indent=2), encoding="utf-8")


def load_json(path, default):
    init_json(path, default)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def save_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def password_hash(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def build_food_db():
    rows = []
    for item in BASE_FOODS + POPULAR_DISHES:
        rows.append({"名称": item[0], "类别": item[1], "热量kcal": item[2], "蛋白质g": item[3], "碳水g": item[4], "脂肪g": item[5], "适合场景": item[6], "注意": item[7]})
    methods = ["清蒸", "水煮", "少油快炒", "炖煮", "烤制", "凉拌", "番茄风味", "黑椒风味", "蒜香风味", "咖喱风味", "椒盐少油", "葱香", "菌菇汤底", "低脂酱烤"]
    staples = ["配杂粮饭", "配糙米饭", "配荞麦面", "配红薯", "配玉米", "配全麦面包", "配小米粥", "配紫米饭团"]
    proteins = [x for x in BASE_FOODS if x[1] in ["肉类", "水产", "豆制品", "蛋白质"]]
    vegs = [x for x in BASE_FOODS if x[1] == "蔬菜"]
    for p in proteins:
        for v in vegs:
            for m in methods:
                rows.append({"名称": f"{m}{p[0]}{v[0]}组合", "类别": "组合菜", "热量kcal": round(p[2] + v[2] + (20 if "炒" in m or "烤" in m else 6)), "蛋白质g": round(p[3] + v[3], 1), "碳水g": round(p[4] + v[4], 1), "脂肪g": round(p[5] + v[5] + (2 if "炒" in m or "烤" in m else 0), 1), "适合场景": "居家做饭/食堂简餐", "注意": f"{p[7]}；{v[7]}"})
    for p in proteins:
        for s in staples:
            rows.append({"名称": f"{p[0]}{s}套餐", "类别": "套餐", "热量kcal": round(p[2] + 180), "蛋白质g": round(p[3] + 5, 1), "碳水g": round(p[4] + 38, 1), "脂肪g": round(p[5] + 2, 1), "适合场景": "外卖为主/食堂简餐/便利店", "注意": p[7]})
    return rows


FOOD_DB = build_food_db()


def recipe(meal, title, scene, targets, tastes, avoid, foods, source, fallback, health, heat, protein, carb, fat, tags, emoji, tip):
    return {"meal": meal, "title": title, "scene": scene, "targets": targets, "tastes": tastes, "avoid": avoid, "foods": foods, "source": source, "fallback": fallback, "health": health, "heat": heat, "protein": protein, "carb": carb, "fat": fat, "tags": tags, "emoji": emoji, "tip": tip}


RECIPES = [
    # ===== 早餐 =====
    recipe("breakfast", "晨光燕麦碗", "居家做饭", ["减脂减重", "控糖降压", "维持健康"], ["清淡少油", "正常口味"], [], ["燕麦40g", "水煮蛋1个", "无糖豆浆250ml", "蓝莓一小把"], "家里备燕麦、鸡蛋、无糖豆浆", "买不到蓝莓时换半个苹果；蛋白不够时加1个鸡蛋", "高纤维主食+优质蛋白，控制糖油", 410, 24, 48, 13, ["燕麦", "鸡蛋", "豆浆"], "🥣", "升糖平稳，适合早八和久坐学习。"),
    recipe("breakfast", "玉米豆浆能量站", "食堂简餐", ["减脂减重", "控糖降压", "维持健康"], ["清淡少油", "正常口味"], [], ["无糖豆浆1杯", "茶叶蛋1个", "玉米半根", "黄瓜少量"], "食堂早餐窗口", "没有玉米就换红薯半个；没有豆浆就换无糖牛奶", "少油少糖，主食不过量", 360, 20, 43, 11, ["豆浆", "鸡蛋", "玉米"], "🌽", "比油条包子组合更稳。"),
    recipe("breakfast", "全麦三明治轻启", "外卖为主", ["减脂减重", "维持健康"], ["清淡少油", "正常口味"], [], ["鸡蛋全麦三明治", "无糖豆浆", "小番茄一份"], "外卖轻食店、便利店", "买不到三明治时：茶叶蛋2个+饭团半个+无糖豆浆", "酱料少、饮料无糖、蛋白质足", 440, 27, 46, 16, ["三明治", "鸡蛋", "豆浆"], "🥪", "点外卖备注少酱、不要含糖饮料。"),
    recipe("breakfast", "南瓜小米粥暖身", "外卖为主", ["养胃调理", "维持健康"], ["清淡少油"], [], ["南瓜小米粥", "蒸蛋", "青菜包半个"], "粥店、早餐外卖", "没有蒸蛋时加茶叶蛋；没有青菜包就换玉米半根", "热软清淡，减少生冷辛辣", 380, 17, 58, 9, ["小米", "南瓜", "鸡蛋"], "🥣", "选热粥热菜，少冰饮和辣味。"),
    recipe("breakfast", "紫米饭团元气盒", "便利店/超市", ["减脂减重", "维持健康"], ["正常口味"], [], ["紫米饭团1个", "茶叶蛋1个", "无糖豆浆1杯"], "便利店早餐柜", "没有饭团就换全麦三明治；没有豆浆换无糖牛奶", "粗粮主食+蛋白，便利店也能健康吃", 420, 22, 52, 14, ["紫米", "鸡蛋", "豆浆"], "🍙", "便利店早餐优选组合，避开油炸饼类。"),
    recipe("breakfast", "红薯鸡蛋暖胃盘", "居家做饭", ["养胃调理", "控糖降压"], ["清淡少油"], [], ["红薯1个（中）", "水煮蛋1个", "小米粥1碗", "小番茄几颗"], "家里蒸红薯、煮鸡蛋", "没有红薯换玉米；没有小米换燕麦粥", "粗粮暖胃，膳食纤维丰富", 390, 19, 55, 10, ["红薯", "鸡蛋", "小米"], "🍠", "蒸红薯比烤红薯更健康，少糖油。"),
    recipe("breakfast", "荞麦面清汤晨食", "居家做饭", ["控糖降压", "维持健康"], ["清淡少油"], [], ["荞麦面60g", "荷包蛋1个", "青菜少量", "清汤底"], "家里煮面", "没有荞麦面换意面；没有青菜换黄瓜丝", "低GI主食，控糖友好", 380, 21, 48, 12, ["荞麦", "鸡蛋", "青菜"], "🍜", "清汤面比炒面少油，适合控糖人群。"),
    recipe("breakfast", "意式番茄烘蛋", "居家做饭", ["增肌塑形", "维持健康"], ["正常口味"], [], ["鸡蛋2个", "番茄半个", "全麦面包1片", "橄榄油少量"], "家里平底锅", "没有全麦面包换玉米半根；没有番茄换彩椒", "高蛋白+番茄红素，增肌友好", 450, 28, 38, 22, ["鸡蛋", "番茄", "全麦"], "🍳", "意式做法少油，番茄炒蛋升级版。"),

    # ===== 午餐 =====
    recipe("lunch", "糙米鸡胸彩虹盘", "居家做饭", ["减脂减重", "控糖降压", "维持健康"], ["清淡少油"], [], ["糙米饭100g", "香煎鸡胸肉120g", "西兰花150g", "胡萝卜80g"], "家里备餐", "没有鸡胸肉换鸡蛋2个或豆腐150g；没有糙米换玉米半根", "蛋白质足、主食定量、蔬菜足", 620, 46, 70, 16, ["糙米", "鸡胸肉", "西兰花"], "🍱", "适合提前备餐。"),
    recipe("lunch", "杂粮饭清蒸鱼时蔬", "食堂简餐", ["减脂减重", "控糖降压"], ["清淡少油"], [], ["杂粮饭半份", "清蒸鱼或鸡胸肉", "西兰花", "番茄炒蛋少油"], "食堂窗口", "没有清蒸鱼就选鸡蛋豆腐；没有杂粮饭就米饭半份", "避开油炸，先菜后蛋白再主食", 610, 43, 62, 18, ["杂粮", "鱼", "西兰花"], "🐟", "跳过油炸窗口，青菜至少两拳。"),
    recipe("lunch", "蒸鸡腿杂粮南瓜碗", "外卖为主", ["控糖降压", "减脂减重"], ["清淡少油"], [], ["蒸鸡腿去皮", "杂粮饭半份", "蒸南瓜少量", "绿叶菜双份"], "蒸菜外卖、健康餐外卖", "没有蒸菜店时：便利店鸡胸肉+玉米半根+无糖豆浆+沙拉", "蒸煮少油盐，主食半份", 610, 42, 58, 20, ["鸡腿", "杂粮", "南瓜"], "🍱", "备注少油少盐，不点含糖饮料。"),
    recipe("lunch", "荞麦牛肉青菜面", "外卖为主", ["增肌塑形", "维持健康"], ["正常口味", "重口味但想健康一点"], ["高尿酸/痛风"], ["荞麦面", "牛肉加量", "青菜加量", "汤少喝"], "面馆外卖", "没有牛肉面时选鸡肉饭少酱；汤面不可得时选轻食碗", "蛋白加量、少喝汤减少盐", 760, 44, 92, 21, ["荞麦", "牛肉", "青菜"], "🍜", "重口味可以吃，但少喝汤减少盐摄入。"),
    recipe("lunch", "红薯鸡胸轻食盒", "外卖为主", ["减脂减重", "维持健康"], ["清淡少油"], [], ["烤红薯1个", "鸡胸肉100g", "生菜沙拉", "油醋汁"], "轻食外卖", "没有红薯换玉米；没有油醋汁换柠檬汁", "粗粮主食+ lean蛋白，饱腹感强", 580, 42, 58, 18, ["红薯", "鸡胸肉", "生菜"], "🥗", "轻食碗自己搭配，避开高热量酱料。"),
    recipe("lunch", "玉米虾仁豆腐煲", "居家做饭", ["减脂减重", "维持健康"], ["清淡少油"], ["海鲜过敏"], ["玉米1根", "虾仁100g", "嫩豆腐150g", "菌菇少量"], "家里做煲", "没有虾仁换鸡胸肉；海鲜过敏换豆腐+鸡蛋", "高蛋白低脂，玉米替代米饭", 520, 38, 48, 16, ["玉米", "虾仁", "豆腐"], "🍲", "玉米当主食，比米饭更有饱腹感。"),
    recipe("lunch", "意面番茄肉酱轻量", "居家做饭", ["维持健康", "增肌塑形"], ["正常口味"], [], ["意面80g", "瘦牛肉末80g", "番茄酱汁", "西兰花"], "家里煮意面", "没有意面换荞麦面；没有牛肉换鸡胸肉", "低GI主食，西餐也能健康吃", 680, 38, 78, 22, ["意面", "牛肉", "番茄"], "🍝", "意面比中式面条升糖慢，适合控糖。"),
    recipe("lunch", "紫米三文鱼波奇碗", "外卖为主", ["增肌塑形", "维持健康"], ["正常口味"], ["海鲜过敏"], ["紫米饭100g", "三文鱼100g", "牛油果半个", "黄瓜海草"], "轻食店、日料店", "没有三文鱼换金枪鱼；海鲜过敏换鸡胸肉", "优质脂肪+蛋白，增肌优选", 720, 42, 55, 38, ["紫米", "三文鱼", "牛油果"], "🥙", "波奇碗选刺身级鱼，避开油炸天妇罗。"),

    # ===== 晚餐 =====
    recipe("dinner", "鳕鱼豆腐蔬菜汤", "居家做饭", ["减脂减重", "控糖降压", "维持健康"], ["清淡少油"], ["海鲜过敏"], ["鳕鱼100g", "豆腐100g", "青菜200g", "玉米半根"], "家里做汤", "没有鳕鱼换鸡胸肉100g；海鲜过敏换豆腐+鸡蛋", "晚餐少油但保留蛋白质", 480, 36, 38, 15, ["鳕鱼", "豆腐", "玉米"], "🍲", "晚餐少油但保留蛋白质。"),
    recipe("dinner", "豆腐蒸蛋小米粥", "食堂简餐", ["养胃调理", "维持健康", "减脂减重"], ["清淡少油"], ["鸡蛋过敏"], ["家常豆腐少油", "蒸蛋", "熟青菜", "小米粥小碗"], "食堂热菜窗口", "没有蒸蛋就换鸡肉或豆腐；没有小米粥就米饭半份", "热软熟食，减少凉拌辣菜", 500, 26, 56, 16, ["豆腐", "鸡蛋", "小米"], "🍲", "选熟菜，不要凉拌辣菜。"),
    recipe("dinner", "清汤麻辣烫自选", "外卖为主", ["维持健康", "减脂减重"], ["重口味但想健康一点", "正常口味"], ["胃病"], ["清汤麻辣烫", "鸡蛋/鸡胸肉", "豆腐", "青菜菌菇", "不喝汤"], "麻辣烫外卖", "没有清汤就换蒸菜套餐；胃病用户换粥+蒸蛋", "清汤、少丸子、不喝汤，减少油盐", 590, 34, 42, 24, ["麻辣烫", "豆腐", "青菜"], "🍢", "选清汤、少丸子、不喝汤。"),
    recipe("dinner", "照烧鸡肉饭轻量", "外卖为主", ["增肌塑形", "维持健康"], ["正常口味"], [], ["照烧鸡肉饭少酱", "米饭半份", "蔬菜加量", "无糖茶"], "日式简餐外卖", "没有日式饭时选烤鸡腿饭去皮少酱或轻食鸡肉碗", "主食半份、少酱、蔬菜加量", 650, 42, 72, 19, ["鸡肉", "米饭", "蔬菜"], "🍱", "备注少酱，米饭吃半份。"),
    recipe("dinner", "燕麦南瓜蒸蛋盅", "居家做饭", ["减脂减重", "控糖降压"], ["清淡少油"], ["鸡蛋过敏"], ["燕麦30g", "南瓜100g", "鸡蛋1个", "牛奶少量"], "家里蒸锅", "没有鸡蛋换豆腐；没有燕麦换小米", "燕麦替代米饭，晚餐轻负担", 420, 22, 48, 14, ["燕麦", "南瓜", "鸡蛋"], "🎃", "燕麦当晚餐主食，比米饭热量低。"),
    recipe("dinner", "荞麦面菌菇豆腐汤", "居家做饭", ["减脂减重", "控糖降压"], ["清淡少油"], ["痛风"], ["荞麦面60g", "北豆腐100g", "菌菇100g", "青菜少量"], "家里煮面", "没有荞麦面换意面；痛风换鸡蛋", "低GI主食+植物蛋白，清淡饱腹", 460, 28, 52, 14, ["荞麦", "豆腐", "菌菇"], "🍜", "荞麦面晚餐吃，升糖慢不易饿。"),
    recipe("dinner", "红薯鸡胸肉温沙拉", "居家做饭", ["减脂减重", "维持健康"], ["清淡少油"], [], ["红薯1个", "鸡胸肉100g", "生菜", "油醋汁少量"], "家里烤箱/蒸锅", "没有红薯换玉米；没有生菜换黄瓜", "温沙拉比冷沙拉更适合中国胃", 520, 38, 52, 16, ["红薯", "鸡胸肉", "生菜"], "🥗", "温沙拉冬天吃更舒服，不刺激胃。"),
    recipe("dinner", "紫米杂粮粥配蛋", "居家做饭", ["养胃调理", "控糖降压"], ["清淡少油"], [], ["紫米杂粮粥1碗", "水煮蛋1个", "凉拌黄瓜", "少量豆腐干"], "家里电饭煲", "没有紫米换小米；没有豆腐干换青菜", "杂粮粥养胃，晚餐好消化", 440, 24, 58, 12, ["紫米", "鸡蛋", "黄瓜"], "🥣", "杂粮粥提前泡，电饭煲预约更省事。"),

    # ===== 加餐 =====
    recipe("snack", "苹果酸奶小食", "居家做饭", ["减脂减重", "控糖降压", "维持健康"], ["清淡少油", "正常口味"], ["乳糖不耐受"], ["苹果半个", "无糖酸奶100g"], "家里或便利店", "乳糖不耐受换无糖豆浆；控糖用户苹果半个", "控制零食热量，避免甜点奶茶", 150, 6, 24, 3, ["苹果", "酸奶"], "🍎", "下午饿时吃，不放睡前。"),
    recipe("snack", "坚果酸奶能量包", "外卖为主", ["维持健康", "增肌塑形"], ["正常口味"], ["乳糖不耐受", "坚果过敏"], ["无糖酸奶1杯", "原味坚果10g"], "便利店/超市", "坚果过敏换茶叶蛋；乳糖不耐受换无糖豆浆", "小份坚果，控制脂肪摄入", 210, 10, 14, 12, ["酸奶", "坚果"], "🥜", "坚果只吃一小把。"),
    recipe("snack", "玉米段蛋白加餐", "食堂简餐", ["减脂减重", "维持健康"], ["清淡少油"], [], ["玉米半根", "茶叶蛋1个"], "食堂小卖部", "没有玉米换红薯；没有茶叶蛋换无糖豆浆", "粗粮+蛋白，加餐不超标", 180, 12, 22, 6, ["玉米", "鸡蛋"], "🌽", "食堂加餐最实惠组合。"),
    recipe("snack", "蓝莓燕麦杯", "居家做饭", ["减脂减重", "控糖降压"], ["清淡少油"], [], ["燕麦20g", "蓝莓一小把", "无糖酸奶50g"], "家里备料", "没有蓝莓换苹果；没有酸奶换豆浆", "低卡高纤，解馋不胖", 140, 5, 22, 3, ["燕麦", "蓝莓", "酸奶"], "🫐", "燕麦杯提前做，冷藏当甜品吃。"),
]


def setup_style():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap');

    .stApp { 
        background: linear-gradient(160deg, #fff0f5 0%, #f0f8ff 25%, #fff8f0 50%, #f5fff5 75%, #fff5f8 100%); 
        color: #3d2b2b; 
        font-family: 'Nunito', 'Microsoft YaHei', sans-serif;
    }

    .block-container { max-width: 1400px; padding-top: 0.5rem; }

    /* 侧边栏 - 毛玻璃效果 */
    section[data-testid="stSidebar"] > div { 
        background: rgba(255,255,255,0.85) !important; 
        backdrop-filter: blur(20px);
        border-right: 2px solid rgba(255,182,193,0.3);
    }

    /* 标题字体 */
    h1, h2, h3 { font-family: 'Nunito', 'Microsoft YaHei', sans-serif; letter-spacing: -0.5px; }

    /* ===== HERO 区域 - 可爱渐变卡片 ===== */
    .hero {
        background: linear-gradient(135deg, #ffd6e0 0%, #ffe4e1 30%, #e6f3ff 70%, #d4f1f4 100%);
        border-radius: 24px;
        padding: 32px 36px;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px rgba(255,182,193,0.25), 0 4px 16px rgba(135,206,235,0.15);
        border: 2px solid rgba(255,255,255,0.6);
        position: relative;
        overflow: hidden;
    }
    .hero::before {
        content: "🌸";
        position: absolute;
        top: -10px;
        right: 20px;
        font-size: 80px;
        opacity: 0.15;
        transform: rotate(15deg);
    }
    .hero::after {
        content: "🥑";
        position: absolute;
        bottom: -15px;
        left: 30px;
        font-size: 70px;
        opacity: 0.12;
        transform: rotate(-10deg);
    }
    .hero h1 { 
        margin: 0; 
        font-size: 42px; 
        font-weight: 900;
        background: linear-gradient(135deg, #ff6b8a, #ff8e53, #4ecdc4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: none;
    }
    .hero p { 
        margin: 12px 0 0; 
        color: #8b6f7a; 
        font-size: 16px;
        font-weight: 600;
    }

    /* ===== PANEL 面板 - 毛玻璃 ===== */
    .panel {
        background: rgba(255,255,255,0.75);
        backdrop-filter: blur(16px);
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 20px;
        border: 1.5px solid rgba(255,182,193,0.25);
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    }
    .panel h2 {
        color: #5a4a4a;
        font-weight: 800;
        font-size: 24px;
        margin-bottom: 8px;
    }
    .panel p {
        color: #8b7a7a;
        font-size: 14px;
    }

    /* ===== METRIC 指标卡 - 彩色渐变 ===== */
    .metric {
        background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(255,255,255,0.6));
        border-radius: 20px;
        padding: 20px;
        min-height: 130px;
        border: 2px solid transparent;
        background-clip: padding-box;
        position: relative;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .metric:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    .metric:nth-child(1) { border-image: linear-gradient(135deg, #ff9a9e, #fecfef) 1; }
    .metric:nth-child(2) { border-image: linear-gradient(135deg, #a8edea, #fed6e3) 1; }
    .metric:nth-child(3) { border-image: linear-gradient(135deg, #d299c2, #fef9d7) 1; }
    .metric:nth-child(4) { border-image: linear-gradient(135deg, #89f7fe, #66a6ff) 1; }

    .metric span { 
        color: #9a8a8a; 
        font-size: 13px; 
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .metric b { 
        display: block; 
        margin-top: 12px; 
        font-size: 32px; 
        color: #ff6b8a;
        font-weight: 900;
    }

    /* ===== DISH 菜品卡 - 可爱圆角 + 悬浮效果 ===== */
    .dish {
        background: rgba(255,255,255,0.85);
        backdrop-filter: blur(12px);
        border-radius: 24px;
        overflow: hidden;
        min-height: 620px;
        border: 2px solid rgba(255,182,193,0.2);
        box-shadow: 0 6px 24px rgba(0,0,0,0.06);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .dish:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 16px 48px rgba(255,107,138,0.2);
        border-color: rgba(255,182,193,0.5);
    }
    .dish img { 
        width: 100%; 
        height: 160px; 
        object-fit: cover; 
        display: block;
        border-bottom: 3px solid rgba(255,182,193,0.3);
    }
    .dish-body { padding: 20px; }

    /* 标签 pill - 可爱圆角 */
    .pill { 
        display: inline-block; 
        padding: 6px 14px; 
        border-radius: 999px; 
        background: linear-gradient(135deg, #ffe4e1, #ffd6e0); 
        color: #d4587a; 
        font-size: 12px; 
        font-weight: 800; 
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(255,107,138,0.15);
        border: 1px solid rgba(255,182,193,0.3);
    }

    /* 菜品标题 */
    .dish-title { 
        font-size: 20px; 
        font-weight: 900; 
        line-height: 1.4; 
        margin-bottom: 10px;
        color: #4a3a3a;
    }

    /* 食材列表 */
    .foods { 
        margin: 0 0 12px 20px; 
        padding: 0; 
        line-height: 1.8; 
        font-size: 14px;
        color: #6a5a5a;
    }
    .foods li::marker { color: #ff9a9e; }

    /* 营养成分 - 彩色小卡片 */
    .nutri { 
        display: grid; 
        grid-template-columns: 1fr 1fr; 
        gap: 10px; 
        margin: 14px 0; 
    }
    .nutri div { 
        background: linear-gradient(135deg, #fff5e6, #ffe4e1); 
        padding: 10px 12px; 
        border-radius: 14px; 
        font-size: 13px; 
        color: #7a5a4a;
        font-weight: 700;
        border: 1px solid rgba(255,182,193,0.2);
        text-align: center;
    }
    .nutri div b {
        color: #ff6b8a;
        font-size: 18px;
    }

    /* 提示框 - 可爱粉色 */
    .tip { 
        background: linear-gradient(135deg, #fff0f5, #ffe4e1); 
        color: #7a5a6a; 
        border-radius: 14px; 
        padding: 12px 14px; 
        line-height: 1.6; 
        font-size: 13px; 
        margin-top: 10px;
        border: 1px solid rgba(255,182,193,0.3);
        border-left: 4px solid #ff9a9e;
    }

    /* 小字信息 */
    .small { 
        color: #9a8a8a; 
        font-size: 12px; 
        margin-top: 10px; 
        line-height: 1.6;
        background: rgba(255,255,255,0.5);
        padding: 10px;
        border-radius: 12px;
    }

    /* 按钮 - 可爱渐变 */
    .stButton > button { 
        width: 100%; 
        border-radius: 16px; 
        border: 0; 
        background: linear-gradient(135deg, #ff9a9e, #fecfef, #ff6b8a); 
        color: #fff; 
        font-weight: 900;
        font-size: 15px;
        padding: 12px;
        box-shadow: 0 4px 15px rgba(255,107,138,0.3);
        transition: all 0.3s ease;
        text-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    .stButton > button:hover { 
        background: linear-gradient(135deg, #ff6b8a, #ff9a9e, #fecfef); 
        color: #fff;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255,107,138,0.4);
    }

    /* 侧边栏按钮 */
    section[data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(135deg, #a8edea, #fed6e3);
        color: #5a4a4a;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    }

    /* 单选框美化 */
    .stRadio > div { gap: 8px; }
    .stRadio label {
        background: rgba(255,255,255,0.6);
        border-radius: 12px;
        padding: 6px 12px;
        border: 1.5px solid rgba(255,182,193,0.2);
    }

    /* 输入框美化 */
    .stTextInput > div > div, .stNumberInput > div > div {
        border-radius: 14px !important;
        border: 2px solid rgba(255,182,193,0.3) !important;
    }

    /* 复选框美化 */
    .stCheckbox > label {
        background: rgba(255,255,255,0.5);
        border-radius: 10px;
        padding: 4px 10px;
    }

    /* 滚动条美化 */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: rgba(255,182,193,0.1); border-radius: 10px; }
    ::-webkit-scrollbar-thumb { background: linear-gradient(135deg, #ff9a9e, #fecfef); border-radius: 10px; }

    /* 动画效果 */
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    @keyframes wiggle {
        0%, 100% { transform: rotate(0deg); }
        25% { transform: rotate(-3deg); }
        75% { transform: rotate(3deg); }
    }
    </style>
    """, unsafe_allow_html=True)

def calc_bmi(height, weight):
    bmi = weight / ((height / 100) ** 2)
    if bmi < 18.5:
        level = "偏瘦"
    elif bmi < 24:
        level = "标准健康"
    elif bmi < 28:
        level = "超重"
    else:
        level = "肥胖"
    return round(bmi, 2), level


def calc_bmr(gender, age, height, weight):
    return 10 * weight + 6.25 * height - 5 * age + (5 if gender == "男" else -161)


def calc_tdee(bmr, active):
    return round(bmr * {"久坐为主": 1.2, "轻度活动": 1.375, "中度运动": 1.55, "高强度运动": 1.725}.get(active, 1.2))


def target_cal(tdee, target):
    if target == "减脂减重":
        return max(1200, tdee - 400)
    if target == "增肌塑形":
        return tdee + 300
    if target in ["控糖降压", "养胃调理"]:
        return max(1200, tdee - 200)
    return tdee


def macro_split(cal, target):
    if target == "减脂减重":
        p, c, f = .30, .35, .35
    elif target == "增肌塑形":
        p, c, f = .30, .50, .20
    elif target == "控糖降压":
        p, c, f = .27, .38, .35
    else:
        p, c, f = .25, .45, .30
    return round(cal * p / 4), round(cal * c / 4), round(cal * f / 9)


def user_signature(user):
    return json.dumps(user, ensure_ascii=False, sort_keys=True)


def seed_value(*parts):
    return int(hashlib.sha256("|".join(map(str, parts)).encode("utf-8")).hexdigest()[:12], 16)


def parse_list(text):
    return [x.strip() for x in text.replace("，", ",").split(",") if x.strip()]


def auth_page():
    st.markdown('<div class="hero"><h1>🌸 欢迎来到食愈小助手 🥑</h1><p>✨ 登录后开启你的专属健康饮食之旅 ✨</p></div>', unsafe_allow_html=True)
    users = load_json(USERS_FILE, {})
    tab_login, tab_register = st.tabs(["登录", "注册"])
    with tab_login:
        username = st.text_input("用户名", key="login_user")
        password = st.text_input("密码", type="password", key="login_pwd")
        if st.button("登录"):
            if username in users and users[username]["password"] == password_hash(password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("登录成功")
                st.rerun()
            else:
                st.error("用户名或密码错误")
    with tab_register:
        new_user = st.text_input("注册用户名")
        new_pwd = st.text_input("注册密码", type="password")
        if st.button("注册"):
            if not new_user or not new_pwd:
                st.warning("请输入用户名和密码")
            elif new_user in users:
                st.error("用户名已存在")
            else:
                users[new_user] = {"password": password_hash(new_pwd), "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")}
                save_json(USERS_FILE, users)
                st.success("注册成功，请返回登录")


def safe_for_user(r, user, strict_scene=True, strict_target=True):
    scene_text = user["scene"] + " " + user["custom_scene"]
    if strict_scene and r["scene"] != user["scene"] and user["scene"] != "用户自定义":
        return False
    if strict_target and user["target"] not in r["targets"]:
        return False
    if user["taste"] == "清淡少油" and "清淡少油" not in r["tastes"]:
        return False
    if any(d in r["avoid"] for d in user["disease"]):
        return False
    text = r["title"] + " " + " ".join(r["foods"]) + " " + " ".join(r["tags"])
    if any(x and x in text for x in user["hate"]):
        return False
    if any(word in scene_text for word in ["便利店", "超市", "赶车", "宿舍"]) and r["scene"] == "居家做饭":
        return False
    return True


MEAL_VARIANTS = {
    "breakfast": [
        ("·鲜果缤纷", ["苹果半个", "蓝莓一小把"], 45, 0, 11, 0, ["水果", "维生素"]),
        ("·蛋白加倍", ["水煮蛋1个", "无糖豆浆半杯"], 105, 10, 3, 6, ["高蛋白", "耐饿"]),
        ("·玉米能量", ["玉米半根", "小番茄几颗"], 90, 4, 18, 1, ["粗粮", "便携"]),
        ("·红薯暖身", ["红薯半个", "温豆浆1杯"], 85, 5, 16, 2, ["粗粮", "暖胃"]),
        ("·紫米元气", ["紫米饭团半个", "无糖茶"], 110, 4, 22, 2, ["粗粮", "低GI"]),
    ],
    "lunch": [
        ("·蔬菜加倍", ["清炒时蔬半份", "紫菜蛋花汤"], 95, 5, 10, 4, ["蔬菜", "高纤"]),
        ("·红薯主食", ["红薯1个替米饭", "青菜加量"], 40, 2, 10, 0, ["粗粮", "控碳"]),
        ("·玉米饱腹", ["玉米1根替米饭", "豆腐加量"], 55, 6, 10, 1, ["粗粮", "植物蛋白"]),
        ("·荞麦面版", ["荞麦面替米饭", "汤少喝"], 30, 2, 6, 0, ["低GI", "面食"]),
        ("·紫米杂粮", ["紫米饭替白米饭", "坚果5g"], 65, 3, 10, 3, ["粗粮", "抗氧化"]),
    ],
    "dinner": [
        ("·燕麦轻食", ["燕麦30g替主食", "牛奶少量"], 70, 4, 10, 2, ["低GI", "轻负担"]),
        ("·红薯暖胃", ["红薯1个替米饭", "温汤一碗"], 60, 2, 14, 0, ["粗粮", "暖胃"]),
        ("·小米粥版", ["小米粥替米饭", "蒸蛋半份"], 50, 5, 8, 1, ["养胃", "好消化"]),
        ("·荞麦面版", ["荞麦面60g替米饭", "青菜加量"], 45, 3, 8, 1, ["低GI", "面食"]),
        ("·玉米饱腹", ["玉米半根替米饭", "菌菇加量"], 55, 3, 12, 1, ["粗粮", "高纤"]),
    ],
    "snack": [
        ("·水果清新", ["橙子半个", "猕猴桃半个"], 55, 1, 13, 0, ["水果", "维C"]),
        ("·坚果能量", ["原味坚果10g"], 65, 2, 2, 6, ["坚果", "优质脂肪"]),
        ("·酸奶蛋白", ["无糖酸奶100g"], 70, 5, 7, 2, ["酸奶", "蛋白"]),
        ("·玉米便携", ["玉米小段", "无糖茶"], 55, 3, 10, 1, ["粗粮", "便携"]),
        ("·燕麦杯", ["燕麦20g", "蓝莓少量"], 50, 2, 8, 1, ["高纤", "低卡"]),
    ],
}


def expand_recipe_variants(recipes):
    expanded = []
    for r in recipes:
        expanded.append(r)
        variants = MEAL_VARIANTS.get(r["meal"], [])
        # 随机打乱变体顺序，每次不同
        shuffled_variants = variants[:]
        random.shuffle(shuffled_variants)
        # 每个菜品只随机取1-2个变体，不要全部展开
        num_variants = random.randint(1, min(2, len(shuffled_variants)))
        for suffix, foods, heat, protein, carb, fat, tags in shuffled_variants[:num_variants]:
            item = dict(r)
            item["title"] = f'{r["title"]}{suffix}'
            item["foods"] = list(r["foods"]) + foods
            item["heat"] = int(r["heat"] + heat)
            item["protein"] = int(r["protein"] + protein)
            item["carb"] = int(r["carb"] + carb)
            item["fat"] = int(r["fat"] + fat)
            item["tags"] = list(dict.fromkeys(list(r["tags"]) + tags))
            item["tip"] = f'{r["tip"]} 🔄 主食已轮换，粗粮搭配更健康。'
            expanded.append(item)
    return expanded





# ===== 智能三餐推荐系统 =====
# 从食材库动态组合生成推荐

MEAL_RULES = {
    "breakfast": {
        "combos": [
            ("{staple}+{protein}", 1.0),
            ("{staple}配{protein}", 1.0),
            ("{protein}配{staple}", 0.8),
        ],
        "required": ["主食", "蛋白质"],
        "optional": ["饮品"],
        "staple_amount": 0.6,
        "protein_amount": 1.0,
        "veg_amount": 0,
        "emoji_pool": ["🌅", "☀️", "🥐", "🍳", "🥣"]
    },
    "lunch": {
        "combos": [
            ("{staple}+{protein}+{veg}", 1.0),
            ("{protein}炒{veg}配{staple}", 0.8),
            ("{protein}烧{veg}配{staple}", 0.7),
            ("{veg}炒{protein}配{staple}", 0.6),
            ("{protein}炖{veg}配{staple}", 0.5),
        ],
        "required": ["主食", "蛋白质", "蔬菜"],
        "optional": ["汤"],
        "staple_amount": 1.0,
        "protein_amount": 1.0,
        "veg_amount": 1.0,
        "emoji_pool": ["🌿", "🍱", "🥗", "🍜"]
    },
    "dinner": {
        "combos": [
            ("{protein}+{veg}", 1.0),
            ("{protein}炒{veg}", 0.9),
            ("{veg}炒{protein}", 0.8),
            ("{protein}汤配{veg}", 0.6),
            ("{staple}配{protein}和{veg}", 0.5),
        ],
        "required": ["蛋白质", "蔬菜"],
        "optional": ["主食", "汤"],
        "staple_amount": 0.5,
        "protein_amount": 0.8,
        "veg_amount": 1.0,
        "emoji_pool": ["🌙", "🍲", "🥣", "🌸"]
    },
    "snack": {
        "combos": [
            ("{fruit}", 1.0),
            ("{fruit}+{protein}", 0.7),
            ("{protein}小食", 0.5),
        ],
        "required": ["水果"],
        "optional": ["蛋白质", "坚果"],
        "staple_amount": 0,
        "protein_amount": 0.5,
        "veg_amount": 0,
        "emoji_pool": ["✨", "🍎", "🥜", "🫐"]
    }
}

def filter_foods_by_scene(foods, scene, user_diseases, user_hates):
    """根据用户场景和限制筛选食材"""
    filtered = []
    for food in foods:
        name, category, heat, pro, carb, fat, food_scene, warning = food

        # 检查疾病禁忌
        skip = False
        for disease in user_diseases:
            if disease and disease in warning:
                skip = True
                break
        if skip:
            continue

        # 检查不吃食材
        for hate in user_hates:
            if hate and hate in name:
                skip = True
                break
        if skip:
            continue

        # 场景匹配：检查食材的适合场景是否包含用户场景关键词
        scene_match = False
        if scene == "用户自定义":
            scene_match = True
        elif scene in food_scene or any(keyword in food_scene for keyword in scene.split("/")):
            scene_match = True
        elif "居家" in scene and "居家" in food_scene:
            scene_match = True
        elif "食堂" in scene and ("食堂" in food_scene or "家常菜" in food_scene):
            scene_match = True
        elif "外卖" in scene and ("外卖" in food_scene or "轻食" in food_scene or "美食" in food_scene):
            scene_match = True
        elif "便利店" in scene and ("便利店" in food_scene or "早餐" in food_scene):
            scene_match = True
        elif "通勤" in scene and ("便携" in food_scene or "早餐" in food_scene):
            scene_match = True
        elif "带饭" in scene and ("家常菜" in food_scene or "汤" in food_scene):
            scene_match = True

        # 通用食材（如鸡蛋、燕麦）所有场景都可用
        if not scene_match and ("早餐" in food_scene or "加餐" in food_scene or "无" in warning):
            scene_match = True

        if scene_match:
            filtered.append(food)

    return filtered


def pick_foods_for_meal(meal_type, scene, user_diseases, user_hates, used_foods, rng):
    """为某一餐随机挑选食材组合"""
    rules = MEAL_RULES[meal_type]

    # 按类别分组筛选食材
    staples = filter_foods_by_scene([f for f in BASE_FOODS if f[1] == "主食"], scene, user_diseases, user_hates)
    proteins = filter_foods_by_scene([f for f in BASE_FOODS if f[1] in ["蛋白质", "肉类", "水产", "豆制品"]], scene, user_diseases, user_hates)
    vegs = filter_foods_by_scene([f for f in BASE_FOODS if f[1] == "蔬菜"], scene, user_diseases, user_hates)
    fruits = filter_foods_by_scene([f for f in BASE_FOODS if f[1] == "水果"], scene, user_diseases, user_hates)
    nuts = filter_foods_by_scene([f for f in BASE_FOODS if f[1] == "坚果"], scene, user_diseases, user_hates)
    drinks = filter_foods_by_scene([f for f in BASE_FOODS if f[1] in ["饮品", "奶制品"]], scene, user_diseases, user_hates)

    # 排除最近用过的食材
    def exclude_used(pool):
        return [f for f in pool if f[0] not in used_foods]

    staples = exclude_used(staples) or staples
    proteins = exclude_used(proteins) or proteins
    vegs = exclude_used(vegs) or vegs
    fruits = exclude_used(fruits) or fruits

    picked = {}
    foods_list = []
    total_heat = 0
    total_pro = 0
    total_carb = 0
    total_fat = 0
    tags = []

    # 挑选主食
    if rules["staple_amount"] > 0 and staples:
        s = rng.choice(staples)
        amount = rules["staple_amount"]
        picked["staple"] = s
        if "燕麦" in s[0]:
            foods_list.append(f"燕麦粥一碗")
        elif "米饭" in s[0] or "饭" in s[0]:
            foods_list.append(f"米饭一碗")
        elif "红薯" in s[0]:
            foods_list.append(f"红薯一个")
        elif "玉米" in s[0]:
            foods_list.append(f"玉米一根")
        elif "面条" in s[0] or "面" in s[0]:
            foods_list.append(f"面条一碗")
        elif "面包" in s[0]:
            foods_list.append(f"全麦面包一片")
        elif "粥" in s[0]:
            foods_list.append(f"{s[0]}一碗")
        elif "饭团" in s[0]:
            foods_list.append(f"饭团一个")
        elif "馒头" in s[0]:
            foods_list.append(f"馒头一个")
        else:
            foods_list.append(f"{s[0]}适量")
        total_heat += s[2] * amount
        total_pro += s[3] * amount
        total_carb += s[4] * amount
        total_fat += s[5] * amount
        tags.append(s[0])
        used_foods.add(s[0])

    # 挑选蛋白质
    if proteins:
        p = rng.choice(proteins)
        amount = rules["protein_amount"]
        picked["protein"] = p
        if "鸡胸肉" in p[0]:
            foods_list.append(f"鸡胸肉一份")
        elif "鸡腿" in p[0]:
            foods_list.append(f"鸡腿一个(去皮)")
        elif "牛肉" in p[0]:
            foods_list.append(f"牛肉一份")
        elif "猪肉" in p[0]:
            foods_list.append(f"瘦肉一份")
        elif "鱼" in p[0]:
            foods_list.append(f"{p[0]}一份")
        elif "虾仁" in p[0]:
            foods_list.append(f"虾仁一份")
        elif "豆腐" in p[0]:
            foods_list.append(f"{p[0]}一块")
        elif "鸡蛋" in p[0] or "蛋" in p[0]:
            foods_list.append(f"鸡蛋一个")
        elif "豆浆" in p[0]:
            foods_list.append(f"豆浆一杯")
        elif "牛奶" in p[0]:
            foods_list.append(f"牛奶一杯")
        elif "酸奶" in p[0]:
            foods_list.append(f"酸奶一杯")
        else:
            foods_list.append(f"{p[0]}适量")
        total_heat += p[2] * amount
        total_pro += p[3] * amount
        total_carb += p[4] * amount
        total_fat += p[5] * amount
        tags.append(p[0])
        used_foods.add(p[0])

    # 挑选蔬菜
    if rules["veg_amount"] > 0 and vegs:
        v = rng.choice(vegs)
        amount = rules["veg_amount"]
        picked["veg"] = v
        if "西兰花" in v[0]:
            foods_list.append(f"西兰花一份")
        elif "菠菜" in v[0]:
            foods_list.append(f"菠菜一份")
        elif "番茄" in v[0]:
            foods_list.append(f"番茄炒蛋" if "鸡蛋" in str(picked.get("protein", "")) else f"番茄一份")
        elif "黄瓜" in v[0]:
            foods_list.append(f"黄瓜一份")
        elif "生菜" in v[0]:
            foods_list.append(f"生菜一份")
        elif "胡萝卜" in v[0]:
            foods_list.append(f"胡萝卜一份")
        elif "南瓜" in v[0]:
            foods_list.append(f"南瓜一份")
        elif "菌菇" in v[0]:
            foods_list.append(f"菌菇一份")
        elif "白菜" in v[0] or "娃娃菜" in v[0]:
            foods_list.append(f"{v[0]}一份")
        elif "芹菜" in v[0]:
            foods_list.append(f"芹菜一份")
        elif "海带" in v[0]:
            foods_list.append(f"海带一份")
        else:
            foods_list.append(f"{v[0]}一份")
        total_heat += v[2] * amount
        total_pro += v[3] * amount
        total_carb += v[4] * amount
        total_fat += v[5] * amount
        tags.append(v[0])
        used_foods.add(v[0])

    # 随机挑选可选食材
    picked_optional = {}
    if fruits and rng.random() > 0.3:
        f = rng.choice(fruits)
        picked_optional["fruit"] = f
        if "苹果" in f[0]:
            foods_list.append(f"苹果一个")
        elif "香蕉" in f[0]:
            foods_list.append(f"香蕉一根")
        elif "橙子" in f[0]:
            foods_list.append(f"橙子一个")
        elif "猕猴桃" in f[0]:
            foods_list.append(f"猕猴桃一个")
        elif "蓝莓" in f[0]:
            foods_list.append(f"蓝莓一小把")
        else:
            foods_list.append(f"{f[0]}一个")
        total_heat += f[2] * 0.5
        total_pro += f[3] * 0.5
        total_carb += f[4] * 0.5
        total_fat += f[5] * 0.5
        tags.append(f[0])
        used_foods.add(f[0])

    if drinks and rng.random() > 0.4:
        d = rng.choice(drinks)
        picked_optional["drink"] = d
        foods_list.append(f"{d[0]}一杯")
        total_heat += d[2]
        total_pro += d[3]
        total_carb += d[4]
        total_fat += d[5]
        tags.append(d[0])
        used_foods.add(d[0])

    if nuts and rng.random() > 0.7:
        n = rng.choice(nuts)
        picked_optional["nut"] = n
        foods_list.append(f"坚果一小把")
        total_heat += n[2] * 0.1
        total_pro += n[3] * 0.1
        total_carb += n[4] * 0.1
        total_fat += n[5] * 0.1
        tags.append(n[0])
        used_foods.add(n[0])

    # 生成菜名 - 用日常说法
    combo_template, _ = rng.choice(rules["combos"])
    staple_name = picked.get("staple", ("",))[0] if "staple" in picked else ""
    protein_name = picked.get("protein", ("",))[0] if "protein" in picked else ""
    veg_name = picked.get("veg", ("",))[0] if "veg" in picked else ""

    # 简化食材名称用于菜名
    def simplify_name(name):
        if not name:
            return ""
        # 去掉修饰词，保留核心食材
        simple = name.replace("无糖", "").replace("低脂", "").replace("瘦", "").replace("嫩", "").replace("北", "").replace("家常", "")
        return simple

    s_name = simplify_name(staple_name)
    p_name = simplify_name(protein_name)
    v_name = simplify_name(veg_name)

    # 替换占位符
    title = combo_template
    title = title.replace("{staple}", s_name)
    title = title.replace("{protein}", p_name)
    title = title.replace("{veg}", v_name)

    # 清理并优化菜名
    title = title.replace("++", "+").replace("+", "+").strip("+")
    if title.startswith("+"):
        title = title[1:]
    if title.endswith("+"):
        title = title[:-1]

    # 如果标题为空或太简单，用默认格式
    if not title or title == "+" or len(title) < 3:
        if meal_type == "breakfast":
            title = f"{s_name}配{p_name}" if s_name and p_name else f"{p_name}早餐" if p_name else "营养早餐"
        elif meal_type == "lunch":
            title = f"{p_name}配{s_name}" if p_name and s_name else f"{p_name}套餐" if p_name else "午餐套餐"
        elif meal_type == "dinner":
            title = f"{p_name}配{v_name}" if p_name and v_name else f"{p_name}晚餐" if p_name else "清淡晚餐"
        else:
            title = f"{p_name}小食" if p_name else "健康加餐"

    emoji = rng.choice(rules["emoji_pool"])

    # 生成健康提示
    health_parts = []
    if protein_name:
        health_parts.append(f"{p_name}补充蛋白质")
    if staple_name:
        health_parts.append(f"{s_name}提供能量")
    if veg_name:
        health_parts.append(f"{v_name}增加膳食纤维")
    health = "，".join(health_parts) if health_parts else "营养均衡，清淡少油"

    # 生成替代建议
    fallback_parts = []
    if protein_name:
        fallback_parts.append(f"没有{p_name}可以换鸡蛋或豆腐")
    if staple_name:
        fallback_parts.append(f"没有{s_name}可以换米饭或面条")
    if veg_name:
        fallback_parts.append(f"没有{v_name}可以换其他绿叶菜")
    fallback = "；".join(fallback_parts) if fallback_parts else "按「一荤一素一主食」自由搭配"

    # 生成小贴士
    tips = [
        "细嚼慢咽，七分饱就好",
        "先吃蔬菜，再吃蛋白质，最后吃主食",
        "少油少盐，清淡更健康",
        "多喝水，餐前半小时喝一杯",
        "饭后散步15分钟，帮助消化"
    ]
    tip = f"{emoji} {rng.choice(tips)}"

    return {
        "meal": meal_type,
        "title": f"{emoji} {title}",
        "scene": scene,
        "targets": ["维持健康", "减脂减重"],
        "tastes": ["清淡少油"],
        "avoid": [],
        "foods": foods_list,
        "source": f"{scene}常见食材",
        "fallback": fallback,
        "health": health,
        "heat": round(total_heat),
        "protein": round(total_pro, 1),
        "carb": round(total_carb, 1),
        "fat": round(total_fat, 1),
        "tags": tags,
        "emoji": emoji,
        "tip": tip
    }

def generate_dynamic_plan(user, include_snack=True):
    """动态生成三餐推荐，每次完全不同"""
    # 完全随机种子
    rng = random.Random()

    scene = user.get("scene", "用户自定义")
    diseases = user.get("disease", [])
    hates = user.get("hate", [])

    # 记录已用食材，避免重复
    used_foods = set()

    plan = {}
    meal_order = ["breakfast", "lunch", "dinner"]
    if include_snack:
        meal_order.append("snack")

    for meal in meal_order:
        dish = pick_foods_for_meal(meal, scene, diseases, hates, used_foods, rng)
        plan[meal] = dish

    st.session_state.current_plan = plan
    return plan

def candidate_recipes(meal, user):
    base = [r for r in RECIPES if r["meal"] == meal]
    for strict_scene, strict_target in [(True, True), (True, False), (False, True), (False, False)]:
        pool = [r for r in base if safe_for_user(r, user, strict_scene, strict_target)]
        if pool:
            return expand_recipe_variants(pool)
    return expand_recipe_variants(base)


def generate_plan(user, include_snack=True):
    sig = user_signature(user)
    if st.session_state.get("last_user_signature") != sig:
        st.session_state.last_user_signature = sig
        st.session_state.plan_round = st.session_state.get("plan_round", 0) + 1
        st.session_state.used_titles = []
        st.session_state.used_titles_by_meal = {}
        st.session_state.pop("current_plan", None)

    # 完全随机种子 - 每次点击都完全不同
    rng = random.Random()

    used_today = set(st.session_state.get("used_titles", []))
    used_by_meal = st.session_state.get("used_titles_by_meal", {})
    plan = {}

    # 餐次固定顺序展示，但内部选择完全随机
    meal_order = ["breakfast", "lunch", "dinner"] + (["snack"] if include_snack else [])

    for meal in meal_order:
        pool = candidate_recipes(meal, user)
        meal_used = set(used_by_meal.get(meal, []))

        # 先排除今天已经用过的
        fresh = [r for r in pool if r["title"] not in used_today]
        if not fresh:
            fresh = pool[:]  # 如果都用过，全部放开

        # 再排除这个餐次最近用过的（但只排除最近3个，不要太严格）
        recent_used = list(meal_used)[-3:]
        candidates = [r for r in fresh if r["title"] not in recent_used]
        if not candidates:
            candidates = fresh[:]

        # 场景匹配的稍微优先一点，但权重很低
        # 主要依赖纯随机
        def sort_key(r):
            # 场景匹配：0=匹配, 1=不匹配（只是轻微影响）
            scene_match = 0 if r["scene"] == user["scene"] else 1
            # 完全随机因子（主导）
            rand = rng.random()
            return (scene_match, rand)

        candidates_shuffled = candidates[:]
        rng.shuffle(candidates_shuffled)  # 先彻底打乱

        # 然后轻微按场景排序（前30%的候选中场景匹配优先）
        candidates_shuffled.sort(key=sort_key)

        # 从前一半中纯随机选
        top_n = max(1, len(candidates_shuffled) // 2)
        picked = rng.choice(candidates_shuffled[:top_n])

        plan[meal] = picked
        used_today.add(picked["title"])
        used_by_meal.setdefault(meal, [])
        used_by_meal[meal] = (used_by_meal[meal] + [picked["title"]])[-10:]  # 只记最近10个

    st.session_state.used_titles = list(used_today)[-30:]  # 只记最近30个
    st.session_state.used_titles_by_meal = used_by_meal
    st.session_state.current_plan = plan
    return plan



def image_uri(r):
    if FOOD_STYLE_PATH.exists():
        return "data:image/png;base64," + base64.b64encode(FOOD_STYLE_PATH.read_bytes()).decode("utf-8")

    # 更可爱的配色方案
    colors = {
        "breakfast": ("#ffe4e1", "#ffd6e0", "#ff9a9e"),   # 粉色系
        "lunch": ("#e8f5e9", "#c8e6c9", "#81c784"),       # 绿色系
        "dinner": ("#e3f2fd", "#bbdefb", "#64b5f6"),      # 蓝色系
        "snack": ("#fff3e0", "#ffe0b2", "#ffb74d")        # 橙色系
    }
    c1, c2, accent = colors.get(r["meal"], ("#ffe4e1", "#ffd6e0", "#ff9a9e"))

    # 餐次装饰元素
    deco = {
        "breakfast": ("☀️", "🥐", "🍳"),
        "lunch": ("🌿", "🍱", "🥗"),
        "dinner": ("🌙", "🍲", "🥣"),
        "snack": ("✨", "🍎", "🥜")
    }
    d = deco.get(r["meal"], ("✨", "🍽️", "🌸"))

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="720" height="420" viewBox="0 0 720 420">
    <defs>
        <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
            <stop stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/>
        </linearGradient>
        <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="4" stdDeviation="8" flood-color="{accent}" flood-opacity="0.2"/>
        </filter>
    </defs>
    <rect width="720" height="420" rx="34" fill="url(#g)"/>

    <!-- 可爱装饰圆点 -->
    <circle cx="80" cy="60" r="40" fill="{accent}" opacity="0.15"/>
    <circle cx="640" cy="360" r="60" fill="{accent}" opacity="0.1"/>
    <circle cx="650" cy="80" r="25" fill="{accent}" opacity="0.12"/>
    <circle cx="70" cy="350" r="35" fill="{accent}" opacity="0.08"/>

    <!-- 浮动小装饰 -->
    <text x="120" y="120" font-size="40" opacity="0.2">{d[0]}</text>
    <text x="580" y="300" font-size="50" opacity="0.15">{d[1]}</text>
    <text x="600" y="150" font-size="30" opacity="0.18">{d[2]}</text>

    <!-- 主内容区域 -->
    <ellipse cx="360" cy="225" rx="200" ry="120" fill="#fff" opacity="0.85" filter="url(#shadow)"/>
    <text x="360" y="210" text-anchor="middle" font-size="110">{r["emoji"]}</text>

    <!-- 标题 -->
    <text x="360" y="340" text-anchor="middle" font-size="32" font-family="Microsoft YaHei, Arial" font-weight="900" fill="#4a3a3a">{r["title"]}</text>
    <text x="360" y="375" text-anchor="middle" font-size="20" font-family="Microsoft YaHei, Arial" fill="#8a7a7a">{r["scene"]} · {MEALS[r["meal"]]}</text>

    <!-- 底部装饰线 -->
    <rect x="280" y="390" width="160" height="4" rx="2" fill="{accent}" opacity="0.4"/>
    </svg>"""
    return "data:image/svg+xml;charset=utf-8," + quote(svg)


def dish_card(r):
    foods = "".join(f"<li>{x}</li>" for x in r["foods"])
    # 根据餐次选择不同的装饰emoji和颜色
    decorations = {
        "breakfast": ("☀️", "🥐", "🍳"),
        "lunch": ("🌿", "🍱", "🥗"),
        "dinner": ("🌙", "🍲", "🥣"),
        "snack": ("✨", "🍎", "🥜")
    }
    deco = decorations.get(r["meal"], ("✨", "🍽️", "🌸"))

    return f"""<div class="dish">
    <img src="{image_uri(r)}" alt="{r["title"]}">
    <div class="dish-body">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
        <div class="pill">{MEALS[r["meal"]]} {deco[0]}</div>
        <span style="font-size:20px;">{deco[1]}</span>
    </div>
    <div class="dish-title">{deco[2]} {r["title"]}</div>
    <ul class="foods">{foods}</ul>
    <div class="nutri">
        <div>🔥 热量 <b>{r["heat"]}</b> kcal</div>
        <div>💪 蛋白质 <b>{r["protein"]}</b> g</div>
        <div>🌾 碳水 <b>{r["carb"]}</b> g</div>
        <div>🥑 脂肪 <b>{r["fat"]}</b> g</div>
    </div>
    <div class="tip"><b>🌟 健康保证：</b>{r["health"]}</div>
    <div class="small">
        <b>📍 食材来源：</b>{r["source"]}<br>
        <b>🔄 没有这道菜时：</b>{r["fallback"]}<br>
        <b>💡 提示：</b>{r["tip"]}
    </div>
    </div></div>"""

def sidebar_nav():
    with st.sidebar:
        st.markdown("<h1 style='text-align:center;'>🌸 食愈</h1>", unsafe_allow_html=True)
        st.caption(f"当前用户：{st.session_state.username}")
        page = st.radio("功能导航", PAGES)
        if st.button("退出登录"):
            st.session_state.logged_in = False
            st.rerun()
        st.caption("请先在“用户信息填写”中保存资料，再进入推荐功能。")
        return page


def default_profile():
    return {
        "gender": "男", "age": 22, "height": 170, "weight": 60.0, "active": "久坐为主",
        "target": "维持健康", "taste": "正常口味", "scene": "食堂简餐", "custom_scene": "",
        "disease": [], "hate": [], "bmi": 20.76, "bmi_level": "标准健康"
    }


def render_profile_form():
    st.markdown('<div class="panel"><h2>📝 个人信息卡</h2><p>登录后先填写身体状况、口味、基础疾病和真实用餐场景。保存后，其他功能会按这份信息自动推荐。</p></div>', unsafe_allow_html=True)
    current = st.session_state.get("user_profile", default_profile())
    with st.form("profile_form"):
        c1, c2 = st.columns(2)
        with c1:
            gender = st.radio("性别", ["男", "女"], horizontal=True, index=0 if current["gender"] == "男" else 1)
            age = st.number_input("年龄", 6, 100, int(current["age"]))
            height = st.number_input("身高 cm", 100, 230, int(current["height"]))
            weight = st.number_input("体重 kg", 25.0, 200.0, float(current["weight"]), step=0.5)
            active = st.radio("活动强度", ["久坐为主", "轻度活动", "中度运动", "高强度运动"], index=["久坐为主", "轻度活动", "中度运动", "高强度运动"].index(current.get("active", "久坐为主")))
            target = st.radio("健康目标", TARGETS, index=TARGETS.index(current.get("target", "维持健康")))
        with c2:
            taste_choice = st.multiselect("口味选择", TASTES, default=[current.get("taste", "正常口味")] if current.get("taste", "正常口味") in TASTES else ["用户自填"])
            taste_custom = st.text_input("自填口味", value="" if current.get("taste", "") in TASTES else current.get("taste", ""), placeholder="如：不吃辣、偏甜、想要汤面")
            disease_known = [d for d in current.get("disease", []) if d in DISEASES]
            disease_unknown = "，".join([d for d in current.get("disease", []) if d not in DISEASES])
            disease_choice = st.multiselect("基础疾病/健康限制", DISEASES, default=disease_known)
            disease_custom = st.text_input("自填疾病或限制", value=disease_unknown, placeholder="如：胆囊炎、贫血、医生要求低钾")
            scene = st.radio("日常用餐场景", SCENES, index=SCENES.index(current.get("scene", "食堂简餐")) if current.get("scene", "食堂简餐") in SCENES else 0)
            custom_scene = st.text_area("描述真实用餐场景", value=current.get("custom_scene", ""), placeholder="如：学校食堂只有盖饭和面；公司附近只有便利店；晚上只能点外卖。")
            hate = st.text_input("不吃的食材", value="，".join(current.get("hate", [])), placeholder="如：牛肉, 香菜, 海鲜")
        submitted = st.form_submit_button("保存用户信息")

    if submitted:
        bmi, level = calc_bmi(height, weight)
        taste = taste_custom if "用户自填" in taste_choice and taste_custom else (taste_choice[0] if taste_choice else "正常口味")
        disease = [d for d in disease_choice if d != "用户自填"] + parse_list(disease_custom)
        profile = {
            "gender": gender, "age": int(age), "height": int(height), "weight": float(weight),
            "active": active, "target": target, "taste": taste, "scene": scene, "custom_scene": custom_scene,
            "disease": disease, "hate": parse_list(hate), "bmi": bmi, "bmi_level": level
        }
        old_sig = st.session_state.get("last_user_signature")
        st.session_state.user_profile = profile
        if old_sig != user_signature(profile):
            st.session_state.plan_round = st.session_state.get("plan_round", 0) + 1
            st.session_state.pop("current_plan", None)
        st.success("用户信息已保存。用户信息发生变化后，三餐推荐会自动更新。")


def get_saved_profile():
    if "user_profile" not in st.session_state:
        return None
    return st.session_state.user_profile



def nutrition(user):
    bmr = calc_bmr(user["gender"], user["age"], user["height"], user["weight"])
    tdee = calc_tdee(bmr, user["active"])
    cal = target_cal(tdee, user["target"])
    pro, carb, fat = macro_split(cal, user["target"])
    return bmr, tdee, cal, pro, carb, fat


def render_metrics(user):
    st.markdown('<div class="panel"><h2>🧮 营养计算器</h2><p>这里不只给热量，还会给出 BMI、基础代谢、每日消耗、三大营养素比例、饮水量、运动消耗和今日饮食重点。</p></div>', unsafe_allow_html=True)
    bmr, tdee, cal, pro, carb, fat = nutrition(user)
    bmi = float(user.get("bmi", 0))
    water_min = round(user["weight"] * 30)
    water_max = round(user["weight"] * 35)
    fiber = 25 if user["gender"] == "女" else 30
    salt = 5
    sugar = 25
    disease_text = "、".join(user.get("disease", [])) if user.get("disease") else "暂无特殊疾病限制"

    st.subheader("📊 核心身体数据")
    cols = st.columns(4)
    core = [
        ("BMI", user["bmi"], user["bmi_level"], "🌸"),
        ("基础代谢 BMR", f"{round(bmr)} kcal", "身体静息消耗", "🔥"),
        ("每日消耗 TDEE", f"{tdee} kcal", user["active"], "⚡"),
        ("目标热量", f"{cal} kcal", user["target"], "🎯")
    ]
    for col, item in zip(cols, core):
        with col:
            st.markdown(f'<div class="metric"><span>{item[3]} {item[0]}</span><b>{item[1]}</b><span>{item[2]}</span></div>', unsafe_allow_html=True)

    st.subheader("🥗 三大营养素建议")
    cols = st.columns(3)
    macro_items = [
        ("💪 蛋白质", pro, "g", "鸡蛋、鱼虾、鸡胸肉、瘦牛肉、豆腐、牛奶"),
        ("🌾 碳水", carb, "g", "米饭、燕麦、玉米、红薯、全麦面包"),
        ("🥑 脂肪", fat, "g", "坚果、橄榄油、鱼类，少吃油炸")
    ]
    for col, item in zip(cols, macro_items):
        with col:
            st.markdown(f'<div class="metric"><span>{item[0]}</span><b>{item[1]}{item[2]}</b><span>{item[3]}</span></div>', unsafe_allow_html=True)

    st.subheader("💧 每日健康控制线")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.info(f"💧 饮水量：{water_min}-{water_max} ml/天")
    with c2:
        st.info(f"🌿 膳食纤维：约 {fiber} g/天")
    with c3:
        st.info(f"🧂 食盐：不超过 {salt} g/天")
    with c4:
        st.info(f"🍬 添加糖：不超过 {sugar} g/天")

    st.subheader("🍽️ 餐次分配建议")
    meal_rows = [{"餐次": "早餐", "热量比例": "25%", "建议热量": round(cal * 0.25), "重点": "补蛋白，别只喝奶茶或咖啡"}, {"餐次": "午餐", "热量比例": "40%", "建议热量": round(cal * 0.40), "重点": "主食+蛋白+蔬菜要完整"}, {"餐次": "晚餐", "热量比例": "30%", "建议热量": round(cal * 0.30), "重点": "少油少盐，别过量夜宵"}, {"餐次": "加餐", "热量比例": "5%", "建议热量": round(cal * 0.05), "重点": "水果、酸奶、坚果少量即可"}]
    st.dataframe(pd.DataFrame(meal_rows), use_container_width=True, hide_index=True)

    st.subheader("💝 个性化提醒")
    tips = []
    if bmi < 18.5:
        tips.append("BMI 偏低：不要过度控碳，三餐要保证主食和优质蛋白。")
    elif bmi >= 24:
        tips.append("BMI 偏高：优先控制油炸、含糖饮料和夜宵，主食定量。")
    else:
        tips.append("BMI 在较合理区间：重点保持规律三餐和稳定运动。")
    if "高血压" in disease_text:
        tips.append("有高血压限制：外卖和食堂都要备注少盐、少酱汁。")
    if "糖尿病" in disease_text or "控糖" in user.get("target", ""):
        tips.append("需要控糖：减少甜饮、甜点和精制主食，优先全谷物。")
    if user.get("scene") == "外卖点餐":
        tips.append("外卖场景：优先选轻食、盖饭少酱、汤粉少汤，额外加青菜。")
    for tip in tips:
        st.success(tip)


def render_plan(user):
    st.markdown('<div class="panel"><h2>🍱 今日美味推荐</h2><p>✨ 从食材库智能组合，每次点击都是全新的美味搭配 ✨</p></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 3])
    with c1:
        include_snack = st.checkbox("包含加餐", value=True, key="include_snack_plan")
    with c2:
        make_new = st.button("🎲 重新生成一组", key="new_meal_plan")

    # 点击重新生成时强制刷新
    if make_new:
        st.session_state.plan_round = st.session_state.get("plan_round", 0) + 1
        st.session_state.pop("current_plan", None)
        st.rerun()

    current_sig = user_signature(user)
    need_new = "current_plan" not in st.session_state or st.session_state.get("current_plan_signature") != current_sig
    if need_new:
        # 使用动态推荐系统
        plan = generate_dynamic_plan(user, include_snack)
        st.session_state.current_plan = plan
        st.session_state.current_plan_signature = current_sig
    else:
        plan = st.session_state.current_plan

    meals = ["breakfast", "lunch", "dinner"] + (["snack"] if include_snack and "snack" in plan else [])
    cols = st.columns(len(meals))
    for col, meal in zip(cols, meals):
        with col:
            st.markdown(dish_card(plan[meal]), unsafe_allow_html=True)

    st.info("🌟 小秘诀：每餐蛋白质约一掌心，主食半拳到一拳，蔬菜两拳~ 外卖买不到推荐菜时，按「蛋白 + 主食 + 蔬菜」结构替换就好啦！")

    # === 各场景沟通方案 ===
    scene_talks = {
        "食堂简餐": {
            "title": "🍽️ 食堂场景沟通话术",
            "lines": [
                "师傅，这份菜能不能少油少盐，汤汁少一点？",
                "米饭帮我打半份，青菜多一点。",
                "这个肉可以不要肥肉或者去皮吗？",
                "酱汁可以分开放吗？我自己加一点就行。",
                "我最近需要控糖/控压，能不能帮我选清蒸或水煮的菜？",
                "如果没有这道菜，我可以换成鸡蛋、豆腐或鸡胸肉吗？"
            ],
            "tip": "食堂健康原则：少油少盐、少汤汁、少油炸、主食半份、蔬菜双份、蛋白质一掌心。"
        },
        "外卖为主": {
            "title": "📱 外卖场景沟通话术",
            "lines": [
                "备注：少油少盐，酱汁分装，不要含糖饮料。",
                "米饭只要半份，多加一份青菜可以吗？",
                "鸡肉/鱼肉不要炸的，换成蒸或烤的做法。",
                "不要肥肉和皮，瘦肉多给一点。",
                "汤面的话，汤和面条分开装，我只吃一半面。",
                "如果有轻食/沙拉选项，酱料请单独放。"
            ],
            "tip": "外卖健康原则：看评分选店、优先轻食/蒸菜/汤类、备注少酱少油、主食减半、不喝含糖饮料。"
        },
        "居家做饭": {
            "title": "🏠 居家场景烹饪建议",
            "lines": [
                "用不粘锅可以减少一半用油量，或用喷油壶控制。",
                "肉类提前腌制（料酒+姜+少量酱油），减少后期加油。",
                "蔬菜优先蒸煮或水油焖，保留营养又低油。",
                "调味用天然香料（蒜、葱、姜、八角）代替部分盐和酱油。",
                "一锅出：电饭煲上层蒸菜、下层煮饭，省时省力。",
                "批量备餐：周末做好3天份，分装冷藏，工作日直接加热。"
            ],
            "tip": "居家健康原则：控油用不粘锅/喷油壶、少盐用香料替代、蒸煮优先、批量备餐省时。"
        },
        "办公室带饭": {
            "title": "🍱 带饭场景准备建议",
            "lines": [
                "前一天晚上做好，趁热装盒密封，放冰箱冷藏。",
                "蔬菜选耐热的（西兰花、胡萝卜、豆角），绿叶菜当天早上再烫。",
                "米饭和菜分开放，或者米饭铺底、菜盖上面，减少串味。",
                "带一个便携分格饭盒，蛋白质/主食/蔬菜各占一格。",
                "办公室备一瓶低钠酱油或油醋汁，吃的时候再调味。",
                "没有微波炉？用保温饭盒，早上装热食，中午还是温的。"
            ],
            "tip": "带饭健康原则：密封冷藏防变质、分格不串味、蔬菜选耐热的、自备低钠调味。"
        },
        "便利店/超市": {
            "title": "🏪 便利店/超市选购建议",
            "lines": [
                "优先：茶叶蛋/水煮蛋、无糖豆浆/牛奶、玉米/红薯、沙拉/三明治（不加酱）。",
                "避开：油炸食品、含糖饮料、加工肉制品（香肠/培根）、奶油面包。",
                "关东煮选：萝卜、海带、豆腐、鸡蛋，避开丸子和加工肉串。",
                "饭团选：金枪鱼/鸡肉饭团，避开蛋黄酱和油炸馅料。",
                "看配料表：钠含量超过每日30%的尽量少选。",
                "组合公式：1个蛋白（蛋/鸡胸肉）+ 1个主食（玉米/饭团）+ 1个蔬菜（沙拉/番茄）。"
            ],
            "tip": "便利店健康原则：蛋+粗粮+蔬菜组合、避开油炸和含糖、看钠含量、关东煮选天然食材。"
        },
        "外出通勤": {
            "title": "🚇 外出/通勤场景应对建议",
            "lines": [
                "早上出门带一个水煮蛋+小番茄，避免路上饿乱买。",
                "包里常备：原味坚果小包、无糖燕麦棒、独立包装鸡胸肉。",
                "赶时间时：便利店茶叶蛋+无糖豆浆+玉米，比煎饼果子健康。",
                "高铁站/机场：选蒸点（蒸饺/包子）而非油炸，配无糖茶。",
                "聚餐时：先吃蔬菜和汤，再吃蛋白质，最后吃主食，控制总量。",
                "出差住酒店：早餐优先鸡蛋+牛奶+蔬菜，避开油条和甜豆浆。"
            ],
            "tip": "通勤健康原则：随身备健康零食、赶时间选蒸煮类、聚餐先菜后肉再主食、酒店早餐避开油炸。"
        },
        "用户自定义": {
            "title": "🔧 自定义场景通用建议",
            "lines": [
                "无论什么场景，记住'蛋白+主食+蔬菜'铁三角结构。",
                "蛋白质来源：鸡蛋、豆腐、鱼虾、鸡胸肉、瘦牛肉轮换。",
                "主食选择：糙米、燕麦、红薯、玉米、荞麦面优于白米饭和白面。",
                "蔬菜目标：每餐至少两种颜色（深色+浅色），总量两拳。",
                "遇到不确定的食物：先看烹饪方式（蒸/煮/烤 > 炒 > 炸）。",
                "实在没得选时：鸡蛋+任意主食+任意蔬菜，就是最稳妥的组合。"
            ],
            "tip": "通用健康原则：铁三角结构、蛋白轮换、粗粮优先、蔬菜多彩、烹饪方式蒸煮优先。"
        }
    }

    user_scene = user.get("scene", "用户自定义")
    talk = scene_talks.get(user_scene, scene_talks["用户自定义"])

    with st.expander(talk["title"]):
        for line in talk["lines"]:
            st.code(line, language="text")
        st.info(talk["tip"])

    with st.expander("🤔 为什么这组推荐相对健康"):
        st.write("🎯 系统会根据你选择的用餐场景，从食材库中智能筛选合适的食材，再按「蛋白质+主食+蔬菜」的黄金比例随机组合。")
        st.write("🔄 每次点击「重新生成」都会从食材库中重新挑选，确保推荐新鲜不重复！")
        st.write("💡 如果实际场景买不到某道菜，优先换成同类型食物：鸡蛋/豆腐/鱼虾/鸡胸肉补蛋白，米饭/玉米/红薯补主食，青菜/菌菇/番茄补蔬菜。")

    if st.button("💾 收藏这组推荐", key="save_current_plan"):
        history = load_json(HISTORY_FILE, [])
        history.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "user": user, "plan": plan, "username": st.session_state.username})
        save_json(HISTORY_FILE, history)
        st.success("✨ 已收藏到美食回忆册啦！")


def render_food_db():
    st.markdown(f'<div class="panel"><h2>🍇 食材百宝箱</h2><p>当前食材库共 {len(FOOD_DB)} 种，包含基础食材、外卖美食、组合菜和套餐。</p></div>', unsafe_allow_html=True)
    keyword = st.text_input("搜索食材/美食/场景", placeholder="如：外卖、鸡胸肉、粥、低脂、麻辣烫")
    df = pd.DataFrame(FOOD_DB)
    if keyword:
        df = df[df.apply(lambda row: keyword in "".join(map(str, row.values)), axis=1)]
    st.dataframe(df, use_container_width=True, hide_index=True)


def render_report(user):
    st.markdown('<div class="panel"><h2>🧁 我的健康档案</h2><p>汇总当前身体状态、饮食目标、用餐场景、健康限制和饮食注意事项。</p></div>', unsafe_allow_html=True)
    _, _, cal, pro, carb, fat = nutrition(user)
    st.markdown(f"""<div class="metric" style="line-height:1.8">
    <b style="font-size:20px;color:#333;">个人概况</b><br>
    {user['gender']}，{user['age']}岁，{user['height']}cm，{user['weight']}kg，BMI {user['bmi']}（{user['bmi_level']}）。<br>
    目标：{user['target']}；口味：{user['taste']}；场景：{user['scene']}；真实描述：{user['custom_scene'] or '未填写'}。<br>
    建议：{cal} kcal；蛋白质 {pro}g，碳水 {carb}g，脂肪 {fat}g。
    </div>""", unsafe_allow_html=True)
    st.success("健康保证逻辑：疾病禁忌优先过滤；外卖少酱少汤少糖；食堂优先蒸煮炖；主食定量；每餐保证蛋白质和蔬菜；没有推荐菜时给出替代来源和摄入量。")
    if user["disease"]:
        st.warning("已考虑的限制：" + "、".join(user["disease"]))


def render_canteen_talk(user):
    st.markdown('<div class="panel"><h2>🍳 沟通小技巧</h2><p>食堂场景下，给厨师或窗口师傅的沟通话术。</p></div>', unsafe_allow_html=True)
    lines = [
        "师傅，这份菜能不能少油少盐，汤汁少一点？",
        "米饭帮我打半份，青菜多一点。",
        "这个肉可以不要肥肉/去皮吗？",
        "酱汁可以分开放吗？我自己加一点就行。",
        "我最近需要控糖/控压，能不能帮我选清蒸或水煮的菜？",
        "如果没有这道菜，我可以换成鸡蛋、豆腐或鸡胸肉吗？",
    ]
    for line in lines:
        st.code(line, language="text")
    st.info("食堂健康原则：少油少盐、少汤汁、少油炸、主食半份、蔬菜双份、蛋白质一掌心。")


def render_feedback(user):
    st.markdown('<div class="panel"><h2>💌 给我留言</h2><p>记录用户对推荐结果的满意度，方便后续优化。</p></div>', unsafe_allow_html=True)
    score = st.slider("这次推荐满意度", 1, 5, 4)
    text = st.text_area("反馈内容", placeholder="如：外卖推荐不太符合我学校附近情况；希望多推荐面食。")
    if st.button("提交反馈"):
        feedback = load_json(FEEDBACK_FILE, [])
        feedback.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "username": st.session_state.username, "score": score, "text": text, "user": user})
        save_json(FEEDBACK_FILE, feedback)
        st.success("💌 收到你的小心意啦，会努力改进的！")


def render_history():
    st.markdown('<div class="panel"><h2>📒 美食回忆册</h2><p>查看保存过的推荐菜单。</p></div>', unsafe_allow_html=True)
    history = load_json(HISTORY_FILE, [])
    mine = [h for h in history if h.get("username") == st.session_state.username]
    if not mine:
        st.info("还没有保存过推荐。")
        return
    for i, item in enumerate(reversed(mine), 1):
        with st.expander(f"记录 {i} · {item['time']}"):
            rows = [{"餐次": MEALS[k], "菜名": v["title"], "场景": v["scene"], "热量": v["heat"], "食材": "、".join(v["foods"])} for k, v in item["plan"].items()]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def main():
    setup_style()
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if not st.session_state.logged_in:
        auth_page()
        return
    page = sidebar_nav()
    st.markdown('<div class="hero"><h1>🌸 食愈小助手 🥑</h1><p>✨ 你的专属健康饮食管家 · 每一餐都是对自己的温柔照顾 ✨</p></div>', unsafe_allow_html=True)
    if page == "用户信息填写":
        render_profile_form()
        return
    user = get_saved_profile()
    if user is None:
        st.warning("请先进入“用户信息填写”保存资料，再使用其他功能。")
        render_profile_form()
        return
    if page == "营养计算":
        render_metrics(user)
    elif page == "三餐推荐":
        render_plan(user)
    elif page == "食材库":
        render_food_db()
    elif page == "个人健康报告":
        render_report(user)
    elif page == "用户反馈":
        render_feedback(user)
    elif page == "历史记录":
        render_history()


if __name__ == "__main__":
    main()