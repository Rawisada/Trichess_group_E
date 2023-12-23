import random
import websockets
import asyncio
import json
import random
 
async def ws_client():

    url = "ws://192.168.11.20:8181/game"
    # Connect to the server
    async with websockets.connect(url) as ws:
        #รับข้อมูล server เมื่อ connect ผ่าน
        response = await ws.recv()
        received_data = json.loads(response)
        print(f"Received: {json.dumps(received_data,indent=2)}\n")

        player = received_data['Player']
        password = received_data['Password']

        Mypiece = []
        EnemyPieces = []
        
        #รอบแรก เพื่อรับค่า start 
        while True: 
            try:
                #รับข้อมูล server เมื่อเริ่ม start
                response = await ws.recv()
                json_response = json.loads(response)
                print('parse json response')
                print(f'Server: {json.dumps(json_response, indent=2)}\n')

                #รับข้อความเมื่อถึง MyTurn
                response_Myturn  = await ws.recv()
                json_response_Myturn  = response_Myturn.replace("True", 'true')
                json_response_Myturn = json.loads(json_response_Myturn)
                print(f'Board: {json.dumps(json_response_Myturn, indent=2)}\n')

                #check turn
                if(json_response_Myturn["YourTurn"] == True):
                    print("---------------------------------------Myturn--------------------------------------------")
                    #เก็บหมากศัตรูทั้ง 2 player
                    for piece in json_response_Myturn['Board']:
                        if piece['Owner'] != player:
                            EnemyPieces.append({'Field': piece['Field'], 'Piece': piece['Piece'], 'Movable': 0 })
                    
                    # ส่งข้อมูลให้ server ส่ง Mypiece มา
                    data_to_send = {"Command": "MyPiece", "Password": password}
                    await ws.send(json.dumps(data_to_send, indent=2))
                    print(f"Sent: {json.dumps(data_to_send)}\n")
                
                    response_MyPiece = await ws.recv()
                    json_response_MyPiece = json.loads(response_MyPiece)
                    print(f'Received of Mypiece: {json.dumps(json_response_MyPiece,indent=2)}\n')

                    #เก็บหมากของตัวเองใน Mypiece
                    for piece in json_response_MyPiece['Board']:
                        Mypiece.append({'Field': piece['Field'], 'Piece': piece['Piece'], 'Movable': 0 })
                    
                    # MoveAble ของหมากแต่ละตัวใน EnemyPieces
                    for piece in  EnemyPieces:
                        data_to_send = {"Command": "Movable", "Password": password, "Field": piece['Field']}
                        await ws.send(json.dumps(data_to_send, indent=2))
                        print(f"Sent : {json.dumps(data_to_send)}\n")

                        response_MoveAble = await ws.recv()
                        json_response_MoveAble = json.loads(response_MoveAble)
                        print(f'Received of Moveale: {json.dumps(json_response_MoveAble,indent=2)}\n')

                        if(json_response_MoveAble["Status"] == "Success"):
                            if'MovableFields' in json_response_MoveAble['Message']:
                                piece['Movable'] = json_response_MoveAble['MovableFields']
                    
                    print("---------------------------------------Step1--------------------------------------------")
                    Movable = []
                    # MoveAble ของหมากแต่ละตัวใน Mypiece
                    for piece in Mypiece:
                        data_to_send = {"Command": "Movable", "Password": password, "Field": piece['Field']}
                        await ws.send(json.dumps(data_to_send, indent=2))
                        print(f"Sent: {json.dumps(data_to_send)}\n")

                        response_MoveAble = await ws.recv()
                        json_response_MoveAble = json.loads(response_MoveAble)

                        # MoveAble ที่สามารถเดินได้ทั้งหมดใน 1 piece
                        if(json_response_MoveAble["Status"] == "Success"):
                            if'MovableFields' in json_response_MoveAble['Message']:
                                print(f'Received of Moveable: {json.dumps(json_response_MoveAble,indent=2)}\n')
                                for piece1 in json_response_MoveAble['MovableFields']:
                                    Status = 0
                                    for piece2 in  EnemyPieces:
                                        #ถ้ากินได้จะได้คะแนน
                                        if piece1['Field'] ==  piece2['Field'] :
                                            if piece2["Piece"] == "Pawn":
                                                Movable.append({"Field": piece1['Field'], "Score" : 10})
                                            elif piece2["Piece"] == "Knight" or piece2["Piece"] == "Bishop":
                                                Movable.append({"Field": piece1['Field'], "Score" : 30})
                                            elif  piece2["Piece"] == "Rook":
                                                Movable.append({"Field": piece1['Field'], "Score" : 50})
                                            elif  piece2["Piece"] == "Queen":
                                                Movable.append({"Field": piece1['Field'], "Score" : 90})
                                            elif  piece2["Piece"] == "King":
                                                Movable.append({"Field": piece1['Field'], "Score" : 900})
                                            Status = 1
                                    #ถ้ากินไม่ได้จะได้ 0 
                                    if Status == 0:
                                        Movable.append({"Field": piece1['Field'], "Score" : 0})
                                
                                piece['Movable'] = Movable
                                Movable = []

                    print("MyPiece :",Mypiece)
                    print("---------------------------------------Step2--------------------------------------------")
            
                    
                    # หมากที่เดินได้ทั้งหมด
                    Mypiece_Movable = []
                    for piece in Mypiece:
                        if piece['Movable'] != 0:
                            Mypiece_Movable.append(piece)
                    
                    # หาค่า Min ที่หมากเราจะโดนกินในแต่ละทางเลือก       
                    for piece1 in Mypiece_Movable:
                        Movable = []
                        for piece2 in piece1['Movable']:
                            for piece5 in Mypiece_Movable:
                                if piece1 != piece5:
                                    Status = 0
                                    for piece3 in EnemyPieces:
                                        #หมากแต่ละตัวของศัตรูทั้งหมดสามารถเดินไปที่ไหนได้บ้าง
                                        if piece3['Movable'] != 0:
                                            for piece4 in piece3['Movable']:
                                                if piece4['Field'] ==  piece5['Field'] :
                                                    if piece5["Piece"] == "Pawn":
                                                        score = piece2["Score"] - 10 
                                                        Movable.append(score)
                                                    elif piece5["Piece"] == "Knight" or piece5["Piece"] == "Bishop":
                                                        score = piece2["Score"] - 30 
                                                        Movable.append(score)
                                                    elif  piece5["Piece"] == "Rook":
                                                        score = piece2["Score"] - 50 
                                                        Movable.append(score)
                                                    elif  piece5["Piece"] == "Queen":
                                                        score = piece2["Score"] - 90 
                                                        Movable.append(score)
                                                    elif  piece5["Piece"] == "King":
                                                        score = piece2["Score"] - 900 
                                                        Movable.append(score)
                                                    Status = 1
                                                if Status == 1:
                                                    break
                                            if Status == 1:
                                                break
                                    if Status == 0:
                                        Movable.append(piece2["Score"])

                                elif piece1 == piece5:
                                    #หมากศัตรูทั้งหมด
                                    Status = 0
                                    for piece3 in EnemyPieces:
                                        #หมากแต่ละตัวของศัตรูทั้งหมดสามารถเดินไปที่ไหนได้บ้าง
                                        if piece3['Movable'] != 0:
                                            for piece4 in piece3['Movable']:
                                            #ถ้าเปรียบเเล้ว Movable หมากตที่ขยับว่าโดนกินไหม 
                                                if piece2['Field'] ==  piece4['Field'] :
                                                    if piece1["Piece"] == "Pawn":
                                                        score = piece2["Score"] - 10 
                                                        Movable.append(score)
                                                    elif piece1["Piece"] == "Knight" or piece1["Piece"] == "Bishop":
                                                        score = piece2["Score"] - 30 
                                                        Movable.append(score)
                                                    elif  piece1["Piece"] == "Rook":
                                                        score = piece2["Score"] - 50 
                                                        Movable.append(score)
                                                    elif  piece1["Piece"] == "Queen":
                                                        score = piece2["Score"] - 90 
                                                        Movable.append(score)
                                                    elif  piece1["Piece"] == "King":
                                                        score = piece2["Score"] - 900 
                                                        Movable.append(score)
                                                    Status = 1
                                                if Status == 1:
                                                    break
                                            if Status == 1:
                                                break
                                    if Status == 0:
                                        Movable.append(piece2["Score"])
                        print(Movable)
                        min_value = min(Movable)
                        piece2['Score'] = min_value
                    
                    print("MyPiece :", Mypiece)

                    status = 0
                    pieceFrom = 0
                    pieceTo = 0
                    pieceScore = 0
                    
                    #หาค่า Max ที่เราจะเดินได้มากที่สุด
                    for piece1 in  Mypiece_Movable:
                        for piece2 in piece1['Movable']:
                            if status == 0:
                                pieceFrom = piece1["Field"]
                                pieceTo = piece2['Field']
                                pieceScore = piece2["Score"]
                                status = 1
                                

                            else:
                                if pieceScore <= piece2["Score"]:
                                    pieceFrom = piece1["Field"]
                                    pieceTo = piece2['Field']
                                    pieceScore = piece2["Score"]
                               
                
                    
                    data_to_send = {"Command": "Move", "Password": password ,"Move": {"From": pieceFrom ,"To": pieceTo}}
                    await ws.send(json.dumps(data_to_send, indent=2))
                    print(f"Sent: {json.dumps(data_to_send)}\n")

                    response_data = await ws.recv()
                    print(f'Received of Move : {json.dumps(response_data, indent=2)}\n')


                    #if promote
                    if("RequirePromotion" in response_data):
                        data_to_send = {"Command": "Promote", "Password": password ,"Promotion":"Queen"}
                        await ws.send(json.dumps(data_to_send, indent=2))
                        print(f"Sent: {json.dumps(data_to_send)}\n")

                        response_data = await ws.recv()
                        print(f'Received of Move : {json.dumps(response_data, indent=2)}\n')

                        response_data = await ws.recv()
                        print(f'Received of Move : {json.dumps(response_data, indent=2)}\n')

                    Mypiece = []
                    EnemyPieces = []
                    break
                

            except json.JSONDecodeError:
                print('Received non-JSON response')
        
        
        
        while True:
            
            response_Myturn  = await ws.recv()
            json_response_Myturn  = response_Myturn.replace("True", 'true')
            json_response_Myturn = json.loads(json_response_Myturn)
            print(f'Board: {json.dumps(json_response_Myturn, indent=2)}\n')

            Mypiece = []
            EnemyPieces = []
            #check turn
            if(json_response_Myturn["YourTurn"] == True):
                try:
                    print("---------------------------------------Myturn--------------------------------------------")
                    for piece in json_response_Myturn['Board']:
                        if piece['Owner'] != player:
                            EnemyPieces.append({'Field': piece['Field'], 'Piece': piece['Piece'], 'Movable': 0 })
                    
                    #Mypiece
                    data_to_send = {"Command": "MyPiece", "Password": password}
                    await ws.send(json.dumps(data_to_send, indent=2))
                    print(f"Sent: {json.dumps(data_to_send)}\n")
                
                    response_MyPiece = await ws.recv()
                    json_response_MyPiece = json.loads(response_MyPiece)
                    print(f'Received of Mypiece: {json.dumps(json_response_MyPiece,indent=2)}\n')

                    king = ""
                    #เก็บหมากของตัวเองใน Mypiece
                    for piece in json_response_MyPiece['Board']:
                        Mypiece.append({'Field': piece['Field'], 'Piece': piece['Piece'], 'Movable': 0 })
                        if(piece['Piece'] == "King"):
                            king = piece['Field']
                    
                    #MoveAble ของหมากแต่ละตัวใน EnemyPieces
                    for piece in  EnemyPieces:
                        data_to_send = {"Command": "Movable", "Password": password, "Field": piece['Field']}
                        await ws.send(json.dumps(data_to_send, indent=2))
                        print(f"Sent : {json.dumps(data_to_send)}\n")

                        response_MoveAble = await ws.recv()
                        json_response_MoveAble = json.loads(response_MoveAble)
                        print(f'Received of Moveale: {json.dumps(json_response_MoveAble,indent=2)}\n')

                        if(json_response_MoveAble["Status"] == "Success"):
                            if'MovableFields' in json_response_MoveAble['Message']:
                                piece['Movable'] = json_response_MoveAble['MovableFields']
                    
                    
                    #ส่งคำสั่งไป checkKing
                    data_to_send = {"Command": "CheckKing", "Password": password}
                    await ws.send(json.dumps(data_to_send, indent=2))
                    print(f"Sent: {json.dumps(data_to_send)}\n")

                    
                    response_CheckKing = await ws.recv()
                    response_CheckKing  = response_CheckKing.replace("True",'true')
                    response_CheckKing  = response_CheckKing.replace("False","false")
                    json_response_response_CheckKing = json.loads(response_CheckKing)
                    print(f'Received of Mypiece: {json.dumps(json_response_response_CheckKing,indent=2)}\n')

                    #ถ้าเกิดการ checkking
                    statusking = 0
                    if(json_response_response_CheckKing["KingInCheck"] == True):
                        for piece in json_response_response_CheckKing["KingMovableField"]:
                            for piece2 in EnemyPieces:
                                if piece['Field'] == piece2['Field']:
                                    data_to_send = {"Command": "Move", "Password": password ,"Move": {"From": king ,"To": piece['Field']}}
                                    await ws.send(json.dumps(data_to_send, indent=2))
                                    print(f"Sent: {json.dumps(data_to_send)}\n")

                                    response_data = await ws.recv()
                                    #print("1", Moveable[ramdom_pieceMoveable][2], "2", Mypiece[ramdom_piece]['Piece'])
                                    print(f'Received of Move : {json.dumps(response_data, indent=2)}\n')
                                    statusking = 1
                                    break
                        if(statusking == 0):
                            kinglist = []
                            kinglist = json_response_response_CheckKing["KingMovableField"]
                            ramdom_pieceMoveableking = random.randint(0, len(kinglist) - 1)
                            data_to_send = {"Command": "Move", "Password": password ,"Move": {"From": king ,"To": kinglist[ramdom_pieceMoveableking]['Field']}}
                            await ws.send(json.dumps(data_to_send, indent=2))
                            print(f"Sent: {json.dumps(data_to_send)}\n")

                            response_data = await ws.recv()
                           
                            print(f'Received of Move : {json.dumps(response_data, indent=2)}\n')
                          

                                

                    else:
                        print("--------------------------------------- false chack king--------------------------------------------")
                    
                        print("---------------------------------------Step1--------------------------------------------")
                        Movable = []
                        # MoveAble ของหมากแต่ละตัวใน Mypiece
                        for piece in Mypiece:
                            data_to_send = {"Command": "Movable", "Password": password, "Field": piece['Field']}
                            await ws.send(json.dumps(data_to_send, indent=2))
                            print(f"Sent: {json.dumps(data_to_send)}\n")

                            response_MoveAble = await ws.recv()
                            json_response_MoveAble = json.loads(response_MoveAble)
                            print(f'Received of Moveable: {json.dumps(json_response_MoveAble,indent=2)}\n')

                            # MoveAble ที่สามารถเดินได้
                            if(json_response_MoveAble["Status"] == "Success"):
                                if'MovableFields' in json_response_MoveAble['Message']:
                                    print(f'Received of Moveable: {json.dumps(json_response_MoveAble,indent=2)}\n')
                                    for piece1 in json_response_MoveAble['MovableFields']:
                                        Status = 0
                                        for piece2 in  EnemyPieces:
                                            #ถ้ากินได้
                                            if piece1['Field'] ==  piece2['Field'] :
                                                if piece2["Piece"] == "Pawn":
                                                    Movable.append({"Field": piece1['Field'], "Score" : 10})
                                                elif piece2["Piece"] == "Knight" or piece2["Piece"] == "Bishop":
                                                    Movable.append({"Field": piece1['Field'], "Score" : 30})
                                                elif  piece2["Piece"] == "Rook":
                                                    Movable.append({"Field": piece1['Field'], "Score" : 50})
                                                elif  piece2["Piece"] == "Queen":
                                                    Movable.append({"Field": piece1['Field'], "Score" : 90})
                                                elif  piece2["Piece"] == "King":
                                                    Movable.append({"Field": piece1['Field'], "Score" : 900})
                                                Status = 1
                                        if Status == 0:
                                            Movable.append({"Field": piece1['Field'], "Score" : 0})
                                
                                    piece['Movable'] = Movable
                                    Movable = []

                        print("MyPiece :",Mypiece)
                        print("---------------------------------------Step2--------------------------------------------")
                
                        #เก็บหมากที่เดินได้ทั้งหมด
                        Mypiece_Movable = []
                        for piece in Mypiece:
                            if piece['Movable'] != 0:
                                Mypiece_Movable.append(piece)
                        
                        
                         # หาค่า Min ที่หมากเราจะโดนกินในแต่ละทางเลือก       
                        for piece1 in Mypiece_Movable:
                            Movable = []
                            for piece2 in piece1['Movable']:
                                for piece5 in Mypiece_Movable:
                                    if piece1 != piece5:
                                        Status = 0
                                        for piece3 in EnemyPieces:
                                            #หมากแต่ละตัวของศัตรูทั้งหมดสามารถเดินไปที่ไหนได้บ้าง
                                            if piece3['Movable'] != 0:
                                                for piece4 in piece3['Movable']:
                                                    if piece4['Field'] ==  piece5['Field'] :
                                                        if piece5["Piece"] == "Pawn":
                                                            score = piece2["Score"] - 10 
                                                            Movable.append(score)
                                                        elif piece5["Piece"] == "Knight" or piece5["Piece"] == "Bishop":
                                                            score = piece2["Score"] - 30 
                                                            Movable.append(score)
                                                        elif  piece5["Piece"] == "Rook":
                                                            score = piece2["Score"] - 50 
                                                            Movable.append(score)
                                                        elif  piece5["Piece"] == "Queen":
                                                            score = piece2["Score"] - 90 
                                                            Movable.append(score)
                                                        elif  piece5["Piece"] == "King":
                                                            score = piece2["Score"] - 900 
                                                            Movable.append(score)
                                                        Status = 1
                                                    if Status == 1:
                                                        break
                                                if Status == 1:
                                                    break
                                        if Status == 0:
                                            Movable.append(piece2["Score"])

                                    elif piece1 == piece5:
                                        #หมากศัตรูทั้งหมด
                                        Status = 0
                                        for piece3 in EnemyPieces:
                                            #หมากแต่ละตัวของศัตรูทั้งหมดสามารถเดินไปที่ไหนได้บ้าง
                                            if piece3['Movable'] != 0:
                                                for piece4 in piece3['Movable']:
                                            #ถ้าเปรียบเเล้ว Movable หมากตที่ขยับว่าโดนกินไหม 
                                                    if piece2['Field'] ==  piece4['Field'] :
                                                        if  piece1["Piece"] == "Pawn":
                                                            score = piece2["Score"] - 10 
                                                            Movable.append(score)
                                                        elif piece1["Piece"] == "Knight" or piece1["Piece"] == "Bishop":
                                                            score = piece2["Score"] - 30 
                                                            Movable.append(score)
                                                        elif  piece1["Piece"] == "Rook":
                                                            score = piece2["Score"] - 50 
                                                            Movable.append(score)
                                                        elif  piece1["Piece"] == "Queen":
                                                            score = piece2["Score"] - 90 
                                                            Movable.append(score)
                                                        elif  piece1["Piece"] == "King":
                                                            score = piece2["Score"] - 900 
                                                            Movable.append(score)
                                                        Status = 1
                                                    if Status == 1:
                                                        break
                                                if Status == 1:
                                                    break
                                        if Status == 0:
                                            Movable.append(piece2["Score"])
                            print(Movable)
                            min_value = min(Movable)
                            piece2['Score'] = min_value
                        
                        print("MyPiece :",Mypiece)

                        status = 0
                        pieceFrom = 0
                        pieceTo = 0
                        pieceScore = 0
                        
                        #หาค่า Max ที่เราจะเดินได้มากที่สุด
                        for piece1 in  Mypiece_Movable:
                            for piece2 in   piece1['Movable']:
                                if status == 0:
                                    pieceFrom = piece1["Field"]
                                    pieceTo = piece2['Field']
                                    pieceScore = piece2["Score"]
                                    status = 1
                                else:
                                    if pieceScore <= piece2["Score"]:
                                        pieceFrom = piece1["Field"]
                                        pieceTo = piece2['Field']
                                        pieceScore = piece2["Score"]
                                    
                        print("Mypiece_Movable", Mypiece_Movable)
                        
                        data_to_send = {"Command": "Move", "Password": password ,"Move": {"From": pieceFrom ,"To": pieceTo}}
                        await ws.send(json.dumps(data_to_send, indent=2))
                        print(f"Sent: {json.dumps(data_to_send)}\n")

                        response_data = await ws.recv()
                        print(f'Received of Move : {json.dumps(response_data, indent=2)}\n')

                        #if promote
                        if("RequirePromotion" in response_data):
                            print("Promote!!!!!!")
                            data_to_send = {"Command": "Promote", "Password": password ,"Promotion":"Queen"}
                            await ws.send(json.dumps(data_to_send, indent=2))
                            print(f"Sent: {json.dumps(data_to_send)}\n")

                            response_data = await ws.recv()
                            print(f'Received of Move : {json.dumps(response_data, indent=2)}\n')

                            response_data = await ws.recv()
                            print(f'Received of Move : {json.dumps(response_data, indent=2)}\n')

                        Mypiece = []
                        EnemyPieces = []
                

                except json.JSONDecodeError:
                    print('Received non-JSON response')
        

            
 
# Start the connection
asyncio.get_event_loop().run_until_complete(ws_client())


