

--------adding cycle---------
owner_id = request.session.get('owner_id')

cursor = connection.cursor()
sql = "SELECT COUNT(*) FROM CYCLE WHERE OWNER_ID = %s"
cursor.execute(sql, [owner_id])
result = cursor.fetchall()
cursor.close()
count_cycle = int(result[0][0])
count_cycle = count_cycle + 1
-- NEED TO PASS THE NUMBER OF CYCLE AN OWNER HAS AND THE OWNER_ID NUMBER TO THE PHOTO_PATH FUNCTION
-- photo_path = SOMETHING(count_cycle,owner_id)


cursor = connection.cursor()
sql = "INSERT INTO CYCLE(CYCLE_ID,MODEL,STATUS,PHOTO_PATH,OWNER_ID) VALUES(CYCLE_INCREMENT.NEXTVAL, %s, %s, %s, %s)"
cursor.execute(sql, [model, 0, photo_path, owner_id])
connection.commit()
cursor.close()

---------------------------------------------------------

----------------show my cycle--------------

owner_id = request.session.get('owner_id')

cursor = connection.cursor()
sql = "SELECT PHOTO,MODEL,RATING FROM CYCLE WHERE OWNER_ID = %s"
cursor.execute(sql,owner_id)
result = cursor.fetchall()
cursor.close()

for r in result:
	photo_path = r[0]
	model = r[1]
	rating = r[3]

----------------------------------------------------

--------------------searching for cycle in my location---------------------

location = request.POST.get('location')

cursor = connection.cursor()
sql = "SELECT DISTINCT CYCLE_ID FROM CYCLE C, OWNER O WHERE O.OWNER_ID=C.OWNER_ID AND UPPER(O.LOCATION) = %s"
cursor.execute(sql,location)
cycle_list = cursor.fetchall()
cursor.close()

for cyc in cycle_list:
	cycle_id = cyc[0]
	cursor = connection.cursor()
	sql = "SELECT PHOTO,MODEL,RATING FROM CYCLE WHERE CYCLE_ID = %s"
	cursor.execute(sql,cycle_id)
	cycle = cursor.fetchall()
	cursor.close()

----------------------OR-----------------------

location = request.POST.get('location')

cursor = connection.cursor()
sql = "SELECT OWNER_ID FROM OWNER WHERE UPPER(LOCATION) = %s"
cursor.execute(sql,location)
result = cursor.fetchall()
cursor.close()
cycle_list=[]
for r in result:
	own_id = r[0]
	cursor = connection.cursor()
	sql = "SELECT CYCLE_ID FROM CYCLE WHERE OWNER_ID = %s"
	cursor.execute(sql,own_id)
	cycle = cursor.fetchall()
	cursor.close()
	for cyc in cycle:
		cycle_list.append(cyc[0])

for cyc in cycle_list:
	cycle_id = cyc[0]
	cursor = connection.cursor()
	sql = "SELECT PHOTO,MODEL,RATING FROM CYCLE WHERE CYCLE_ID = %s"
	cursor.execute(sql,cycle_id)
	cycle = cursor.fetchall()
	cursor.close()

-----------------
---------------------------------------------TRIGGER FOR CYCLE_RATING_UPDATE----------------------------------------

CREATE OR REPLACE TRIGGER UPDATE_RATING_CYCLE
AFTER INSERT
ON CYCLE_REVIEW
FOR EACH ROW
DECLARE
	CYC_ID NUMBER;
	NEW_AVG_RATING NUMBER;
BEGIN
	CYC_ID := :NEW.CYCLE_ID;

	SELECT AVG(RATING) INTO NEW_AVG_RATING FROM CYCLE_REVIEW WHERE CYCLE_ID = CYC_ID;

	UPDATE CYCLE SET RATING = NEW_AVG_RATING WHERE CYCLE_ID = CYC_ID;
EXCEPTION
	WHEN NO_DATA_FOUND THEN
		DBMS_OUTPUT.PUT_LINE('NO DATA');
	WHEN OTHERS THEN
		DBMS_OUTPUT.PUT_LINE('DO NOT KNOW');
END;
/
-----------------------------------------------------TRIGGER FOR OWNER_RATING_UPDATE------------------------------------------------------

CREATE OR REPLACE TRIGGER UPDATE_RATING_OWNER
AFTER INSERT
ON PEER_REVIEW
FOR EACH ROW
DECLARE
	OWN_ID NUMBER;
	NEW_AVG_RATING NUMBER;
BEGIN
	OWN_ID := :NEW.OWNER_ID;

	SELECT AVG(RATING) INTO NEW_AVG_RATING FROM PEER_REVIEW WHERE OWNER_ID = OWN_ID;

	UPDATE OWNER SET RATING = NEW_AVG_RATING WHERE OWNER_ID = OWN_ID;
EXCEPTION
	WHEN NO_DATA_FOUND THEN
		DBMS_OUTPUT.PUT_LINE('NO DATA');
	WHEN OTHERS THEN
		DBMS_OUTPUT.PUT_LINE('DO NOT KNOW');
END;
/

-----------------------------------------------------------------
-------------------------------SEQUENCE------------------------------------------

CREATE SEQUENCE OWNER_INCREMENT
INCREMENT BY 1
START WITH 10000
MAXVALUE 50000
NOCYCLE ;

--DROP SEQUENCE OWNER_INCREMENT

CREATE SEQUENCE CUSTOMER_INCREMENT
INCREMENT BY 1
START WITH 50000
MAXVALUE 90000
NOCYCLE ;

--DROP SEQUENCE CUSTOMER_INCREMENT

CREATE SEQUENCE CYCLE_INCREMENT
INCREMENT BY 1
START WITH 90000
MAXVALUE 130000
NOCYCLE ;

--DROP SEQUENCE CYCLE_INCREMENT

CREATE SEQUENCE TRIP_INCREMENT
INCREMENT BY 1
START WITH 10000
MAXVALUE 99999
NOCYCLE ;

--DROP SEQUENCE TRIP_INCREMENT

CREATE SEQUENCE CYCLE_REVIEW_INCREMENT
INCREMENT BY 1
START WITH 10000
MAXVALUE 99999
NOCYCLE ;

--DROP SEQUENCE CYCLE_REVIEW_INCREMENT

CREATE SEQUENCE PEER_REVIEW_INCREMENT
INCREMENT BY 1
START WITH 10000
MAXVALUE 99999
NOCYCLE ;

--DROP SEQUENCE PEER_REVIEW_INCREMENT

------------------------------------------------------------
-----------------------------test insert owner/customer procedure---------------------------------

CREATE OR REPLACE PROCEDURE INSERT_OWNER ( OWN_NAME IN VARCHAR2, OWN_PASS IN VARCHAR2, OWN_PHONE IN VARCHAR2, OWN_EMAIL IN VARCHAR2) IS
	ID NUMBER;
BEGIN
	INSERT INTO OWNER(OWNER_ID,OWNER_NAME,PASSWORD,OWNER_PHONE,EMAIL_ADDRESS)
	VALUES(OWNER_INCREMENT.NEXTVAL,OWN_NAME,OWN_PASS,OWN_PHONE,OWN_EMAIL);

	SELECT OWNER_ID INTO ID FROM OWNER WHERE EMAIL_ADDRESS=OWN_EMAIL;

	INSERT INTO OWNER_EMAIL_VERIFICATION(OWNER_ID,IS_VERIFIED,EMAIL_ADDRESS,TOKEN_VALUE,TOKEN_CREATED)
	VALUES(ID,1,OWN_EMAIL,'AABBCCDD',SYSDATE);

END;
/


CREATE OR REPLACE PROCEDURE INSERT_CUSTOMER ( CUS_NAME IN VARCHAR2, CUS_PASS IN VARCHAR2, CUS_PHONE IN VARCHAR2, CUS_EMAIL IN VARCHAR2) IS
	ID NUMBER;
BEGIN
	INSERT INTO CUSTOMER(CUSTOMER_ID,CUSTOMER_NAME,PASSWORD,CUSTOMER_PHONE,EMAIL_ADDRESS)
	VALUES(CUSTOMER_INCREMENT.NEXTVAL,CUS_NAME,CUS_PASS,CUS_PHONE,CUS_EMAIL);

	SELECT CUSTOMER_ID INTO ID FROM CUSTOMER WHERE EMAIL_ADDRESS=CUS_EMAIL;

	INSERT INTO CUSTOMER_EMAIL_VERIFICATION(CUSTOMER_ID,IS_VERIFIED,EMAIL_ADDRESS,TOKEN_VALUE,TOKEN_CREATED)
	VALUES(ID,1,CUS_EMAIL,'AABBCCDD',SYSDATE);

	INSERT INTO DOCUMENT(CUSTOMER_ID,TYPE_NAME,FILE_PATH)
	VALUES(ID,'National ID Card','files/customer/doc/101.PNG');

END;
/

--------------------------------------------------------
----------------------FINDING OWNER REVIEW---------------------------

SELECT P.CUSTOMER_ID, C.CUSTOMER_NAME, P.COMMENT_TEXT, P.RATING
FROM PEER_REVIEW P, CUSTOMER C
WHERE P.OWNER_ID = SOMETHING AND P.CUSTOMER_ID = C.CUSTOMER_ID