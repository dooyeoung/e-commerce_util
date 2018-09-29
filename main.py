from flask import Flask, render_template, request, jsonify, json, url_for
import pickle
import MySQLdb
import os
from os.path import basename
import ast

app = Flask(__name__)
app.config.update(
    TEMPLATES_AUTO_RELOAD = True,
)

def init():
    # db 접속
    db = MySQLdb.connect(
        "127.0.0.1",
        "root",
        "fbendud89",
        "soulfood",
        charset='utf8',
    ) 
    return db
db = init();


@app.route("/")
def index():
    return render_template("index.html")
 

@app.route('/<string:page_name>/')
def static_page(page_name): 
    return render_template('%s.html' % page_name)


@app.route("/search_item/", methods=["POST"])
def search_item():

    datas = select_item_by_name(request.values['txt'])
    res = json.loads(json.dumps(datas))
 

    if request.method == 'POST':
        result = {"status":200, "result":res}
    else:
        result = {"status":201}
 
    return jsonify(result) 


@app.route("/combine/", methods=["POST"])
def combine():
    datas = select_combi() 
    res = json.loads(json.dumps(datas))

    if request.method == 'POST':
        result = {"status":200, "result":res}
    else:
        result = {"status":201}
 
    return jsonify(result) 


@app.route("/get_combine/", methods=["POST"])
def get_combine():
    combi_id = request.values['combi_id']

    datas = select_combi_by_id(combi_id)

    print(datas);
    sd = ast.literal_eval(datas[0][4])
    print(sd);

    karr = []
    for k,v in sd.items():
        karr.append(k)

    ids = karr[len(karr)-1].split(',') 

    if len(ids) == 1: 
        ids = karr
    
    files = []
    for item_id in ids:
        static_file_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static')

        dirname = static_file_dir + "/upload"
        find_file_name = ''
        filenames = os.listdir(dirname)
        for filename in filenames:
            full_filename = os.path.join(dirname, filename)
            fname = basename(full_filename)

            if fname == ".DS_Store":
                continue

            idtxt = fname.split(".")[0] 
            if item_id == idtxt:
                find_file_name = fname 
                files.append(fname) 


    #karr = sd.keys()[].split(',')
    # res = json.loads(json.dumps(datas))

    if request.method == 'POST':
        result = {"status":200, "result":sd, "ids":files, "type":datas[0][1]}
    else:
        result = {"status":201}
 
    return jsonify(result) 



def select_combi_by_id(combi_id):


    SQL_QUERY = "SELECT * from `combine` where id = {}".format(combi_id)
    
    try:
        curs = db.cursor()
        count = curs.execute(SQL_QUERY)
        rows = curs.fetchall()
    except Exception as e:
        print(e) 
        print(combi_id)
    
    return rows


@app.route('/add_combi/', methods=['POST'])
def add_combi(): 
    data = request.values['combi']
    title = request.values['title']
    td = request.values['type']
    price = request.values['price']

    add_combine(title, data, td, price)
 
    # #sd = ast.literal_eval("{'1': '2', '11': '2'}")
      
    # for key in mydic.keys():
    #     amt = mydic[key]

    if request.method == 'POST':
        result = {"status":200, "result":True}
    else:
        result = {"status":201}
 
    return jsonify(result) 

def add_combine(title, data, td,price):    
    #SQL_QUERY = "INSERT INTO `combine` VALUES (NULL, %s)"
    SQL_QUERY = "INSERT INTO `combine` VALUES (NULL, {},'{}',{},'{}')".format(td,title,price,data)
 
    result = True
    try:
        curs = db.cursor()
        count = curs.execute(SQL_QUERY)
        db.commit()
        print("success to add combine")
        #print(SQL_QUERY) 
    except Exception as e:
        print("fail to add combine")
        #print(SQL_QUERY)
        print(e)
        result = False 
    return result 




@app.route("/view_img/", methods=["POST"])
def view_img():  
    item_id = request.values['item_id']  
    datas = select_item_by_id(item_id)

    static_file_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static')

    dirname = static_file_dir + "/upload"
    find_file_name = ''
    filenames = os.listdir(dirname)
    for filename in filenames:
        full_filename = os.path.join(dirname, filename)
        fname = basename(full_filename)

        if fname == ".DS_Store":
            continue

        idtxt = fname.split(".")[0] 
        if item_id == idtxt:
            find_file_name = fname 

    
    colordata = select_color_id(item_id) 

    res = json.loads(json.dumps(datas))
    if request.method == 'POST':
        result = {"status":200, "result":res, "img_file":find_file_name, "color":colordata}
    else:
        result = {"status":201}
 
    return jsonify(result) 


@app.route("/upload_tmp_img/", methods=["POST"])
def upload_tmp_img():
    svg = request.values['svgData']  
    
    result = False
    try: 
        static_file_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static')
        f = open(static_file_dir+'/tmp.svg', 'w')
        f.write(svg)
        f.close() 
        result  = True
    except Exception as e:
        print(e)
        result = False;

    if request.method == 'POST':
        result = {"status":200, "result":result}
    else:
        result = {"status":201}

    return jsonify(result)
 
@app.route("/set_back_wt/", methods=["POST"])
def set_back_wt():
    w = request.values['width']
    t = request.values['top']
    item_id = request.values['item_id']

    update_wt(item_id, w, t) 

    if request.method == 'POST':
        result = {"status":200, "result":True}
    else:
        result = {"status":201}

    return jsonify(result)

@app.route("/set_back_color/", methods=["POST"])
def set_back_color():

    color = request.values['color']
    typedata = request.values['type']
    item_id = request.values['item_id']
    update_color(item_id, color, typedata)
 
    if request.method == 'POST':
        result = {"status":200, "result":True}
    else:
        result = {"status":201}

    return jsonify(result)

@app.route("/file_upload/", methods=["POST"])
def file_upload():
    result = False
    try: 
        last_id = request.values['last_id']
        f = request.files['file']

        static_file_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static')

        ext = os.path.splitext(f.filename)[1]
        f.save(static_file_dir + "/upload/" +last_id + ext)
 
        result = True
    except Exception as e:
        print(e)
        result = False

    if request.method == 'POST':
        result = {"status":200, "result":result}
    else:
        result = {"status":201}

    return jsonify(result)



@app.route("/view_item/", methods=["POST"])
def view_item():  
    item_id = request.values['item_id'] 
    datas = select_item_all_by_id(item_id)
    
    res = json.loads(json.dumps(datas))
    if request.method == 'POST':
        result = {"status":200, "result":res}
    else:
        result = {"status":201}
 
    return jsonify(result)


@app.route("/list/", methods=["POST"])
def list():
    
    items = select_item()

    res = json.loads(json.dumps(items))

    if request.method == 'POST':
        result = {"status":200, "result":res}
    else:
        result = {"status":201}
 
    return jsonify(result)


@app.route("/delete/", methods=["POST"])
def delete():

    delete_id = request.values['id']

    delete_by_id_item('item', delete_id)
    delete_by_id_item('nutrition_basic', delete_id) 
    delete_by_id_item('nutrition_etc', delete_id)
    delete_by_id_item('message', delete_id)
    delete_by_id_item('material', delete_id)


    if request.method == 'POST':
        result = {"status":200, "result":True}
    else:
        result = {"status":201}
 
    return jsonify(result)


@app.route("/add/", methods=["POST"])
def add():
    item = request.values.to_dict()
 

    res1 = False
    res2 = False
    res3 = False
    res4 = False

    last_id = add_item(item['name'], item['price'], item['weight'], item['company'],
        item['type'], item['wrap'], item['expired'],
        item['item_id'],item['callcenter'],item['maker'],
        item['seller']) 

    if last_id != -1:
        res1 = add_nutrition_basic(last_id, item['kcal'],item['carbohydrate'],item['sugar'],
            item['protein'],item['fat'],item['fat_s'],item['fat_t'],
            item['cholesterol'], item['salt'],item['amount_one'],item['amount_total'],item['amount_unit'])

        if res1 == False:
            #remove item
            delete_by_id_item('item', last_id)
        else:
            res2 = add_nutrition_etc(last_id,item['fiber'],item['folate'],item['niacin'],
                item['iron'],item['calcium'],item['vitamin_a'],item['vitamin_b1'],
                item['vitamin_b2'],item['vitamin_b6'],item['vitamin_c'],
                item['vitamin_d'],item['vitamin_e'])

            if res2 == False:
                #remove item, basic
                delete_by_id_item('item', last_id)
                delete_by_id_item('nutrition_basic', last_id) 
            else:
                res3 = add_message(last_id,item["msg1"],item["msg2"],item["msg3"]
                    ,item["msg4"],item["msg5"],item["msg6"],item["msg7"],item['msg5_txt'])

                if res3 == False:
                    #remove item, basic, etc
                    delete_by_id_item('item', last_id)
                    delete_by_id_item('nutrition_basic', last_id) 
                    delete_by_id_item('nutrition_etc', last_id) 
                else :
                    res4 = add_material(last_id, item["material"],item["material_s"])

                    add_color(last_id);
                    if res4 == False:
                        # remove all
                        delete_by_id_item('item', last_id)
                        delete_by_id_item('nutrition_basic', last_id) 
                        delete_by_id_item('nutrition_etc', last_id)
                        delete_by_id_item('message', last_id)


    adding_result = False
    if res1 & res2 & res3 & res4:
        adding_result = True
    else:
        print("remove")

    if request.method == 'POST':
        result = {"status":200, "result":adding_result, 'last_id':last_id}
    else:
        result = {"status":201}
 
    return jsonify(result)



def delete_by_id_item(tablename, id):

    field = "id_item"
    if tablename == "item":
        field = "id"

    SQL_QUERY = """
    DELETE FROM `{}` WHERE `{}` IN ('{}');
    """.format(tablename,field,id)
    
    try:
        curs = db.cursor()
        count = curs.execute(SQL_QUERY)
        db.commit()
        print("success to delete ", tablename)
        print(SQL_QUERY);

        if get_count(tablename) == 0:
            truncate(tablename)

    except Exception as e:
        print("fail to add message")
        print(SQL_QUERY)
        print(e)

def truncate(tablename):
    SQL_QUERY = "truncate `"+tablename+"`";

    curs = db.cursor()
    count = curs.execute(SQL_QUERY) 



def select_item_by_name(txt):
    SQL_QUERY =  "select * from `item` where `name` like '%{}%'".format(txt)

    print(SQL_QUERY)
    curs = db.cursor()
    count = curs.execute(SQL_QUERY) 
    rows = curs.fetchall()
    
    return rows


def select_combi():
    SQL_QUERY = "select * from `combine`";
    
    curs = db.cursor()
    count = curs.execute(SQL_QUERY) 
    rows = curs.fetchall()  
    return rows


def get_count(tablename):
    SQL_QUERY = "select * from `"+tablename+"`";
    
    curs = db.cursor()
    count = curs.execute(SQL_QUERY) 
    rows = curs.fetchall()  
    return len(rows)


def select_item():
    SQL_QUERY = "select * from `item`";
    
    curs = db.cursor()
    count = curs.execute(SQL_QUERY) 
    rows = curs.fetchall()
    
    return rows

def select_item_by_id(item_id):
    q1 = "select * from `item` where id = "+item_id

    curs = db.cursor()
    curs.execute(q1) 
    rows1 = curs.fetchall()

    return rows1

def select_item_all_by_id(item_id):
    q1 = "select * from `item` where id = "+item_id
    q2 = "select * from `nutrition_basic` where id_item =  "+item_id
    q3 = "select * from `nutrition_etc` where id_item = "+item_id
    q4 = "select * from `material` where id_item = "+item_id
    q5 = "select * from `message` where id_item = "+item_id


    curs = db.cursor()
    curs.execute(q1) 
    rows1 = curs.fetchall()

    curs.execute(q2) 
    rows2 = curs.fetchall()

    curs.execute(q3) 
    rows3 = curs.fetchall()

    curs.execute(q4) 
    rows4 = curs.fetchall()

    curs.execute(q5) 
    rows5 = curs.fetchall()

    return (rows1, rows2, rows3, rows4, rows5)

def select_color_id(item_id):
    q1 = "select * from `background` where `id_item` = "+item_id

    curs = db.cursor()
    curs.execute(q1) 
    rows1 = curs.fetchall()

    return rows1


def add_color(id_item):

    SQL_QUERY = "INSERT INTO `background` VALUES (NULL, %s, %s, %s, %s, %s)"

    result = True
    try:
        curs = db.cursor()
        count = curs.execute(SQL_QUERY, (id_item, "#FFFFFF", "#FFFFFF", 350, 330))
        db.commit()
        print("success to add add_color")
        #print(SQL_QUERY) 
    except Exception as e:
        print("fail to add add_color")
        #print(SQL_QUERY)
        print(e)
        result = False 
    return result

def update_wt(id_item, width, top):
    SQL_QUERY = "UPDATE `background` SET `width` = %s, `top` = %s WHERE `id_item` = %s"

    result = True
    try:
        curs = db.cursor()
        count = curs.execute(SQL_QUERY, (width, top, id_item))
        db.commit()
        print("success to update_wt")
        #print(SQL_QUERY) 
    except Exception as e:
        print("fail to update_wt")
        #print(SQL_QUERY)
        print(e)
        result = False 
    return result


def update_color(id_item, color, typedata):

    SQL_QUERY = ""
    if typedata == '0':
        SQL_QUERY = "UPDATE `background` SET `color0` = %s WHERE `id_item` = %s"
    else:
        SQL_QUERY = "UPDATE `background` SET `color1` = %s WHERE `id_item` = %s"

    result = True
 
    try:
        curs = db.cursor()
        count = curs.execute(SQL_QUERY, (color, int(id_item)))
        db.commit()
        print("success to update_color")
        #print(SQL_QUERY) 
    except Exception as e:
        print("fail to update_color")
        #print(SQL_QUERY)
        print(e)
        result = False 
    return result



def add_message(id_item,msg1,msg2,msg3,msg4,msg5,msg6,msg7,msg5_txt):

    SQL_QUERY = """
    INSERT INTO `message`
    VALUES (NULL,{},{},{},{},{},{},{},{},'{}')
    """.format(id_item,msg1,msg2,msg3,msg4,msg5,msg6,msg7,msg5_txt)


    result = True
    try:
        curs = db.cursor()
        count = curs.execute(SQL_QUERY)
        db.commit() 
        #print(SQL_QUERY)  
        print("success to add message")
    except Exception as e:
        print("fail to add message")
        #print(SQL_QUERY)  
        print(e)
        result = False 
    return result    

def add_material(id_item,material, material_s):

    if len(material) == 0:
        material = None

    SQL_QUERY = "INSERT INTO `material` VALUES (NULL, %s, %s, %s)"

    result = True
    try:
        curs = db.cursor()
        count = curs.execute(SQL_QUERY, (id_item, material, material_s))
        db.commit()
        print("success to add material")
        #print(SQL_QUERY) 
    except Exception as e:
        print("fail to add material")
        #print(SQL_QUERY)
        print(e)
        result = False 
    return result



def add_item(name, price, weight, company,
    type, wrap, expired, item_id, callcenter, maker, seller):
     
    item_id = None if not item_id else int(item_id)
    SQL_QUERY = """
    INSERT INTO `item` (`id`, `name`, `price`, `weight`, `company`,`type`,`wrap`,`expired`,`item_id`,`callcenter`,`maker`,`seller`) 
    VALUES (NULL, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """ 

    inputdata = (name, price, weight, company,
        type, wrap, expired, item_id, callcenter, maker, seller)
    last_id = -1
    try:
        curs = db.cursor()
        count = curs.execute(SQL_QUERY, inputdata)
        db.commit()
        print("success to add item")
        #print(curs._last_executed)
        last_id = curs.lastrowid
    except Exception as e:
        print("fail to add item")
        #print(SQL_QUERY)
        print(e)
        last_id = -1

    return last_id


def add_nutrition_basic(id_item,kcal,carbohydrate,sugar,
    protein,fat,fat_s,fat_t,cholesterol,salt,
    amount_one,amount_total,amount_unit):
    SQL_QUERY = """
    INSERT INTO `nutrition_basic` VAlUES(NULL,{},{},{},{},{},{},{},{},{},{},{},{},'{}')
    """.format(id_item,kcal,carbohydrate,sugar,protein,fat,fat_s,fat_t,cholesterol,
        salt,amount_one,amount_total,amount_unit)

    result = True
    try:
        curs = db.cursor()
        count = curs.execute(SQL_QUERY)
        db.commit()
        print("success to add nutrition")
        #print(SQL_QUERY) 
    except Exception as e:
        print("fail to add nutrition")
        #print(SQL_QUERY)
        print(e)
        result = False 
    return result


def add_nutrition_etc(id_item,fiber,folate,niacin,iron,calcium,
    vitamin_a,vitamin_b1,vitamin_b2,vitamin_b6,vitamin_c,vitamin_d,vitamin_e):
 
    fiber = None if not fiber else float(fiber)
    folate = None if not folate else float(folate)
    niacin = None if not niacin else float(niacin) 
    iron = None if not iron else float(iron)
    calcium = None if not calcium else float(calcium)
    vitamin_a = None if not vitamin_a else float(vitamin_a)
    vitamin_b1 = None if not vitamin_b1 else float(vitamin_b1)
    vitamin_b2 = None if not vitamin_b2 else float(vitamin_b2)
    vitamin_b6 = None if not vitamin_b6 else float(vitamin_b6)
    vitamin_c = None if not vitamin_c else float(vitamin_c)
    vitamin_d = None if not vitamin_d else float(vitamin_d)
    vitamin_e = None if not vitamin_e else float(vitamin_e)

    SQL_QUERY = "INSERT INTO `nutrition_etc` VALUES (NULL,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    inputdata = (id_item,fiber,folate,niacin,iron,calcium,vitamin_a,vitamin_b1,vitamin_b2,vitamin_b6,vitamin_c,vitamin_d,vitamin_e)

    result = True
    try:
        curs = db.cursor()
        count = curs.execute(SQL_QUERY, inputdata)
        db.commit()
        print("success to add nutrition_etc")
        #print(curs._last_executed) 
    except Exception as e:
        print("fail to add nutrition_etc") 
        print(e)
        result = False 
    return result


if __name__ == "__main__":
    app.run(debug=True)