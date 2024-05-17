CREATE TABLE "Employee" (
  "id" serial,
  "lastname" varchar NOT NULL,
  "firstname" varchar NOT NULL,
  "category" varchar,
  "primary" key(lastname,firstname)
);

CREATE TABLE "AdresseEmail" (
  "addresse" email PRIMARY KEY,
  "estInterne" bool,
  "employee_id" integer,
  "primary" key(employee,addresse)
);

CREATE TABLE "Email" (
  "id" serial PRIMARY KEY,
  "sender" email,
  "subject" tinytext,
  "dateSend" datetime,
  "content" text
);

CREATE TABLE "ReceiversMail" (
  "email" serial,
  "addresse" email,
  "type" varchar,
  PRIMARY KEY ("email", "addresse")
);

CREATE TABLE "CoupleCommunication" (
  "employee_addresse_1" email,
  "employee_addresse_2" email,
  "total_mails_echanges" integer,
  "primary" key(employee_addresse_1,employee_addresse_2)
);

ALTER TABLE "AdresseEmail" ADD FOREIGN KEY ("employee_id") REFERENCES "Employee" ("id");

ALTER TABLE "AdresseEmail" ADD FOREIGN KEY ("addresse") REFERENCES "ReceiversMail" ("addresse");

ALTER TABLE "AdresseEmail" ADD FOREIGN KEY ("addresse") REFERENCES "Email" ("sender");

ALTER TABLE "Email" ADD FOREIGN KEY ("id") REFERENCES "ReceiversMail" ("email");

ALTER TABLE "AdresseEmail" ADD FOREIGN KEY ("addresse") REFERENCES "CoupleCommunication" ("employee_addresse_1");

ALTER TABLE "AdresseEmail" ADD FOREIGN KEY ("addresse") REFERENCES "CoupleCommunication" ("employee_addresse_2");
