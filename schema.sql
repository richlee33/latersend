drop table if exists emails;
create table emails (
  id integer primary key autoincrement,
  sender text not null,
  recipient text not null,
  subject text not null,
  message text not null,
  entry_date text not null,
  send_date text not null,
  sent integer not null
);
