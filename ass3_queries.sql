select count(*) from books;

select * from members;
delete from members where userid = 1;

select * from members;

alter table members
MODIFY userid int not null auto_increment;


alter table members
add constraint UQ_email UNIQUE(email);

insert into members (fname, lname, address, city, state, zip, phone, email, password)
VALUES ('Philip', 'Velandria', 'Stallvägen', 'Växjö', 'Kronoberg', '35256', '07638727', 'philipvelandria@gmail.com', '12345'); 

show columns from members;

select * from cart;
DELETE from cart WHERE userid = 3;
