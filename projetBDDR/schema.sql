CREATE TABLE "Employee" (
  "id" serial PRIMARY KEY,
  "lastname" varchar NOT NULL,
  "firstname" varchar NOT NULL,
  "category" varchar
);

CREATE TABLE "Adresseemail" (
  "addresse" VARCHAR PRIMARY KEY,
  "estInterne" BOOLEAN,
  "employee_id" integer
);

CREATE TABLE "Email" (
  "email_id" serial PRIMARY KEY,
  "sender" integer,
  "subject" varchar,
  "date_send" datetime,
  "content" text
);

CREATE TABLE "ReceiversMail" (
  "email_id" serial,
  "addresse" varchar,
  "type" varchar,
  PRIMARY KEY ("email_id", "addresse")
);

ALTER TABLE "Adresseemail" ADD FOREIGN KEY ("employee_id") REFERENCES "Employee" ("id");

ALTER TABLE "Adresseemail" ADD FOREIGN KEY ("addresse") REFERENCES "ReceiversMail" ("addresse");

ALTER TABLE "Adresseemail" ADD FOREIGN KEY ("addresse") REFERENCES "Email" ("sender");

ALTER TABLE "Email" ADD FOREIGN KEY ("email_id") REFERENCES "ReceiversMail" ("email_id");
