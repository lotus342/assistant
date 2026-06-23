import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
import os
from datetime import datetime

# ====================== 全局基础配置（莫兰迪风格+纯标题） ======================
st.set_page_config(page_title="食愈小助手", layout="wide")
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.figsize"] = (6, 4)

# 全局CSS：统一莫兰迪色系、圆角柔和样式
st.markdown("""
<style>
/* 全局莫兰迪基础配色定义 */
:root {
    --mori-beige: #EAE3DC;
    --mori-blue: #D8E0E6;
    --mori-green: #D9E2DD;
    --mori-pink: #E9DCDA;
    --mori-yellow: #EAE2D3;
    --mori-grey: #CBCFD3;
    --mori-text: #444444;
}
/* 主标题样式 */
h1 {
    color: #3A3A3A !important;
    font-weight: 600;
}
/* 所有卡片通用莫兰迪圆角 */
div[data-testid="stVerticalBlock"] > div[style*="background"] {
    border-radius: 16px !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
/* 按钮柔和莫兰迪蓝 */
.stButton > button {
    background-color: #B9C8D4 !important;
    color: #222222 !important;
    border: none !important;
    border-radius: 10px !important;
}
.stButton > button:hover {
    background-color: #A0B4C4 !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# 仅纯主标题
st.markdown("# 食愈小助手")
st.divider()

# 内置点击音效（网页原生audio，点击按钮自动播放，无需文件）
click_audio = """
<audio id="clickSound" src="https://assets.mixkit.co/sfx/preview/mixkit-software-interface-start-2574.mp3">
<script>
function playClick() {
    document.getElementById("clickSound").currentTime = 0;
    document.getElementById("clickSound").play();
}
</script>
"""
st.markdown(click_audio, unsafe_allow_html=True)

# ====================== 会话状态初始化（防乱跳逻辑不变） ======================
if "user_info" not in st.session_state:
    st.session_state.user_info = {}
if "target_page" not in st.session_state:
    st.session_state.target_page = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "1. 📝 用户健康信息录入"

menu_list = [
    "1. 📝 用户健康信息录入",
    "2. 📊 营养需求计算结果",
    "3. 🍱 一日三餐智能食谱推荐",
    "4. 🥬 食材营养查询库",
    "5. 📄 个人健康饮食报告",
    "6. 📜 历史记录查询"
]

# 侧边栏导航
select_menu = st.sidebar.selectbox("🧭 功能导航", menu_list, index=menu_list.index(st.session_state.current_page))

# 单次跳转逻辑，杜绝循环乱跳
if st.session_state.target_page is not None:
    st.session_state.current_page = st.session_state.target_page
    st.session_state.target_page = None
    st.rerun()
else:
    st.session_state.current_page = select_menu

menu = st.session_state.current_page
user = st.session_state.user_info

# ====================== 全局虚拟数据库（无改动） ======================
food_db = [
    {"name":"鸡胸肉","heat":118,"protein":23,"carb":0,"fat":2,"fiber":0,"sugar":0,"fit":["减脂","增肌","控糖"],"avoid":["痛风无禁忌"]},
    {"name":"瘦牛肉","heat":106,"protein":22,"carb":0,"fat":1.5,"fiber":0,"sugar":0,"fit":["减脂","增肌"],"avoid":["高尿酸"]},
    {"name":"草鱼","heat":112,"protein":18,"carb":0,"fat":4,"fiber":0,"sugar":0,"fit":["减脂","控血压"],"avoid":["海鲜过敏"]},
    {"name":"鸡蛋","heat":143,"protein":13,"carb":1,"fat":10,"fiber":0,"sugar":0,"fit":["全部人群"],"avoid":["鸡蛋过敏"]},
    {"name":"无糖豆浆","heat":40,"protein":3,"carb":3,"fat":1,"fiber":1,"sugar":0,"fit":["控糖","养胃","乳糖不耐"],"avoid":["无"]},
    {"name":"纯牛奶","heat":60,"protein":3,"carb":5,"fat":3,"fiber":0,"sugar":5,"fit":["增肌","青少年"],"avoid":["乳糖不耐"]},
    {"name":"燕麦片","heat":377,"protein":13,"carb":66,"fat":7,"fiber":10,"sugar":2,"fit":["减脂","控糖","养胃"],"avoid":["无"]},
    {"name":"白米饭","heat":130,"protein":2.6,"carb":28,"fat":0.3,"fiber":0.4,"sugar":0,"fit":["增肌","维持健康"],"avoid":["糖尿病"]},
    {"name":"杂粮饭","heat":110,"protein":3,"carb":23,"fat":0.5,"fiber":4,"sugar":1,"fit":["减脂","控糖","高血压"],"avoid":["无"]},
    {"name":"红薯","heat":86,"protein":1.6,"carb":20,"fat":0.1,"fiber":3,"sugar":4,"fit":["减脂","控糖替代主食"],"avoid":["胃病少食"]},
    {"name":"菠菜","heat":28,"protein":2.9,"carb":3.6,"fat":0.4,"fiber":2,"sugar":0,"fit":["控血压","减脂"],"avoid":["肾结石少食"]},
    {"name":"黄瓜","heat":16,"protein":0.7,"carb":3,"fat":0.2,"fiber":0.5,"sugar":1,"fit":["减脂","控糖"],"avoid":["胃病少食生冷"]},
    {"name":"小米粥","heat":46,"protein":1.4,"carb":10,"fat":0.3,"fiber":1,"sugar":1,"fit":["养胃"],"avoid":["糖尿病高升糖"]},
    {"name":"豆腐","heat":85,"protein":8,"carb":3,"fat":4,"fiber":1,"sugar":0,"fit":["素食","控血压"],"avoid":["痛风少食"]},
    {"name":"苹果","heat":52,"protein":0.3,"carb":14,"fat":0.2,"fiber":2,"sugar":10,"fit":["加餐全部人群"],"avoid":["无"]},
    {"name":"原味坚果","heat":600,"protein":20,"carb":15,"fat":52,"fiber":6,"sugar":2,"fit":["增肌加餐"],"avoid":["减脂少量食用"]},
]

recipe_db = {
    "breakfast": [
        {
            "title":"减脂控糖早餐",
            "foods":["无糖豆浆250ml","水煮鸡蛋1个","燕麦50g","黄瓜半根"],
            "total_heat":430,"protein":28,"carb":48,"fat":13,
            "fit":["减脂","糖尿病","高血压"],
            "avoid":["无"],
            "tip":"少油无糖，拒绝油条包子精制主食"
        },
        {
            "title":"增肌早餐",
            "foods":["纯牛奶300ml","全麦面包2片","煎鸡胸肉80g","香蕉1根"],
            "total_heat":480,"protein":32,"carb":55,"fat":15,
            "fit":["增肌塑形","体力运动人群"],
            "avoid":["乳糖不耐"],
            "tip":"运动前食用，充足碳水提供能量"
        },
        {
            "title":"养胃清淡早餐",
            "foods":["小米粥一碗","蒸南瓜100g","蒸蛋羹"],
            "total_heat":260,"protein":12,"carb":42,"fat":6,
            "fit":["胃病、体虚、术后调理"],
            "avoid":["糖尿病"],
            "tip":"温热食用，禁止空腹生冷"
        }
    ],
    "lunch": [
        {
            "title":"食堂减脂套餐",
            "foods":["杂粮饭80g","清蒸草鱼100g","清炒菠菜200g"],
            "total_heat":680,"protein":52,"carb":72,"fat":17,
            "fit":["减脂减重、控血压"],
            "avoid":["海鲜过敏"],
            "tip":"烹饪清蒸水煮，不油炸，少盐"
        },
        {
            "title":"控血压少油午餐",
            "foods":["糙米饭100g","瘦牛肉80g","芹菜木耳"],
            "total_heat":450,"protein":33,"carb":48,"fat":13,
            "fit":["高血压、中老年"],
            "avoid":["高尿酸"],
            "tip":"禁止咸菜、腌制品，每日盐<5g"
        },
        {
            "title":"素食健康午餐",
            "foods":["荞麦面100g","嫩豆腐150g","菌菇杂蔬"],
            "total_heat":400,"protein":25,"carb":52,"fat":10,
            "fit":["素食人群、减脂"],
            "avoid":["痛风大量食用豆制品"],
            "tip":"搭配坚果补充优质脂肪"
        }
    ],
    "dinner": [
        {
            "title":"低油高蛋白晚餐",
            "foods":["鸡胸肉沙拉","小块玉米半根","小番茄"],
            "total_heat":520,"protein":42,"carb":50,"fat":12,
            "fit":["减脂、夜间易水肿人群"],
            "avoid":["胃病少食生冷沙拉"],
            "tip":"19点前吃完，晚餐主食减半"
        },
        {
            "title":"控糖易消化晚餐",
            "foods":["虾仁豆腐蔬菜汤","少量红薯80g"],
            "total_heat":300,"protein":26,"carb":30,"fat":9,
            "fit":["糖尿病、控糖人群"],
            "avoid":["海鲜过敏"],
            "tip":"不喝粥，不喝浓汤，避免升糖过快"
        },
        {
            "title":"养胃温和晚餐",
            "foods":["清炖鸡蛋豆腐羹","清炒油麦菜"],
            "total_heat":240,"protein":20,"carb":25,"fat":8,
            "fit":["慢性胃炎、消化不良"],
            "avoid":["减脂人群可减少豆腐量"],
            "tip":"不吃烧烤、重油外卖、生冷凉菜"
        }
    ],
    "snack": [
        {
            "title":"低热量加餐",
            "foods":["苹果1个 / 无糖酸奶100g / 小番茄200g"],
            "total_heat":180,"protein":6,"carb":28,"fat":4,
            "fit":["全部人群"],
            "avoid":["无"],
            "tip":"上午10点、下午3点补充，不睡前加餐"
        },
        {
            "title":"增肌能量加餐",
            "foods":["原味坚果15g+纯牛奶200ml"],
            "total_heat":220,"protein":12,"carb":15,"fat":16,
            "fit":["增肌、高强度运动"],
            "avoid":["减脂少量食用"],
            "tip":"每日坚果不超过一小把，热量较高"
        }
    ]
}

disease_avoid_map = {
    "糖尿病": ["白米饭","小米粥","甜点"],
    "高血压": ["咸菜、腌肉、重油重盐"],
    "高尿酸/痛风": ["瘦牛肉","动物内脏","浓汤","豆制品过量"],
    "乳糖不耐": ["纯牛奶"],
    "海鲜过敏": ["草鱼","虾仁"],
    "胃病": ["生冷黄瓜、沙拉、辛辣食物"],
}

history_file = "user_history.json"
if not os.path.exists(history_file):
    with open(history_file,"w",encoding="utf-8") as f:
        json.dump([],f,ensure_ascii=False)

# ====================== 核心计算函数（修复fat重名） ======================
def calc_bmi(height,weight):
    h = height / 100
    bmi = weight / (h ** 2)
    if bmi < 18.5:
        level = "偏瘦"
    elif 18.5 <= bmi < 24:
        level = "标准健康"
    elif 24 <= bmi < 28:
        level = "超重"
    else:
        level = "肥胖"
    return round(bmi,2), level

def calc_bmr(gender,age,height,weight):
    if gender == "男":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    return bmr

def calc_tdee(bmr, act_level):
    act_coef = {
        "久坐（学生/办公室）": 1.2,
        "轻度活动（每日散步30分钟）": 1.375,
        "中度活动（每日健身1小时）": 1.55,
        "高强度运动（体力/力量训练）": 1.725
    }
    coef = act_coef.get(act_level, 1.2)
    return round(bmr * coef)

def get_target_cal(tdee,target):
    if target == "减脂减重":
        return tdee - 400
    elif target == "增肌塑形":
        return tdee + 300
    elif target == "维持健康":
        return tdee
    elif target in ["控糖降压","养胃调理"]:
        return tdee - 200

def calc_macro(cal,target):
    if target == "减脂减重":
        pro_rate = 0.3
        cho_rate = 0.3
        fat_rate = 0.4
    elif target == "增肌塑形":
        pro_rate = 0.3
        cho_rate = 0.5
        fat_rate = 0.2
    else:
        pro_rate = 0.25
        cho_rate = 0.4
        fat_rate = 0.35
    protein = (cal * pro_rate) / 4
    carb = (cal * cho_rate) / 4
    fat_val = (cal * fat_rate) / 9
    return round(protein), round(carb), round(fat_val)

def filter_recipes(recipe_list,user_target,user_disease,avoid_food):
    res = []
    for rec in recipe_list:
        bad = False
        for d in user_disease:
            if rec["title"] in disease_avoid_map.get(d,[]):
                bad = True
        for af in avoid_food:
            if af in "".join(rec["foods"]):
                bad = True
        if not bad and user_target in rec["fit"]:
            res.append(rec)
    if len(res) == 0:
        return [recipe_list[0]]
    return res

def save_history(user_data,cal,pro,cho,fat):
    with open(history_file,"r",encoding="utf-8") as f:
        hist = json.load(f)
    record = {
        "time":datetime.now().strftime("%Y-%m-%d %H:%M"),
        "user":user_data,
        "daily_cal":round(cal),
        "protein":pro,
        "carb":cho,
        "fat":fat
    }
    hist.append(record)
    with open(history_file,"w",encoding="utf-8") as f:
        json.dump(hist,f,ensure_ascii=False,indent=2)

# ====================== 页面1：用户健康信息录入（莫兰迪米色提示框） ======================
if menu == "1. 📝 用户健康信息录入":
    st.markdown("## 🥕 个人身体信息填写区")
    # 莫兰迪米色提示框
    st.markdown("""
    <div style='background:var(--mori-yellow);padding:12px;border-radius:10px;margin-bottom:20px'>
    💡 温馨提示：填写全部信息后点击保存，系统会自动跳转计算营养需求哦！
    </div>
    """, unsafe_allow_html=True)
    
    col1,col2 = st.columns(2)
    with col1:
        st.markdown("### 🧍 基础身材信息")
        gender = st.radio("性别",["👦 男","👧 女"])
        age = st.number_input("年龄",min_value=5,max_value=120,value=22)
        height = st.number_input("身高(cm)",min_value=80,max_value=250,value=170)
        weight = st.number_input("体重(kg)",min_value=20,max_value=300,value=60)
        active = st.selectbox("日常活动强度",[
            "久坐（学生/办公室）",
            "轻度活动（每日散步30分钟）",
            "中度活动（每日健身1小时）",
            "高强度运动（体力/力量训练）"
        ])
    with col2:
        st.markdown("### 🩺 健康与饮食偏好")
        disease = st.multiselect("体检健康异常/基础疾病",[
            "糖尿病","高血压","高尿酸/痛风","乳糖不耐","海鲜过敏","胃病"
        ])
        target = st.radio("你的健康目标",["减脂减重","增肌塑形","维持健康","控糖降压","养胃调理"])
        hate_food = st.text_input("忌口食材（逗号分隔，如牛肉,香菜）","")
        taste = st.radio("饮食口味偏好",["清淡少油","正常口味","重口重油"])
        scene = st.radio("日常用餐场景",["居家做饭","食堂简餐","外卖为主"])

    # 带音效按钮
    btn_save_info = st.button("✅ 保存用户信息并计算BMI", type="primary", use_container_width=True)
    if btn_save_info:
        st.markdown("<script>playClick()</script>", unsafe_allow_html=True)
        hate_list = hate_food.split(",") if hate_food else []
        bmi,bmi_level = calc_bmi(height,weight)
        st.session_state.user_info = {
            "gender":gender.replace("👦 ","").replace("👧 ",""),
            "age":age,"height":height,"weight":weight,
            "active":active,"disease":disease,"target":target,
            "hate":hate_list,"taste":taste,"scene":scene,
            "bmi":bmi,"bmi_level":bmi_level
        }
        st.success(f"🎉 信息保存成功！你的BMI：{bmi}，身体状态：{bmi_level}")
        st.session_state.target_page = "2. 📊 营养需求计算结果"
        st.rerun()

# ====================== 页面2：营养需求计算结果（莫兰迪蓝卡片） ======================
elif menu == "2. 📊 营养需求计算结果":
    if not user:
        st.warning("⚠️ 请先完成【用户健康信息录入】！")
    else:
        st.markdown("## 📈 健康计算结果看板")
        g = user["gender"]
        a = user["age"]
        h = user["height"]
        w = user["weight"]
        act = user["active"]
        tar = user["target"]

        bmr = calc_bmr(g,a,h,w)
        tdee = calc_tdee(bmr,act)
        target_cal = get_target_cal(tdee,tar)
        pro,cho,fat = calc_macro(target_cal,tar)

        col_top = st.columns(4)
        card_style = "padding:16px;border-radius:12px;text-align:center;background:var(--mori-blue);"
        with col_top[0]:
            st.markdown(f"<div style='{card_style}'><h2>{user['bmi']}</h2><p>BMI指数</p><span style='background:#BFD3C7;padding:3px 8px;border-radius:8px'>{user['bmi_level']}</span></div>", unsafe_allow_html=True)
        with col_top[1]:
            st.markdown(f"<div style='{card_style}'><h2>{round(bmr)} kcal</h2><p>基础代谢 BMR</p></div>", unsafe_allow_html=True)
        with col_top[2]:
            st.markdown(f"<div style='{card_style}'><h2>{round(tdee)} kcal</h2><p>每日消耗 TDEE</p></div>", unsafe_allow_html=True)
        with col_top[3]:
            st.markdown(f"<div style='{card_style}'><h2>{round(target_cal)} kcal</h2><p>目标摄入热量</p></div>", unsafe_allow_html=True)

        st.divider()
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            st.subheader("🥗 每日营养素需求")
            fig1, ax1 = plt.subplots()
            bar_name = ["碳水", "脂肪", "蛋白质"]
            bar_data = [cho, fat, pro]
            ax1.bar(bar_name, bar_data, color="#99B3A8", width=0.5)
            ax1.set_ylim(0, max(bar_data)+20)
            st.pyplot(fig1)
        with col_chart2:
            st.subheader("🍽️ 三餐热量分配")
            breakfast = filter_recipes(recipe_db["breakfast"],tar,user["disease"],user["hate"])[0]
            lunch = filter_recipes(recipe_db["lunch"],tar,user["disease"],user["hate"])[0]
            dinner = filter_recipes(recipe_db["dinner"],tar,user["disease"],user["hate"])[0]
            pie_data = [lunch["total_heat"], breakfast["total_heat"], dinner["total_heat"]]
            pie_label = ["午餐","早餐","晚餐"]
            fig2, ax2 = plt.subplots()
            ax2.bar(pie_label, pie_data, color="#D4B8A0", width=0.5)
            st.pyplot(fig2)

        btn_save_data = st.button("💾 保存本次营养数据，前往三餐推荐", type="primary", use_container_width=True)
        if btn_save_data:
            st.markdown("<script>playClick()</script>", unsafe_allow_html=True)
            save_history(user,target_cal,pro,cho,fat)
            st.success("✅ 营养数据已存入本地记录！正在跳转三餐推荐页面...")
            st.session_state.target_page = "3. 🍱 一日三餐智能食谱推荐"
            st.rerun()

# ====================== 页面3：一日三餐（新增跳转报告按钮 + 莫兰迪四色卡片） ======================
elif menu == "3. 🍱 一日三餐智能食谱推荐":
    if not user:
        st.warning("⚠️ 请先录入健康信息并计算营养需求！")
    else:
        st.markdown("## 🥘 为你定制一日三餐方案")
        tar = user["target"]
        dis = user["disease"]
        hate = user["hate"]
        bf = filter_recipes(recipe_db["breakfast"],tar,dis,hate)[0]
        lu = filter_recipes(recipe_db["lunch"],tar,dis,hate)[0]
        di = filter_recipes(recipe_db["dinner"],tar,dis,hate)[0]
        sn = filter_recipes(recipe_db["snack"],tar,dis,hate)[0]

        col_bf, col_lu, col_di, col_sn = st.columns(4)
        # 早餐 莫兰迪米黄
        with col_bf:
            st.markdown(f"""
            <div style="background:var(--mori-yellow); padding:16px; border-radius:14px;height:100%">
                <h3>🌞 早餐</h3>
                <h4>{bf["title"]}</h4>
                <p>食材：{"、".join(bf["foods"])}</p>
                <p>🔥热量 {bf["total_heat"]}kcal | 🥩蛋白 {bf["protein"]}g</p>
                <p>🍞碳水 {bf["carb"]}g | 🧈脂肪 {bf["fat"]}g</p>
            </div>
            """, unsafe_allow_html=True)
        # 午餐 莫兰迪浅绿
        with col_lu:
            st.markdown(f"""
            <div style="background:var(--mori-green); padding:16px; border-radius:14px;height:100%">
                <h3>🥗 午餐</h3>
                <h4>{lu["title"]}</h4>
                <p>食材：{"、".join(lu["foods"])}</p>
                <p>🔥热量 {lu["total_heat"]}kcal | 🥩蛋白 {lu["protein"]}g</p>
                <p>🍞碳水 {lu["carb"]}g | 🧈脂肪 {lu["fat"]}g</p>
            </div>
            """, unsafe_allow_html=True)
        # 晚餐 莫兰迪浅蓝
        with col_di:
            st.markdown(f"""
            <div style="background:var(--mori-blue); padding:16px; border-radius:14px;height:100%">
                <h3>🍲 晚餐</h3>
                <h4>{di["title"]}</h4>
                <p>食材：{"、".join(di["foods"])}</p>
                <p>🔥热量 {di["total_heat"]}kcal | 🥩蛋白 {di["protein"]}g</p>
                <p>🍞碳水 {di["carb"]}g | 🧈脂肪 {di["fat"]}g</p>
            </div>
            """, unsafe_allow_html=True)
        # 加餐 莫兰迪浅粉
        with col_sn:
            st.markdown(f"""
            <div style="background:var(--mori-pink); padding:16px; border-radius:14px;height:100%">
                <h3>🍎 加餐</h3>
                <h4>{sn["title"]}</h4>
                <p>食材：{"、".join(sn["foods"])}</p>
                <p>🔥热量 {sn["total_heat"]}kcal | 🥩蛋白 {sn["protein"]}g</p>
                <p>🍞碳水 {sn["carb"]}g | 🧈脂肪 {sn["fat"]}g</p>
            </div>
            """, unsafe_allow_html=True)

        st.divider()
        # ========== 新增：一键跳转完整健康报告按钮 ==========
        btn_go_report = st.button("📄 生成完整个人健康饮食报告", type="primary", use_container_width=True)
        if btn_go_report:
            st.markdown("<script>playClick()</script>", unsafe_allow_html=True)
            st.session_state.target_page = "5. 📄 个人健康饮食报告"
            st.rerun()

        st.markdown("## 📄 简易饮食预览")
        bmi_val = user["bmi"]
        bmi_state = user["bmi_level"]
        tar_cal = round(get_target_cal(calc_tdee(calc_bmr(user["gender"],user["age"],user["height"],user["weight"]), user["active"]), user["target"]))
        p, c, f = calc_macro(tar_cal, user["target"])
        st.markdown(f"""
        <div style='background:var(--mori-beige);padding:18px;border-radius:12px'>
        <ul style='font-size:16px;line-height:2;color:var(--mori-text)'>
        <li>当前BMI为{bmi_val}，状态为{bmi_state}。</li>
        <li>建议每日摄入约{tar_cal}kcal，其中蛋白质{p}g、碳水{c}g、脂肪{f}g。</li>
        <li>当前目标为{user['target']}，用餐场景为{user['scene']}，口味倾向为{user['taste']}。</li>
        <li>每日饮水建议1800-2200ml，运动量较大时适当增加。</li>
        <li>烹饪方式优先选择蒸、煮、炖、少油快炒，减少油炸和重油红烧。</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        for d in user["disease"]:
            st.markdown(f"<div style='background:var(--mori-yellow);padding:10px;border-radius:8px;margin-top:10px'>⚠️ {d}饮食限制：{disease_avoid_map.get(d,'无特殊限制')}</div>", unsafe_allow_html=True)

# ====================== 页面4：食材营养查询库（莫兰迪浅绿提示） ======================
elif menu == "4. 🥬 食材营养查询库":
    st.markdown("## 🥦 虚拟食材营养数据库查询")
    st.markdown("<div style='background:var(--mori-green);padding:10px;border-radius:10px'>🔍 输入食材名称快速查询营养、适配人群与禁忌</div>", unsafe_allow_html=True)
    food_df = pd.DataFrame(food_db)
    search_key = st.text_input("输入食材名称搜索","")
    if search_key:
        res_df = food_df[food_df["name"].str.contains(search_key)]
        st.dataframe(res_df,use_container_width=True)
    else:
        st.dataframe(food_df,use_container_width=True)

# ====================== 页面5：个人健康饮食报告（莫兰迪浅蓝头部） ======================
elif menu == "5. 📄 个人健康饮食报告":
    if not user:
        st.warning("⚠️ 请先录入健康信息并计算营养需求")
    else:
        st.markdown("## 📑 专属完整健康饮食总结报告")
        st.markdown("<div style='background:var(--mori-blue);padding:12px;border-radius:10px'>🍀 结合你的身体数据、疾病、减脂/增肌目标生成专属饮食指南</div>", unsafe_allow_html=True)
        st.subheader("一、🧍 身体基础概况")
        st.write(f"性别：{user['gender']} 年龄：{user['age']}岁 身高：{user['height']}cm 体重：{user['weight']}kg")
        st.write(f"BMI：{user['bmi']}，体型评估：{user['bmi_level']}")
        st.write(f"日常活动：{user['active']}")
        st.write(f"健康目标：{user['target']}")
        disease_text = "无" if len(user['disease']) == 0 else "、".join(user['disease'])
        st.write(f"基础疾病：{disease_text}")

        st.subheader("二、📌 核心饮食原则")
        if user["target"] == "减脂减重":
            st.success("1. 总热量制造缺口400大卡，高蛋白、低精制碳水、低脂\n2. 主食替换杂粮、红薯，杜绝甜品奶茶\n3. 晚餐主食减半，19点前完成用餐")
        elif user["target"] == "增肌塑形":
            st.success("1. 热量盈余300大卡，充足蛋白质+复合碳水\n2. 每日三餐均匀摄入肉蛋豆制品\n3. 运动前后补充碳水加餐")
        elif "糖尿病" in user["disease"]:
            st.error("1. 禁止粥、白米饭、糕点等高升糖食物\n2. 主食全部替换杂粮，少食多餐\n3. 杜绝一切含糖饮料、水果限量")
        elif "高血压" in user["disease"]:
            st.error("1. 严格控盐，不吃腌制品、加工肉\n2. 多芹菜、菠菜、豆腐等高钾食材\n3. 避免重油重辣外卖")
        elif user["target"] == "养胃调理":
            st.info("1. 不吃生冷、辛辣、坚硬食物\n2. 三餐定时定量，温热饮食为主\n3. 少食多餐，拒绝空腹刺激肠胃")

        st.subheader("三、🌱 长期健康改善建议")
        st.markdown("""
        <div style='background:var(--mori-yellow);padding:12px;border-radius:10px'>
        <ol style="color:var(--mori-text)">
        <li>烹饪方式：清蒸、水煮、清炒，减少油炸红烧</li>
        <li>饮水：每日2000ml白开水，不喝含糖饮品</li>
        <li>作息：23点前入睡，熬夜会降低代谢、升高食欲</li>
        <li>运动：配合目标增加活动量，减脂多有氧，增肌多力量训练</li>
        </ol>
        </div>
        """, unsafe_allow_html=True)

# ====================== 页面6：历史记录查询（莫兰迪浅粉提示） ======================
elif menu == "6. 📜 历史记录查询":
    st.markdown("## 🕒 历史营养计算记录存档")
    st.markdown("<div style='background:var(--mori-pink);padding:10px;border-radius:10px'>💾 所有保存过的身体数据、营养需求、食谱记录都存在这里</div>", unsafe_allow_html=True)
    with open(history_file,"r",encoding="utf-8") as f:
        history = json.load(f)
    if len(history) == 0:
        st.info("暂无历史记录，请先完成计算并保存数据")
    else:
        for idx,item in enumerate(history):
            with st.expander(f"记录{idx+1}｜{item['time']}"):
                u = item["user"]
                st.write(f"BMI：{u['bmi']} | 目标：{u['target']}")
                st.write(f"每日推荐热量：{item['daily_cal']} kcal")
                st.write(f"蛋白质：{item['protein']}g 碳水：{item['carb']}g 脂肪：{item['fat']}g")
                disease_text = "无" if len(u['disease']) == 0 else "、".join(u['disease'])
                st.write(f"基础疾病：{disease_text}")