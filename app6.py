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
HISTORY_FILE = APP_DIR / "user_history.json"

SCENES = ["居家做饭", "食堂简餐", "外卖为主", "办公室带餐", "外出通勤"]
TARGETS = ["减脂减重", "增肌塑形", "维持健康", "控糖降压", "养胃调理"]
DISEASES = ["糖尿病", "高血压", "高尿酸/痛风", "乳糖不耐", "海鲜过敏", "胃病"]
TASTES = ["清淡少油", "正常口味", "想吃丰富一点但尽量健康", "重口味但想健康一点"]
MEAL_LABELS = {"breakfast": "早餐", "lunch": "午餐", "dinner": "晚餐", "snack": "加餐"}


def stable_int(text: str) -> int:
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:12], 16)


def ensure_history_file() -> None:
    if not HISTORY_FILE.exists():
        HISTORY_FILE.write_text("[]", encoding="utf-8")


def build_food_db() -> list[dict]:
    proteins = [
        "鸡胸肉", "鸡腿肉", "牛肉", "瘦猪肉", "里脊肉", "鸭胸肉", "火鸡胸", "羊肉片", "鸡蛋", "鹌鹑蛋",
        "虾仁", "鳕鱼", "三文鱼", "巴沙鱼", "金枪鱼", "带鱼", "鲈鱼", "龙利鱼", "蛤蜊", "扇贝",
        "豆腐", "嫩豆腐", "豆干", "腐竹", "毛豆", "鹰嘴豆", "黑豆", "红腰豆", "低脂牛奶", "无糖酸奶",
        "希腊酸奶", "无糖豆浆", "奶酪", "鸡肉丸", "牛肉丸", "鱼丸", "蟹柳", "午餐鸡肉片", "卤牛肉", "卤鸡腿",
    ]
    staples = [
        "白米饭", "糙米饭", "杂粮饭", "燕麦", "全麦面包", "贝果", "玉米", "红薯", "紫薯", "土豆",
        "山药", "小米粥", "南瓜粥", "荞麦面", "意面", "乌冬面", "米粉", "河粉", "藜麦", "全麦卷饼",
        "馒头", "花卷", "菜包", "鸡蛋饼", "煎饼", "寿司饭团", "燕麦粥", "黑米饭", "青稞饭", "玉米饼",
        "吐司", "苏打饼干", "魔芋面", "凉皮", "粉丝", "米线", "杂粮馒头", "窝头", "芋头", "莲藕",
    ]
    vegetables = [
        "西兰花", "菠菜", "生菜", "油麦菜", "娃娃菜", "上海青", "空心菜", "菜心", "芦笋", "秋葵",
        "黄瓜", "番茄", "胡萝卜", "白萝卜", "南瓜", "冬瓜", "茄子", "青椒", "彩椒", "洋葱",
        "西葫芦", "蘑菇", "香菇", "金针菇", "杏鲍菇", "海带", "紫菜", "木耳", "芹菜", "莴笋",
        "豆芽", "荷兰豆", "四季豆", "豌豆", "苦瓜", "丝瓜", "花菜", "包菜", "紫甘蓝", "玉米笋",
        "竹笋", "莲藕", "山药", "莴苣", "苋菜", "茼蒿", "韭菜", "蒜苗", "小白菜", "西芹",
    ]
    fruits = [
        "苹果", "香蕉", "蓝莓", "草莓", "橙子", "柚子", "猕猴桃", "梨", "桃子", "葡萄",
        "西瓜", "哈密瓜", "火龙果", "芒果", "菠萝", "樱桃", "李子", "木瓜", "牛油果", "石榴",
        "圣女果", "桑葚", "无花果", "椰子", "杨桃", "枇杷", "柠檬", "青提", "黑加仑", "覆盆子",
    ]
    snacks = [
        "原味坚果", "杏仁", "核桃", "腰果", "开心果", "花生", "奇亚籽", "亚麻籽", "黑芝麻", "海苔",
        "低糖蛋白棒", "全麦饼干", "低脂奶酪棒", "无糖豆乳", "冻干草莓", "烤红薯", "茶叶蛋", "即食鸡胸",
        "低脂肉脯", "低糖酸奶杯", "水果杯", "玉米杯", "关东煮萝卜", "关东煮豆腐", "银耳羹", "绿豆汤",
        "红豆汤", "燕麦奶", "无糖咖啡", "气泡水",
    ]
    cuisine_items = [
        "番茄牛腩", "照烧鸡腿", "黑椒牛柳", "香煎鳕鱼", "咖喱鸡肉", "鸡肉卷", "牛肉卷", "虾仁滑蛋",
        "番茄炒蛋", "青椒肉丝", "宫保鸡丁", "鱼香肉丝", "麻婆豆腐", "三杯鸡", "白灼虾", "清蒸鲈鱼",
        "菌菇鸡汤", "萝卜牛肉汤", "紫菜蛋花汤", "冬瓜丸子汤", "日式肥牛饭", "韩式拌饭", "越南春卷",
        "墨西哥鸡肉碗", "轻食沙拉", "寿司拼盘", "鸡肉汉堡", "牛肉汉堡", "披萨", "意式肉酱面",
        "泰式鸡肉饭", "沙县鸡腿饭", "兰州牛肉面", "云吞面", "潮汕粥", "麻辣烫", "冒菜", "烤肉饭",
        "黄焖鸡米饭", "卤肉饭", "盖浇饭", "水饺", "馄饨", "粥铺套餐", "轻食卷饼", "烤鱼套餐",
    ]
    drinks = [
        "白开水", "柠檬水", "无糖绿茶", "无糖乌龙茶", "黑咖啡", "拿铁少糖", "燕麦拿铁", "豆乳拿铁",
        "低糖酸梅汤", "银耳水", "薄荷水", "姜枣茶", "低糖椰子水", "苏打水", "无糖可可", "玉米须茶",
        "大麦茶", "菊花茶", "红茶", "普洱茶",
    ]
    groups = [
        ("蛋白质", proteins, 120, 20, 2, 4, "午餐/晚餐"),
        ("主食", staples, 150, 4, 30, 2, "早餐/午餐/晚餐"),
        ("蔬菜", vegetables, 35, 2, 6, 0.5, "午餐/晚餐"),
        ("水果", fruits, 60, 0.6, 15, 0.2, "加餐"),
        ("加餐", snacks, 180, 8, 16, 9, "加餐"),
        ("菜品", cuisine_items, 420, 25, 45, 15, "外卖/食堂/居家"),
        ("饮品", drinks, 30, 0.5, 5, 0, "饮品"),
    ]
    db = []
    for category, names, heat, protein, carb, fat, scene in groups:
        for idx, name in enumerate(names):
            db.append({
                "name": name,
                "category": category,
                "heat": max(5, heat + (idx % 9 - 4) * 7),
                "protein": max(0, round(protein + (idx % 7 - 3) * 0.8, 1)),
                "carb": max(0, round(carb + (idx % 8 - 3) * 2.2, 1)),
                "fat": max(0, round(fat + (idx % 6 - 2) * 0.9, 1)),
                "fiber": round((idx % 6) * 0.8, 1),
                "scene": scene,
                "fit": "通用/按量搭配",
                "avoid": "按个人过敏和疾病情况调整",
            })
    # More than 300 items: combine cooking methods with common bases.
    methods = ["清蒸", "香煎", "番茄", "黑椒", "菌菇", "咖喱", "照烧", "蒜香", "葱油", "椒盐", "低脂", "家常"]
    bases = ["鸡肉", "牛肉", "虾仁", "豆腐", "鱼片", "鸡蛋", "蘑菇", "花菜", "茄子", "土豆", "南瓜", "鳕鱼", "瘦肉", "鸡腿", "牛腩", "鱼丸", "豆皮", "鸡胸", "玉米", "藜麦"]
    for m in methods:
        for b in bases:
            name = f"{m}{b}"
            db.append({
                "name": name,
                "category": "组合菜",
                "heat": 260 + stable_int(name) % 210,
                "protein": round(10 + stable_int(name + "p") % 28, 1),
                "carb": round(8 + stable_int(name + "c") % 50, 1),
                "fat": round(4 + stable_int(name + "f") % 20, 1),
                "fiber": round(1 + stable_int(name + "x") % 6, 1),
                "scene": "居家/食堂/外卖",
                "fit": "丰富菜品",
                "avoid": "按用户忌口过滤",
            })
    return db


FOOD_DB = build_food_db()


RECIPES = [
    # Breakfast - home
    {"meal": "breakfast", "title": "燕麦蓝莓酸奶碗", "scene": ["居家做饭", "办公室带餐"], "targets": ["减脂减重", "维持健康", "控糖降压"], "tastes": ["清淡少油", "正常口味"], "avoid": ["乳糖不耐"], "ingredients": ["燕麦", "无糖酸奶", "蓝莓", "坚果碎"], "heat": 360, "protein": 20, "carb": 42, "fat": 12, "tip": "不用开火，适合早八和赶时间。"},
    {"meal": "breakfast", "title": "番茄鸡蛋全麦三明治", "scene": ["居家做饭", "外出通勤"], "targets": ["减脂减重", "增肌塑形", "维持健康"], "tastes": ["正常口味", "想吃丰富一点但尽量健康"], "avoid": ["鸡蛋过敏"], "ingredients": ["全麦面包", "鸡蛋", "番茄", "生菜", "低脂奶酪"], "heat": 430, "protein": 26, "carb": 48, "fat": 15, "tip": "酱料减半，饱腹感更稳。"},
    {"meal": "breakfast", "title": "南瓜小米暖胃粥套餐", "scene": ["居家做饭", "食堂简餐", "外卖为主"], "targets": ["养胃调理", "维持健康"], "tastes": ["清淡少油"], "avoid": [], "ingredients": ["小米粥", "南瓜", "水煮蛋", "清炒青菜"], "heat": 350, "protein": 17, "carb": 56, "fat": 8, "tip": "胃不舒服时优先热粥热菜。"},
    {"meal": "breakfast", "title": "鸡胸肉卷饼早餐", "scene": ["居家做饭", "外卖为主", "外出通勤"], "targets": ["增肌塑形", "维持健康"], "tastes": ["正常口味", "重口味但想健康一点"], "avoid": [], "ingredients": ["全麦卷饼", "鸡胸肉", "黄瓜", "生菜", "酸奶酱"], "heat": 510, "protein": 35, "carb": 54, "fat": 16, "tip": "外卖备注少酱少油。"},
    {"meal": "breakfast", "title": "便利店控糖早餐", "scene": ["外卖为主", "外出通勤", "办公室带餐"], "targets": ["减脂减重", "控糖降压"], "tastes": ["清淡少油"], "avoid": ["乳糖不耐"], "ingredients": ["茶叶蛋", "即食鸡胸", "无糖酸奶", "黄瓜条"], "heat": 380, "protein": 34, "carb": 18, "fat": 15, "tip": "避开甜面包、奶茶和含糖咖啡。"},
    {"meal": "breakfast", "title": "食堂豆浆鸡蛋玉米餐", "scene": ["食堂简餐"], "targets": ["减脂减重", "控糖降压", "维持健康"], "tastes": ["清淡少油", "正常口味"], "avoid": [], "ingredients": ["无糖豆浆", "茶叶蛋", "玉米", "拌黄瓜"], "heat": 370, "protein": 22, "carb": 43, "fat": 11, "tip": "比油条包子组合更稳。"},
    {"meal": "breakfast", "title": "牛油果鸡蛋贝果", "scene": ["居家做饭", "外卖为主"], "targets": ["增肌塑形", "维持健康"], "tastes": ["想吃丰富一点但尽量健康"], "avoid": ["鸡蛋过敏"], "ingredients": ["贝果", "鸡蛋", "牛油果", "番茄", "生菜"], "heat": 560, "protein": 28, "carb": 60, "fat": 22, "tip": "适合活动量大或训练日。"},
    {"meal": "breakfast", "title": "鲜虾云吞汤早餐", "scene": ["外卖为主", "食堂简餐"], "targets": ["维持健康", "养胃调理"], "tastes": ["正常口味", "清淡少油"], "avoid": ["海鲜过敏"], "ingredients": ["鲜虾云吞", "青菜", "紫菜", "蛋花汤"], "heat": 420, "protein": 24, "carb": 52, "fat": 10, "tip": "备注少盐，汤不要喝太多。"},
    # Lunch - varied
    {"meal": "lunch", "title": "香煎鸡胸糙米彩蔬盘", "scene": ["居家做饭", "食堂简餐"], "targets": ["减脂减重", "控糖降压", "增肌塑形"], "tastes": ["清淡少油", "正常口味"], "avoid": [], "ingredients": ["鸡胸肉", "糙米饭", "西兰花", "彩椒", "蘑菇"], "heat": 610, "protein": 46, "carb": 68, "fat": 16, "tip": "蛋白质足，适合午后不犯困。"},
    {"meal": "lunch", "title": "番茄牛腩杂粮饭", "scene": ["居家做饭", "食堂简餐", "外卖为主"], "targets": ["增肌塑形", "维持健康"], "tastes": ["正常口味", "想吃丰富一点但尽量健康"], "avoid": ["高尿酸/痛风"], "ingredients": ["牛腩", "番茄", "杂粮饭", "胡萝卜", "生菜"], "heat": 720, "protein": 42, "carb": 82, "fat": 24, "tip": "外卖备注少油，汤汁少拌饭。"},
    {"meal": "lunch", "title": "日式肥牛饭健康版", "scene": ["外卖为主", "食堂简餐"], "targets": ["维持健康", "增肌塑形"], "tastes": ["正常口味", "重口味但想健康一点"], "avoid": ["高尿酸/痛风"], "ingredients": ["肥牛", "洋葱", "米饭", "温泉蛋", "西兰花"], "heat": 760, "protein": 38, "carb": 88, "fat": 28, "tip": "外卖选择小份饭、加青菜、少酱汁。"},
    {"meal": "lunch", "title": "麻辣烫清爽点单", "scene": ["外卖为主"], "targets": ["减脂减重", "控糖降压", "维持健康"], "tastes": ["重口味但想健康一点", "想吃丰富一点但尽量健康"], "avoid": ["胃病"], "ingredients": ["青菜", "豆腐", "虾仁", "魔芋面", "菌菇", "鹌鹑蛋"], "heat": 560, "protein": 34, "carb": 45, "fat": 20, "tip": "选清汤或番茄汤，少麻酱，少丸子。"},
    {"meal": "lunch", "title": "轻食鸡肉藜麦沙拉", "scene": ["外卖为主", "办公室带餐"], "targets": ["减脂减重", "控糖降压"], "tastes": ["清淡少油"], "avoid": [], "ingredients": ["鸡胸肉", "藜麦", "生菜", "牛油果", "玉米粒", "油醋汁"], "heat": 520, "protein": 36, "carb": 46, "fat": 21, "tip": "酱汁单放，吃一半即可。"},
    {"meal": "lunch", "title": "黄焖鸡米饭减油版", "scene": ["外卖为主", "食堂简餐"], "targets": ["维持健康", "增肌塑形"], "tastes": ["正常口味", "重口味但想健康一点"], "avoid": [], "ingredients": ["鸡腿肉", "土豆", "香菇", "青椒", "米饭"], "heat": 730, "protein": 40, "carb": 86, "fat": 24, "tip": "备注少油少盐，米饭吃七分。"},
    {"meal": "lunch", "title": "虾仁滑蛋荞麦面", "scene": ["居家做饭", "食堂简餐"], "targets": ["减脂减重", "维持健康", "控糖降压"], "tastes": ["正常口味"], "avoid": ["海鲜过敏", "鸡蛋过敏"], "ingredients": ["虾仁", "鸡蛋", "荞麦面", "菠菜", "番茄"], "heat": 590, "protein": 37, "carb": 67, "fat": 17, "tip": "比油炒面更清爽。"},
    {"meal": "lunch", "title": "韩式拌饭少酱版", "scene": ["外卖为主", "食堂简餐"], "targets": ["维持健康", "增肌塑形"], "tastes": ["想吃丰富一点但尽量健康", "正常口味"], "avoid": [], "ingredients": ["米饭", "牛肉", "鸡蛋", "菠菜", "胡萝卜", "豆芽"], "heat": 690, "protein": 35, "carb": 86, "fat": 20, "tip": "辣酱减半，额外加青菜。"},
    {"meal": "lunch", "title": "番茄豆腐菌菇荞麦面", "scene": ["居家做饭", "外卖为主"], "targets": ["养胃调理", "控糖降压", "减脂减重"], "tastes": ["清淡少油", "正常口味"], "avoid": ["高尿酸/痛风"], "ingredients": ["豆腐", "番茄", "菌菇", "荞麦面", "青菜"], "heat": 540, "protein": 25, "carb": 70, "fat": 14, "tip": "适合想吃面又不想太油。"},
    {"meal": "lunch", "title": "烤肉饭健康点单", "scene": ["外卖为主"], "targets": ["维持健康", "增肌塑形"], "tastes": ["重口味但想健康一点"], "avoid": [], "ingredients": ["烤鸡肉", "米饭", "生菜", "玉米", "海苔", "少量酱汁"], "heat": 710, "protein": 42, "carb": 82, "fat": 23, "tip": "选鸡肉优先，少酱少芝士。"},
    # Dinner
    {"meal": "dinner", "title": "豆腐南瓜暖胃煲", "scene": ["居家做饭", "外卖为主"], "targets": ["养胃调理", "减脂减重", "维持健康"], "tastes": ["清淡少油"], "avoid": ["高尿酸/痛风"], "ingredients": ["豆腐", "南瓜", "娃娃菜", "菌菇", "小米粥"], "heat": 390, "protein": 20, "carb": 48, "fat": 11, "tip": "晚餐温热、少油，胃更舒服。"},
    {"meal": "dinner", "title": "清蒸鲈鱼蔬菜饭", "scene": ["居家做饭", "食堂简餐"], "targets": ["减脂减重", "控糖降压", "维持健康"], "tastes": ["清淡少油", "正常口味"], "avoid": ["海鲜过敏"], "ingredients": ["鲈鱼", "杂粮饭", "菜心", "香菇", "姜丝"], "heat": 560, "protein": 42, "carb": 55, "fat": 14, "tip": "鱼肉清蒸，盐和蒸鱼豉油少放。"},
    {"meal": "dinner", "title": "咖喱鸡肉蔬菜饭", "scene": ["居家做饭", "外卖为主"], "targets": ["增肌塑形", "维持健康"], "tastes": ["想吃丰富一点但尽量健康", "正常口味"], "avoid": [], "ingredients": ["鸡腿肉", "土豆", "胡萝卜", "洋葱", "米饭"], "heat": 680, "protein": 36, "carb": 78, "fat": 22, "tip": "咖喱酱少放，增加蔬菜比例。"},
    {"meal": "dinner", "title": "粥铺养胃晚餐", "scene": ["外卖为主"], "targets": ["养胃调理", "维持健康"], "tastes": ["清淡少油"], "avoid": [], "ingredients": ["南瓜粥", "蒸蛋", "清炒青菜", "少量鸡丝"], "heat": 430, "protein": 22, "carb": 58, "fat": 10, "tip": "外卖选择粥铺，比烧烤炸鸡更适合晚餐。"},
    {"meal": "dinner", "title": "沙县蒸饺鸡汤组合", "scene": ["外卖为主"], "targets": ["维持健康", "增肌塑形"], "tastes": ["正常口味"], "avoid": [], "ingredients": ["蒸饺", "鸡汤", "青菜", "卤蛋"], "heat": 620, "protein": 34, "carb": 68, "fat": 21, "tip": "别点炸物，汤少喝。"},
    {"meal": "dinner", "title": "鸡胸紫薯饱腹盘", "scene": ["居家做饭", "办公室带餐"], "targets": ["减脂减重", "增肌塑形"], "tastes": ["清淡少油", "正常口味"], "avoid": [], "ingredients": ["鸡胸肉", "紫薯", "西兰花", "番茄", "蘑菇"], "heat": 500, "protein": 39, "carb": 48, "fat": 13, "tip": "适合晚饭后还要学习工作。"},
    {"meal": "dinner", "title": "冒菜健康点单", "scene": ["外卖为主"], "targets": ["维持健康", "减脂减重"], "tastes": ["重口味但想健康一点"], "avoid": ["胃病", "高血压"], "ingredients": ["青菜", "豆腐", "鸡肉片", "魔芋结", "海带", "菌菇"], "heat": 580, "protein": 33, "carb": 42, "fat": 24, "tip": "选微辣，少油碟，少加工丸子。"},
    {"meal": "dinner", "title": "番茄虾仁豆腐汤饭", "scene": ["居家做饭", "食堂简餐"], "targets": ["减脂减重", "控糖降压", "养胃调理"], "tastes": ["清淡少油", "正常口味"], "avoid": ["海鲜过敏"], "ingredients": ["虾仁", "豆腐", "番茄", "青菜", "少量米饭"], "heat": 460, "protein": 32, "carb": 45, "fat": 13, "tip": "汤饭别太烫，慢慢吃。"},
    # Snacks
    {"meal": "snack", "title": "苹果酸奶加餐", "scene": ["居家做饭", "办公室带餐", "外出通勤"], "targets": ["减脂减重", "维持健康", "养胃调理"], "tastes": ["清淡少油", "正常口味"], "avoid": ["乳糖不耐"], "ingredients": ["苹果", "无糖酸奶", "奇亚籽"], "heat": 170, "protein": 9, "carb": 24, "fat": 4, "tip": "下午饿的时候比奶茶更稳。"},
    {"meal": "snack", "title": "香蕉坚果训练补给", "scene": ["办公室带餐", "外出通勤", "居家做饭"], "targets": ["增肌塑形", "维持健康"], "tastes": ["正常口味"], "avoid": [], "ingredients": ["香蕉", "原味坚果", "黑咖啡"], "heat": 260, "protein": 7, "carb": 30, "fat": 13, "tip": "训练前后都可以。"},
    {"meal": "snack", "title": "便利店轻加餐", "scene": ["外卖为主", "外出通勤", "办公室带餐"], "targets": ["减脂减重", "控糖降压"], "tastes": ["清淡少油"], "avoid": [], "ingredients": ["茶叶蛋", "无糖豆浆", "黄瓜条"], "heat": 210, "protein": 18, "carb": 12, "fat": 9, "tip": "避开薯片、甜饮和奶油面包。"},
    {"meal": "snack", "title": "银耳水果小甜品", "scene": ["居家做饭", "外卖为主"], "targets": ["维持健康", "养胃调理"], "tastes": ["想吃丰富一点但尽量健康"], "avoid": [], "ingredients": ["银耳羹", "梨", "枸杞", "少量冰糖"], "heat": 190, "protein": 3, "carb": 42, "fat": 1, "tip": "甜度选少糖。"},
]


def setup_page(menu: str) -> None:
    
    bg_map = {
        "1": ("#fff1f2", "#e8ffd8", "🥕", "🍅"),
        "2": ("#eef8ff", "#fff6d7", "📊", "🍋"),
        "3": ("#fff0e6", "#eaffea", "🍱", "🥦"),
        "4": ("#f0fff7", "#fff0fb", "🔎", "🍇"),
        "5": ("#f9f2ff", "#fff8df", "📄", "🍓"),
        "6": ("#f4f8ff", "#ffeef1", "🕒", "🥑"),
    }
    key = menu[:1] if menu else "1"
    c1, c2, e1, e2 = bg_map.get(key, bg_map["1"])
    st.markdown(
        f"""
        <style>
        :root {{
            --card: rgba(255,255,255,.86);
            --line: rgba(238,162,144,.38);
            --ink: #3d302a;
            --muted: #7a6a64;
            --green: #6fc17a;
            --orange: #ff9d54;
            --pink: #ffb6c8;
        }}
        .stApp {{
            background:
              radial-gradient(circle at 8% 12%, rgba(255,180,130,.32), transparent 20%),
              radial-gradient(circle at 92% 14%, rgba(139,213,113,.32), transparent 22%),
              linear-gradient(135deg, {c1}, {c2});
            color: var(--ink);
        }}
        .stApp:before {{
            content: "{e1}";
            position: fixed;
            left: 18px;
            top: 70px;
            font-size: 86px;
            opacity: .22;
            z-index: 0;
            pointer-events: none;
        }}
        .stApp:after {{
            content: "{e2}";
            position: fixed;
            right: 24px;
            bottom: 40px;
            font-size: 96px;
            opacity: .20;
            z-index: 0;
            pointer-events: none;
        }}
        .block-container {{
            max-width: 1360px;
            padding-top: 1.4rem;
            position: relative;
            z-index: 1;
        }}
        section[data-testid="stSidebar"] > div {{
            background: rgba(255,255,255,.76);
            backdrop-filter: blur(14px);
            border-right: 1px solid var(--line);
        }}
        .hero, .soft-card, .metric-card, .dish-card {{
            background: var(--card);
            border: 1px solid var(--line);
            border-radius: 20px;
            box-shadow: 0 16px 42px rgba(132,81,63,.12);
            backdrop-filter: blur(12px);
        }}
        .hero {{
            padding: 22px 24px;
            margin-bottom: 18px;
        }}
        .hero h1 {{
            margin: 0 0 6px 0;
            font-size: 34px;
        }}
        .hero p {{
            margin: 0;
            color: var(--muted);
        }}
        .soft-card {{
            padding: 18px;
        }}
        .metric-card {{
            padding: 18px;
            min-height: 120px;
        }}
        .metric-card span {{
            color: var(--muted);
            font-size: 13px;
        }}
        .metric-card strong {{
            display: block;
            margin-top: 9px;
            color: #319152;
            font-size: 28px;
        }}
        .dish-card {{
            overflow: hidden;
            min-height: 545px;
        }}
        .dish-img {{
            width: 100%;
            height: 172px;
            object-fit: cover;
            display: block;
        }}
        .dish-body {{
            padding: 15px 16px 17px;
        }}
        .pill {{
            display: inline-block;
            padding: 5px 10px;
            border-radius: 999px;
            background: #eaffdf;
            color: #347c43;
            font-size: 12px;
            font-weight: 800;
            margin-bottom: 8px;
        }}
        .dish-title {{
            font-size: 19px;
            font-weight: 900;
            line-height: 1.35;
            margin: 0 0 10px;
        }}
        .food-list {{
            margin: 0 0 10px 18px;
            padding: 0;
            color: var(--ink);
            font-size: 14px;
            line-height: 1.65;
        }}
        .nutrition {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
            margin: 11px 0;
        }}
        .nutrition div {{
            background: #fff6e8;
            border-radius: 12px;
            padding: 8px 10px;
            color: #724d2f;
            font-size: 13px;
        }}
        .tip {{
            background: #fff4f7;
            border-radius: 12px;
            padding: 10px 12px;
            color: var(--muted);
            font-size: 13px;
            line-height: 1.55;
        }}
        .stButton > button {{
            border-radius: 12px;
            border: 0;
            background: linear-gradient(135deg, #62bd74, #ffad5a);
            color: white;
            font-weight: 900;
        }}
        .stButton > button:hover {{
            color: white;
            filter: brightness(.96);
        }}


        .sidebar-brand {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 14px 14px 16px;
            margin: 0 0 12px;
            border-radius: 18px;
            background: linear-gradient(135deg, rgba(255,255,255,.92), rgba(255,238,224,.84));
            border: 1px solid rgba(238,162,144,.32);
            box-shadow: 0 10px 24px rgba(132,81,63,.10);
        }}
        .brand-icon {{
            width: 44px;
            height: 44px;
            display: grid;
            place-items: center;
            border-radius: 16px;
            background: #fff5d8;
            font-size: 25px;
        }}
        .brand-title {{
            font-size: 18px;
            font-weight: 900;
            color: var(--ink);
        }}
        .brand-subtitle {{
            font-size: 12px;
            color: var(--muted);
            margin-top: 2px;
        }}
        [data-testid="stSidebar"] div[role="radiogroup"] label {{
            padding: 10px 12px;
            margin: 6px 0;
            border-radius: 14px;
            background: rgba(255,255,255,.60);
            border: 1px solid rgba(238,162,144,.18);
            transition: all .15s ease;
        }}
        [data-testid="stSidebar"] div[role="radiogroup"] label:hover {{
            background: rgba(255,246,232,.95);
            transform: translateX(2px);
        }}
        .sidebar-current {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 13px;
            margin-top: 16px;
            border-radius: 16px;
            background: rgba(234,255,223,.86);
            border: 1px solid rgba(111,193,122,.28);
        }}
        .sidebar-current p {{
            margin: 3px 0 0;
            color: var(--muted);
            font-size: 12px;
        }}
        .current-icon {{
            width: 38px;
            height: 38px;
            border-radius: 14px;
            display: grid;
            place-items: center;
            background: white;
            font-size: 22px;
        }}
        .result-summary {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 14px;
            margin-bottom: 16px;
        }}
        .result-summary span {{
            color: var(--muted);
            font-size: 13px;
        }}
        .result-summary strong {{
            display: block;
            margin: 5px 0;
            font-size: 24px;
            color: #319152;
        }}
        .result-summary p {{
            margin: 0;
            color: var(--muted);
            font-size: 13px;
        }}
        .macro-grid, .meal-cal-grid {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 12px;
            margin: 14px 0 18px;
        }}
        .meal-cal-grid {{
            grid-template-columns: repeat(4, minmax(0, 1fr));
        }}
        .macro-card, .meal-cal-grid div {{
            padding: 15px;
            border-radius: 18px;
            background: rgba(255,255,255,.82);
            border: 1px solid var(--line);
            box-shadow: 0 10px 24px rgba(132,81,63,.08);
        }}
        .macro-card b, .meal-cal-grid span {{
            color: var(--muted);
            font-size: 13px;
        }}
        .macro-card span, .meal-cal-grid b {{
            display: block;
            font-size: 24px;
            font-weight: 900;
            margin: 8px 0;
            color: var(--ink);
        }}
        .bar {{
            height: 9px;
            border-radius: 999px;
            background: rgba(0,0,0,.06);
            overflow: hidden;
        }}
        .bar i {{
            display: block;
            height: 100%;
            border-radius: 999px;
            background: linear-gradient(90deg, #72c982, #ffb25f);
        }}
        .meal-cal-grid p {{
            margin: 0;
            color: var(--muted);
            font-size: 13px;
        }}
        .tip-chip {{
            display: inline-block;
            margin: 0 8px 8px 0;
            padding: 10px 13px;
            border-radius: 999px;
            background: rgba(255,255,255,.82);
            border: 1px solid var(--line);
            color: var(--ink);
            box-shadow: 0 8px 18px rgba(132,81,63,.08);
        }}
        @media (max-width: 900px) {{
            .result-summary, .macro-grid, .meal-cal-grid {{
                grid-template-columns: 1fr;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def dish_image(recipe: dict) -> str:
    title = recipe["title"]
    foods = " · ".join(recipe["ingredients"][:3])
    seed = stable_int(title)
    palettes = [
        ("#fff1d6", "#ff9d54", "#79c267", "#ffccd6"),
        ("#eef8ff", "#7ec8e3", "#ffb86b", "#9bdc8e"),
        ("#fff0f7", "#f38fb1", "#8fd18b", "#ffd36b"),
        ("#f4fff1", "#78c66f", "#ff9d54", "#f9c6d3"),
    ]
    bg, main, side, accent = palettes[seed % len(palettes)]
    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="900" height="520" viewBox="0 0 900 520">
      <rect width="900" height="520" fill="{bg}"/>
      <circle cx="160" cy="110" r="92" fill="{accent}" opacity=".55"/>
      <circle cx="755" cy="105" r="116" fill="{side}" opacity=".35"/>
      <circle cx="740" cy="425" r="118" fill="{accent}" opacity=".45"/>
      <ellipse cx="450" cy="292" rx="270" ry="132" fill="#fff" opacity=".92"/>
      <ellipse cx="450" cy="302" rx="225" ry="96" fill="{main}" opacity=".82"/>
      <circle cx="355" cy="257" r="54" fill="{side}"/>
      <circle cx="438" cy="238" r="42" fill="#fff7b8"/>
      <circle cx="517" cy="260" r="54" fill="{accent}"/>
      <rect x="328" y="318" width="245" height="46" rx="23" fill="#7bc67a" opacity=".92"/>
      <circle cx="386" cy="252" r="7" fill="#3d302a"/>
      <circle cx="516" cy="252" r="7" fill="#3d302a"/>
      <path d="M415 284 Q450 310 488 284" stroke="#3d302a" stroke-width="8" fill="none" stroke-linecap="round"/>
      <text x="450" y="443" text-anchor="middle" font-family="Microsoft YaHei, Arial" font-size="38" font-weight="800" fill="#3d302a">{title}</text>
      <text x="450" y="482" text-anchor="middle" font-family="Microsoft YaHei, Arial" font-size="24" fill="#745f58">{foods}</text>
    </svg>
    """
    return "data:image/svg+xml;utf8," + quote(svg)


def user_signature(user: dict) -> str:
    keys = ["gender", "age", "height", "weight", "active", "target", "scene", "taste"]
    base = "|".join(str(user.get(k, "")) for k in keys)
    disease = ",".join(sorted(user.get("disease", [])))
    hate = ",".join(sorted(user.get("hate", [])))
    return f"{base}|{disease}|{hate}"


def calc_bmi(height: int, weight: int) -> tuple[float, str]:
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


def calc_bmr(gender: str, age: int, height: int, weight: int) -> float:
    if gender == "男":
        return 10 * weight + 6.25 * height - 5 * age + 5
    return 10 * weight + 6.25 * height - 5 * age - 161


def calc_tdee(bmr: float, active: str) -> int:
    coef = {
        "久坐（学生/办公室）": 1.2,
        "轻度活动（每周1-3次）": 1.375,
        "中度活动（每周3-5次）": 1.55,
        "高强度运动（体力/力量训练）": 1.725,
    }.get(active, 1.2)
    return round(bmr * coef)


def target_calories(tdee: int, target: str) -> int:
    if target == "减脂减重":
        return tdee - 400
    if target == "增肌塑形":
        return tdee + 300
    if target in ["控糖降压", "养胃调理"]:
        return tdee - 200
    return tdee


def macro_split(cal: int, target: str) -> tuple[int, int, int]:
    if target == "减脂减重":
        pr, cr, fr = 0.30, 0.32, 0.38
    elif target == "增肌塑形":
        pr, cr, fr = 0.30, 0.50, 0.20
    elif target == "控糖降压":
        pr, cr, fr = 0.28, 0.36, 0.36
    else:
        pr, cr, fr = 0.25, 0.42, 0.33
    return round(cal * pr / 4), round(cal * cr / 4), round(cal * fr / 9)


def disease_conflict(recipe: dict, user: dict) -> bool:
    text = " ".join([recipe["title"], *recipe["ingredients"]])
    disease = user.get("disease", [])
    if "乳糖不耐" in disease and any(x in text for x in ["牛奶", "酸奶", "奶酪", "拿铁"]):
        return True
    if "海鲜过敏" in disease and any(x in text for x in ["虾", "鱼", "贝", "蟹", "三文鱼", "鳕鱼", "鲈鱼"]):
        return True
    if "高尿酸/痛风" in disease and any(x in text for x in ["牛肉", "牛腩", "肥牛", "豆腐", "菌菇", "海鲜", "虾"]):
        return True
    if "胃病" in disease and any(x in text for x in ["麻辣", "冒菜", "重口", "凉皮"]):
        return True
    if "糖尿病" in disease and recipe["heat"] > 760:
        return True
    return False


def recipe_score(recipe: dict, user: dict) -> int:
    score = 0
    if user["scene"] in recipe["scene"]:
        score += 30
    if user["target"] in recipe["targets"]:
        score += 30
    if user["taste"] in recipe["tastes"]:
        score += 10
    if user["target"] == "减脂减重" and recipe["heat"] <= 620:
        score += 8
    if user["target"] == "增肌塑形" and recipe["protein"] >= 30:
        score += 8
    if user["scene"] == "外卖为主" and any(x in recipe["title"] for x in ["外卖", "点单", "沙县", "粥铺", "麻辣烫", "冒菜", "黄焖鸡", "烤肉饭", "肥牛饭"]):
        score += 16
    if disease_conflict(recipe, user):
        score -= 100
    hate = user.get("hate", [])
    if any(h and h in " ".join(recipe["ingredients"]) for h in hate):
        score -= 100
    return score


def recommend_meals(user: dict, round_no: int) -> dict:
    sig = user_signature(user)
    seed = stable_int(f"{sig}|{round_no}|{datetime.now().strftime('%Y-%m-%d-%H')}")
    rng = random.Random(seed)
    result = {}
    used_titles = set()
    used_main_words = set()
    for meal in ["breakfast", "lunch", "dinner", "snack"]:
        pool = [r for r in RECIPES if r["meal"] == meal]
        ranked = sorted(pool, key=lambda r: recipe_score(r, user), reverse=True)
        good = [r for r in ranked if recipe_score(r, user) > -50] or ranked
        top = good[: min(8, len(good))]
        rng.shuffle(top)
        chosen = None
        for item in top:
            main = item["ingredients"][0]
            if item["title"] not in used_titles and main not in used_main_words:
                chosen = item
                break
        chosen = chosen or top[0]
        result[meal] = chosen
        used_titles.add(chosen["title"])
        used_main_words.add(chosen["ingredients"][0])
    return result


def render_dish_card(label: str, recipe: dict) -> None:
    img = dish_image(recipe)
    ingredients = "".join(f"<li>{item}</li>" for item in recipe["ingredients"])
    scenes = "、".join(recipe["scene"])
    st.markdown(
        f"""
        <div class="dish-card">
          <img class="dish-img" src="{img}" alt="{recipe['title']}">
          <div class="dish-body">
            <span class="pill">{label} · {scenes}</span>
            <div class="dish-title">{recipe['title']}</div>
            <ul class="food-list">{ingredients}</ul>
            <div class="nutrition">
              <div>热量 {recipe['heat']} kcal</div>
              <div>蛋白质 {recipe['protein']} g</div>
              <div>碳水 {recipe['carb']} g</div>
              <div>脂肪 {recipe['fat']} g</div>
            </div>
            <div class="tip">{recipe['tip']}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def init_state() -> None:
    if "user_info" not in st.session_state:
        st.session_state.user_info = {}
    if "current_page" not in st.session_state:
        st.session_state.current_page = "1. 用户健康信息录入"
    if "recommend_round" not in st.session_state:
        st.session_state.recommend_round = 0
    if "last_signature" not in st.session_state:
        st.session_state.last_signature = ""


def metric_card(label: str, value: str, note: str = "") -> None:
    st.markdown(
        f"""<div class="metric-card"><span>{label}</span><strong>{value}</strong><span>{note}</span></div>""",
        unsafe_allow_html=True,
    )


ensure_history_file()
init_state()

menu_list = [
    "1. 用户健康信息录入",
    "2. 营养需求计算结果",
    "3. 一日三餐智能推荐",
    "4. 300+食材营养库",
    "5. 个人健康饮食报告",
    "6. 历史记录查询",
]
nav_icons = {
    "1. 用户健康信息录入": "📝",
    "2. 营养需求计算结果": "📊",
    "3. 一日三餐智能推荐": "🍱",
    "4. 300+食材营养库": "🥦",
    "5. 个人健康饮食报告": "📄",
    "6. 历史记录查询": "🕒",
}
nav_notes = {
    "1. 用户健康信息录入": "填写身体数据与偏好",
    "2. 营养需求计算结果": "查看热量与营养面板",
    "3. 一日三餐智能推荐": "生成丰富场景菜单",
    "4. 300+食材营养库": "查询食材与菜品数据",
    "5. 个人健康饮食报告": "汇总专属饮食建议",
    "6. 历史记录查询": "回看保存过的记录",
}

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
          <div class="brand-icon">🥕</div>
          <div>
            <div class="brand-title">食愈导航</div>
            <div class="brand-subtitle">轻松切换功能板块</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    selected = st.radio(
        "功能导航",
        menu_list,
        index=menu_list.index(st.session_state.current_page),
        format_func=lambda x: f"{nav_icons[x]}  {x.split('. ', 1)[1]}",
        label_visibility="collapsed",
    )
    st.markdown(
        f"""
        <div class="sidebar-current">
          <div class="current-icon">{nav_icons[selected]}</div>
          <div>
            <b>{selected.split('. ', 1)[1]}</b>
            <p>{nav_notes[selected]}</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
st.session_state.current_page = selected
setup_page(selected)
user = st.session_state.user_info

st.markdown(
    """
    <div class="hero">
      <h1>食愈小助手</h1>
      <p>300+ 食材库 · 场景化三餐推荐 · 每次生成都换一组 · 可爱美食卡片</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if selected == "1. 用户健康信息录入":
    st.markdown("### 个人身体信息填写区")
    col1, col2 = st.columns(2)
    with col1:
        gender = st.radio("性别", ["男", "女"])
        age = st.number_input("年龄", min_value=5, max_value=120, value=user.get("age", 22))
        height = st.number_input("身高(cm)", min_value=80, max_value=250, value=user.get("height", 170))
        weight = st.number_input("体重(kg)", min_value=20, max_value=300, value=user.get("weight", 60))
        active = st.selectbox("日常活动强度", ["久坐（学生/办公室）", "轻度活动（每周1-3次）", "中度活动（每周3-5次）", "高强度运动（体力/力量训练）"])
    with col2:
        disease = st.multiselect("体检健康异常/基础疾病", DISEASES, default=user.get("disease", []))
        target = st.radio("健康目标", TARGETS)
        taste = st.radio("饮食口味偏好", TASTES)
        scene = st.radio("日常用餐场景", SCENES)
        hate_food = st.text_input("忌口食材（逗号分隔，如牛肉,香菜）", ",".join(user.get("hate", [])))

    if st.button("保存信息并重新生成推荐基础", type="primary", use_container_width=True):
        bmi, bmi_level = calc_bmi(height, weight)
        new_user = {
            "gender": gender,
            "age": int(age),
            "height": int(height),
            "weight": int(weight),
            "active": active,
            "disease": disease,
            "target": target,
            "taste": taste,
            "scene": scene,
            "hate": [x.strip() for x in hate_food.split(",") if x.strip()],
            "bmi": bmi,
            "bmi_level": bmi_level,
        }
        new_sig = user_signature(new_user)
        if new_sig != st.session_state.last_signature:
            st.session_state.recommend_round = stable_int(new_sig) % 997
            st.session_state.last_signature = new_sig
        st.session_state.user_info = new_user
        st.success(f"保存成功：BMI {bmi}，身体状态 {bmi_level}。信息变化后，三餐推荐会同步变化。")

elif selected == "2. 营养需求计算结果":
    if not user:
        st.warning("请先完成用户健康信息录入。")
    else:
        bmr = calc_bmr(user["gender"], user["age"], user["height"], user["weight"])
        tdee = calc_tdee(bmr, user["active"])
        cal = target_calories(tdee, user["target"])
        pro, carb, fat = macro_split(cal, user["target"])
        bmi = user["bmi"]

        st.markdown("### 营养需求计算结果")
        st.markdown(
            f"""
            <div class="soft-card result-summary">
              <div>
                <span>当前目标</span>
                <strong>{user['target']}</strong>
                <p>场景：{user['scene']} · 口味：{user['taste']}</p>
              </div>
              <div>
                <span>身体状态</span>
                <strong>{user['bmi_level']}</strong>
                <p>BMI {bmi}</p>
              </div>
              <div>
                <span>建议重点</span>
                <strong>{'控总热量' if user['target']=='减脂减重' else '补足蛋白' if user['target']=='增肌塑形' else '稳定饮食'}</strong>
                <p>按你的身体信息动态计算</p>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        cols = st.columns(4)
        with cols[0]:
            metric_card("BMI 指数", str(user["bmi"]), user["bmi_level"])
        with cols[1]:
            metric_card("基础代谢 BMR", f"{round(bmr)} kcal", "静息状态每日消耗")
        with cols[2]:
            metric_card("每日消耗 TDEE", f"{tdee} kcal", user["active"])
        with cols[3]:
            metric_card("目标摄入", f"{cal} kcal", "用于后续三餐推荐")

        st.markdown("### 三大营养素分配")
        macro_rows = [
            {"营养素": "蛋白质", "建议摄入": f"{pro} g", "作用": "维持肌肉、增强饱腹感", "食物来源": "鸡蛋、鸡胸肉、牛肉、鱼虾、豆腐"},
            {"营养素": "碳水", "建议摄入": f"{carb} g", "作用": "提供学习和运动能量", "食物来源": "杂粮饭、燕麦、红薯、玉米、荞麦面"},
            {"营养素": "脂肪", "建议摄入": f"{fat} g", "作用": "维持激素和脂溶性营养吸收", "食物来源": "坚果、牛油果、鱼类、橄榄油"},
        ]
        st.dataframe(pd.DataFrame(macro_rows), use_container_width=True, hide_index=True)

        ratio_total = max(pro + carb + fat, 1)
        st.markdown(
            f"""
            <div class="macro-grid">
              <div class="macro-card protein">
                <b>蛋白质</b>
                <span>{pro}g</span>
                <div class="bar"><i style="width:{pro / ratio_total * 100:.0f}%"></i></div>
              </div>
              <div class="macro-card carb">
                <b>碳水</b>
                <span>{carb}g</span>
                <div class="bar"><i style="width:{carb / ratio_total * 100:.0f}%"></i></div>
              </div>
              <div class="macro-card fat">
                <b>脂肪</b>
                <span>{fat}g</span>
                <div class="bar"><i style="width:{fat / ratio_total * 100:.0f}%"></i></div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        breakfast_cal = round(cal * 0.28)
        lunch_cal = round(cal * 0.38)
        dinner_cal = round(cal * 0.28)
        snack_cal = max(120, cal - breakfast_cal - lunch_cal - dinner_cal)
        st.markdown("### 一日热量分配建议")
        st.markdown(
            f"""
            <div class="meal-cal-grid">
              <div><span>早餐</span><b>{breakfast_cal} kcal</b><p>主食 + 蛋白质 + 少量水果</p></div>
              <div><span>午餐</span><b>{lunch_cal} kcal</b><p>一天中最完整的一餐</p></div>
              <div><span>晚餐</span><b>{dinner_cal} kcal</b><p>清淡、不过饱、少油</p></div>
              <div><span>加餐</span><b>{snack_cal} kcal</b><p>水果、酸奶、坚果按量</p></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        tips = []
        if user["target"] == "减脂减重":
            tips.append("保持轻微热量缺口，优先高蛋白和高纤维食物。")
        elif user["target"] == "增肌塑形":
            tips.append("训练日适当增加主食和蛋白质，别只吃蔬菜。")
        elif user["target"] == "控糖降压":
            tips.append("主食优先杂粮，外卖备注少盐少酱，避免含糖饮料。")
        elif user["target"] == "养胃调理":
            tips.append("优先热粥、热汤、软烂主食，减少生冷辛辣。")
        else:
            tips.append("保持三餐规律，主食、蛋白质、蔬菜都要有。")
        if user["scene"] == "外卖为主":
            tips.append("外卖优先选轻食、粥铺、盖饭少酱、麻辣烫清汤少油，少点炸鸡奶茶。")
        elif user["scene"] == "食堂简餐":
            tips.append("食堂选择一荤一素一主食，少选油炸窗口。")
        elif user["scene"] == "居家做饭":
            tips.append("居家可用蒸、煮、炖、少油快炒，食材更容易控量。")
        st.markdown("### 个性化提醒")
        st.markdown("".join(f"<div class='tip-chip'>🍀 {tip}</div>" for tip in tips), unsafe_allow_html=True)

elif selected == "3. 一日三餐智能推荐":
    if not user:
        st.warning("请先完成用户健康信息录入。")
    else:
        st.markdown("### 场景化三餐推荐")
        st.caption("同样身体信息下，点击“换一组不重样推荐”会换新菜单；只要用户信息改变，推荐种子也会改变。")
        col_a, col_b = st.columns([1, 3])
        with col_a:
            if st.button("换一组不重样推荐", type="primary", use_container_width=True):
                st.session_state.recommend_round += 1
        with col_b:
            st.markdown(f"<div class='soft-card'>当前场景：<b>{user['scene']}</b>；目标：<b>{user['target']}</b>；口味：<b>{user['taste']}</b></div>", unsafe_allow_html=True)
        meals = recommend_meals(user, st.session_state.recommend_round)
        cols = st.columns(4)
        for col, meal_key in zip(cols, ["breakfast", "lunch", "dinner", "snack"]):
            with col:
                render_dish_card(MEAL_LABELS[meal_key], meals[meal_key])
        total = sum(m["heat"] for m in meals.values())
        st.markdown(f"<div class='soft-card'>本组推荐总热量约 <b>{total} kcal</b>。外卖场景会优先推荐可点到的轻食、粥铺、麻辣烫健康点单、黄焖鸡减油版、烤肉饭少酱版等。</div>", unsafe_allow_html=True)

        if st.button("保存本次推荐到历史记录", use_container_width=True):
            bmr = calc_bmr(user["gender"], user["age"], user["height"], user["weight"])
            tdee = calc_tdee(bmr, user["active"])
            cal = target_calories(tdee, user["target"])
            pro, carb, fat = macro_split(cal, user["target"])
            history = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
            history.append({
                "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "user": user,
                "target_cal": cal,
                "macro": {"protein": pro, "carb": carb, "fat": fat},
                "meals": {k: v["title"] for k, v in meals.items()},
            })
            HISTORY_FILE.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")
            st.success("已保存。")

elif selected == "4. 300+食材营养库":
    st.markdown(f"### 食材库查询（当前 {len(FOOD_DB)} 种）")
    if len(FOOD_DB) < 300:
        st.error("食材库数量不足300，请检查 build_food_db。")
    q = st.text_input("搜索食材/菜品", "")
    df = pd.DataFrame(FOOD_DB)
    if q:
        df = df[df.apply(lambda row: q in "".join(map(str, row.values)), axis=1)]
    st.dataframe(df, use_container_width=True, height=560)

elif selected == "5. 个人健康饮食报告":
    if not user:
        st.warning("请先完成用户健康信息录入。")
    else:
        meals = recommend_meals(user, st.session_state.recommend_round)
        st.markdown("### 专属健康饮食报告")
        st.markdown(
            f"""
            <div class="soft-card">
            <p><b>身体情况：</b>{user['gender']}，{user['age']}岁，{user['height']}cm，{user['weight']}kg，BMI {user['bmi']}（{user['bmi_level']}）。</p>
            <p><b>目标与场景：</b>{user['target']}；{user['scene']}；{user['taste']}。</p>
            <p><b>疾病/忌口：</b>{'、'.join(user['disease']) if user['disease'] else '无'}；{'、'.join(user['hate']) if user['hate'] else '无'}。</p>
            <p><b>今日建议：</b>优先选择蛋白质明确、蔬菜足量、主食可控的组合。外卖时备注少油少盐、酱汁分装、饭量七分。</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("### 当前推荐菜单")
        for meal_key, recipe in meals.items():
            st.write(f"{MEAL_LABELS[meal_key]}：{recipe['title']}（食材：{'、'.join(recipe['ingredients'])}）")

elif selected == "6. 历史记录查询":
    st.markdown("### 历史记录")
    history = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    if not history:
        st.info("暂无历史记录。")
    else:
        for idx, item in enumerate(reversed(history), 1):
            with st.expander(f"{idx}. {item['time']} - {item['user'].get('scene')} - {item['user'].get('target')}"):
                st.json(item)

