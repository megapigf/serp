from flask import Flask, render_template, session, request, redirect
import time
import json as js

app = Flask(__name__)
app.secret_key = "asd123"

col_pop = 0
stud = {
    "stud": [
        {"name": "А4", "desk": "Иметь к конецу игры 18 популярности.",
            "+R": "18",
            "iff": {
                "col_pop": 18
            }},
        {"name": "Ивангай", "desk": "Иметь к конецу игры 12 популярности.",
            "+R": "12", "iff": {
                "col_pop": 12
            }},
        {"name": "FunnyFriends", "desk": "Иметь к концу игры 6 популярности.",
            "+R": "12", "iff": {
                "col_pop": 6
            }},
        {"name": "Masha BS", "desk": "Иметь к концу игры 1 популярность.",
            "+R": "18", "iff": {
                "col_pop": 1
            }},
        {"name": "Юный Майнер", "desk": "Иметь к концу игры 9 железа.",
            "+R": "9", "iff": {
                "col_dze": 9
            }},
        {"name": "Опытный Майнер", "desk": "Иметь к концу игры 14 железа.",
            "+R": "19", "iff": {
                "col_dze": 14
            }},
        {"name": "Майнер технологичка", "desk": "Иметь к концу игры 19 железа.",
            "+R": "32", "iff": {
                "col_dze": 19
            }},
        {"name": "Запуск ядерного реактора, 1 стадия", "desk": "Иметь к концу игры 19 нефти.",
            "+R": "16", "iff": {
                "col_nef": 19
            }},
        {"name": "Улучшение ядерного реактора, 2 стадия", "desk": "Иметь к концу игры 19 нефти и 19 железа.",
            "+R": "32", "iff": {
                "col_nef": 19,
                "col_dze": 19
            }},
        {"name": "Запуск реактора, 3 стадия", "desk": "Иметь к концу игры 19 нефти, 19 железа и 16 силы.",
            "+R": "64", "iff": {
                "col_nef": 19,
                "col_dze": 19,
                "col_sil": 16
            }}
    ]
}


def iff(user_params, index):
    vp = 0
    for param in stud["stud"][index]["iff"]:
        if stud["stud"][index]["iff"][param] == user_params[param]:
            vp += 1
    if vp == len(stud["stud"][index]["iff"]):
        return 1
    return 0

def loot(l, item, class_, type_):
    for i in l[class_]:
        if i[type_] == item:
            return l[class_].index(i)
    return -1


@app.route("/")
def home():
    if "game" in session:
        return redirect(f"/games/{session['game']}")
    return render_template("home.html")


@app.route("/reg", methods=["GET", "POST"])
def reg():
    if "game" in session:
        return redirect(f"/games/{session['game']}")
    if "user" in session:
        return redirect("/")
    elif request.method == "POST":
        with open("database/ack.json", "r") as ack_js:
            ack = js.load(ack_js)
        username = request.form.get('user')
        password = request.form.get('password')
        if loot(ack, username, "acks", "name") == -1:
            ack["acks"].append({
                "name": username,
                "password": password,
                "R": "0",
                "friends": [],
                "followers": [],
                "sub": [],
                "stud_id": []
            })
            with open("database/ack.json", "w") as t:
                ack = js.dump(ack, t)
            session["user"] = username
            return redirect("/games")
        else:
            return redirect("/reg")
    else:
        return render_template("reg.html")


@app.route("/games", methods=["GET", "POST"])
def games():
    if "game" in session:
        return redirect(f"/games/{session['game']}")
    if "user" in session:
        with open("database/games.json", "r") as games_js:
            games = js.load(games_js)
        if request.method == "POST":
            session["game"] = session["user"]
            games["games"].insert(0, {"creater": session["user"], "time": 0,
                                  "type": "start", "finish": 0, "players": [session["user"]], "win": []})
            with open("database/games.json", "w") as games_js:
                game = js.dump(games, games_js)
            with open("database/games.json", "r") as games_js:
                games = js.load(games_js)
        return render_template("games.html", user=session["user"], **games)
    else:
        return redirect("/reg")


@app.route("/ack/<link>")
def ack(link):
    if "user" not in session:
        return redirect("/")
    if "game" in session:
        return redirect(f"/games/{session['game']}")
    with open("database/ack.json", "r") as ack_js:
        ack = js.load(ack_js)
    index = loot(ack, link, "acks", "name")
    if index == -1:
        return redirect("/")
    else:
        return render_template("ack.html", user=session["user"], link=link, ack=ack, index=index, stud=stud)


@app.route("/login", methods=["GET", "POST"])
def login():
    if "game" in session:
        return redirect(f"/games/{session['game']}")
    if "user" in session:
        return redirect("/")
    elif request.method == "POST":
        with open("database/ack.json", "r") as ack_js:
            ack = js.load(ack_js)
        username = request.form.get('user')
        password = request.form.get('password')
        if ack["acks"][loot(ack, username, "acks", "name")]["password"] == password:
            session["user"] = username
            return redirect("/")
        else:
            return redirect("/login")
    else:
        return render_template("log.html")


@app.route("/games/<link>", methods=["GET", "POST"])
def game_link(link):
    with open("database/games.json", "r") as games_js:
        games = js.load(games_js)
    index = loot(games, link, "games", "creater")
    if "user" not in session:
        return redirect("/reg")
    if games["games"][index]["type"] == "finish" or games["games"][index]["type"] == "ladno":
        return redirect(f"/games/{link}/player")
    elif session["user"] == link:
        return redirect(f"/games/{link}/admin")
    elif "game" in session:
        if session["game"] == link:
            return redirect(f"/games/{link}/player")
    elif request.method == "POST":
        games["games"][index]["players"].append(session["user"])
        session["game"] = link
        with open("database/games.json", "w") as t:
            games = js.dump(games, t)
        return redirect(f"/games/{link}/player")
    elif "game" not in session:
        return render_template("gameslink.html", link=link, player=games["games"][index]["players"], creater=games["games"][index]["creater"], win=games["games"][index]["win"], type_=games["games"][index]["type"])


@app.route("/games/<link>/player", methods=["GET", "POST"])
def gameforplayer(link):
    with open("database/games.json", "r") as games_js:
        games = js.load(games_js)
    with open("database/ack.json", "r") as ack_js:
        ack = js.load(ack_js)
    index = loot(games, link, "games", "creater")
    list_stud_ok = []
    list_stud_no = []
    players = games["games"][index]["players"]
    type_ = games["games"][index]["type"]
    win = games["games"][index]["win"]
    time_ = time.time() - games["games"][index]["time"]
    if request.method == "POST":
        if games["games"][index]["type"] == "ladno":
            col_mon = request.form.get("col_mon")
            col_zve = request.form.get("col_zve")
            col_con = request.form.get("col_con")
            col_edi = request.form.get("col_edi")
            col_der = request.form.get("col_der")
            col_dze = request.form.get("col_dze")
            col_nef = request.form.get("col_nef")
            col_sil = request.form.get("col_sil")
            col_pop = request.form.get("col_pop")
            bonus = request.form.get("bonus")
            user_params = {"col_pop": int(col_pop), "col_mon": int(col_mon), "col_zve": int(col_zve), "col_con": int(col_con), "col_edi": int(
                col_edi), "col_der": int(col_der), "col_dze": int(col_dze), "col_nef": int(col_nef), "col_sil": int(col_sil), "bonus": int(bonus)}
            mn = 0
            if 6 <= int(col_pop) < 12:
                mn = 2
            elif 12 <= int(col_pop) < 16:
                mn = 3
            elif 6 < int(col_pop):
                mn = 1
            sum_cols = int(col_der) + int(col_nef) + \
                int(col_edi) + int(col_dze)
            col_mon = int(col_zve)*(mn+2) + (sum_cols//2)*mn + \
                int(col_con)*(mn+1) + int(col_mon) + int(bonus)
            rR = col_mon // 10
            games["games"][index]["finish"] = games["games"][index]["finish"] + 1
            games["games"][index]["win"].append(
                {"player": session["user"], "col_mon": col_mon})
            if games["games"][index]["finish"] == len(games["games"][index]["players"]):
                games["games"][index]["type"] = "finish"
                with open("database/games.json", "w") as t:
                    games = js.dump(games, t)
                with open("database/games.json", "r") as games_js:
                    games = js.load(games_js)
                ack["acks"][loot(ack, session["user"], "acks", "name")]["R"] = int(
                    ack["acks"][loot(ack, session["user"], "acks", "name")]["R"]) + rR
                for i in range(len(stud["stud"])):
                    if iff(user_params, i) == 1 and i not in ack["acks"][loot(ack, session["user"], "acks", "name")]["stud_id"]:
                        ack["acks"][loot(ack, session["user"],
                                         "acks", "name")]["stud_id"].append(i)
                        ack["acks"][loot(ack, session["user"], "acks", "name")]["R"] = int(
                            ack["acks"][loot(ack, session["user"], "acks", "name")]["R"]) + int(stud["stud"][i]["+R"])
                        list_stud_ok.append(
                            {"name": stud["stud"][i]["name"], "desk": stud["stud"][i]["desk"], "+R": stud["stud"][i]["+R"]})
                    elif i not in ack["acks"][loot(ack, session["user"], "acks", "name")]["stud_id"]:
                        list_stud_no.append(
                            {"name": stud["stud"][i]["name"], "desk": stud["stud"][i]["desk"], "+R": stud["stud"][i]["+R"]})
                session.pop("game")
                players = games["games"][index]["players"]
                type_ = games["games"][index]["type"]
                win = games["games"][index]["win"]
                games["games"].pop(index)
            with open("database/ack.json", "w") as t:
                ack = js.dump(ack, t)
        with open("database/games.json", "w") as t:
            games = js.dump(games, t)
    with open("database/games.json", "r") as games_js:
        games = js.load(games_js)
    with open("database/ack.json", "r") as ack_js:
        ack = js.load(ack_js)
    return render_template("gamelink_player.html", player=players, type_=type_, time=f"{int(time_//3600)}:{int((time_%3600)//60)}:{int(time_%60)}", win=win, link=link, list_stud_no=list_stud_no, list_stud_ok=list_stud_ok)


@app.route("/games/<link>/admin", methods=["POST", "GET"])
def gameforadmin(link):
    if session["user"] != link:
        return redirect(f"/games/{link}")
    with open("database/games.json", "r") as games_js:
        games = js.load(games_js)
    index = loot(games, link, "games", "creater")
    if games["games"][index]["type"] == "play":
        time_ = time.time() - games["games"][index]["time"]
        session["ltime"] = time_
    elif games["games"][index]["type"] == "ladno" or games["games"][index]["type"] == "finish":
        time_ = session["ltime"]
    else:
        time_ = 0
    return render_template("gamelink_admin.html", player=games["games"][index]["players"], type_=games["games"][index]["type"], hour=int(time_//3600), min=int((time_%3600)//60), sec=int((time_%60)//1), link=link)


@app.route("/friends")
def friends():
    if "user" not in session:
        return redirect("/")
    if "game" in session:
        return redirect(f"/games/{session['game']}")
    with open("database/ack.json", "r") as ack_js:
        ack = js.load(ack_js)
    index = loot(ack, session["user"], "acks", "name")
    return render_template("friends.html", ack=ack, index=index, user=session["user"])


@app.route("/chat/<link>", methods=["GET", "POST"])
def chat(link):
    if "user" not in session:
        return redirect("/")
    if "game" in session:
        return redirect(f"/games/{session['game']}")
    with open("database/chats.json", "r") as chat_js:
        chat = js.load(chat_js)
    for i in chat["chats"]:
        if (i["from-to"] == link and i["to-from"] == session["user"]) or (i["from-to"] == session["user"] and i["to-from"] == link):
            index = i
            break
    if request.method == "POST":
        text = request.form.get("text")
        if text.count(" ") != len(text):
            index["msg"].insert(0, {"from": session["user"], "text": text})
            with open("database/chats.json", "w") as t:
                chat = js.dump(chat, t)
    return render_template("chat.html", msg=index["msg"], from_to=index["from-to"], to_from=index["to-from"], link=link)


@app.route("/friends/new_friend/<link>")
def new_friends(link):
    if "user" not in session:
        return redirect("/reg")
    if "game" in session:
        return redirect(f"/games/{session['game']}")
    with open("database/ack.json", "r") as ack_js:
        ack = js.load(ack_js)
    with open("database/chats.json", "r") as chat_js:
        chat = js.load(chat_js)
    index = loot(ack, link, "acks", "name")
    if session["user"] not in ack["acks"][index]["friends"] and session["user"] not in ack["acks"][index]["followers"]:
        ack["acks"][index]["followers"].append(session["user"])
        ack["acks"][loot(ack, session["user"], "acks", "name")
                    ]["sub"].append(link)
    if session["user"] in ack["acks"][index]["followers"] and link in ack["acks"][loot(ack, session["user"], "acks", "name")]["followers"]:
        ack["acks"][index]["friends"].append(session["user"])
        ack["acks"][loot(ack, session["user"], "acks", "name")
                    ]["friends"].append(link)
        chat["chats"].append(
            {"to-from": link, "from-to": session["user"], "msg": []})
    with open("database/ack.json", "w") as t:
        ack = js.dump(ack, t)
    with open("database/chats.json", "w") as t:
        chat = js.dump(chat, t)
    return redirect("/friends")

@app.route("/del_ack")
def del_ack():
    if "user" not in session:
        return redirect("/reg")
    if "game" in session:
        return redirect(f"/games/{session['game']}")
    with open("database/ack.json", "r") as ack_js:
        ack = js.load(ack_js)
    index = loot(ack, session["user"], "acks", "name")
    ack["acks"].pop(index)
    session.pop("user")
    if "game" in session:
        session.pop("game")
    with open("database/ack.json", "w") as t:
        ack = js.dump(ack, t)
    return redirect("/")


@app.route("/clear_session")
def clear_session():
    if "user" in session:
        session.pop("user")
    if "game" in session:
        session.pop("game")
    return redirect("/")


@app.route("/startgame", methods=["POST", "GET"])
def startgame():
    with open("database/games.json", "r") as games_js:
        games = js.load(games_js)
    index = loot(games, session["user"], "games", "creater")
    if games["games"][index]["type"] == "start":
        games["games"][index]["type"] = "play"
        games["games"][index]["time"] = time.time()
        with open("database/games.json", "w") as t:
            games = js.dump(games, t)
    return redirect(f"/games/{session['user']}/admin")

@app.route("/stopgame", methods=["POST", "GET"])
def stopgame():
    with open("database/games.json", "r") as games_js:
        games = js.load(games_js)
    index = loot(games, session["user"], "games", "creater")
    games["games"][index]["type"] = "ladno"
    with open("database/games.json", "w") as t:
        games = js.dump(games, t)
    return redirect(f"/games/{session['user']}/admin")

@app.route("/all_stud")
def all_stud():
    return render_template("stud.html", stud=stud)

if __name__ == "__main__":
    app.run(port=4545, debug=True)